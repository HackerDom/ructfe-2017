#!/usr/bin/env python3

import checker
import aiohttp
import random
import asyncio
import string

import UserAgents

async def check_status(response):
	if response.status >= 500:
		checker.down(error='status code is {}. Content: {}\n'.format(response.status, await response.text()))
	if response.status != 200:
		checker.mumble(error='status code is {}. Content: {}\n'.format(response.status, await response.text()))

class WSHelper:
	def __init__(self, connection):
		self.connection = connection
		self.queue = asyncio.Queue()
		self.wanted = set()
	def start(self):
		asyncio.async(self.start_internal())
	async def start_internal(self):
		async with self.connection as ws:
			async for msg in ws:
				if msg.type == aiohttp.WSMsgType.TEXT:
					try:
						data = msg.json(loads = lambda s : checker.parse_json(s, ['url', 'owner']))
					except Exception as ex:
						checher.mumble(error='can\'t parse service responce', exception=ex)
					await self.queue.put((data['url'], data['owner']))
				elif msg.type == aiohttp.WSMsgType.CLOSED:
					break
				else:
					checker.mumble(error='get message with unexpected type {}\nmessage: {}'.format(msg.type, msg.data))
	def want(self, url, owner):
		self.wanted.add((url, owner))
	def want_many(self, wanted):
		self.wanted |= wanted
	async def finish(self):
		while len(self.wanted) > 0:
			top = await self.queue.get()
			if top in self.wanted:
				self.wanted.remove(top)
		self.connection.close()

class State:
	def __init__(self, hostname, port=None):
		self.hostname = hostname
		self.port = '' if port is None else ':' + str(port)
		self.session = aiohttp.ClientSession(headers={
			'Referer': self.get_url(''), 
			'User-Agent': UserAgents.get()
		})
	def __del__(self):
		self.session.close()
	def get_url(self, path='', proto='http'):
		return '{}://{}{}/{}'.format(proto, self.hostname, self.port, path.lstrip('/'))

	async def get(self, url):
		url = self.get_url(url)
		try:
			checker.log(url)
			async with self.session.get(url) as response:
				await check_status(response)
				return await response.text()
		except Exception as ex:
			checker.down(error=url, exception=ex)

	async def post(self, url, data={}, need_check_status=True):
		url = self.get_url(url)
		try:
			checker.log(url)
			async with self.session.post(url, json=data) as response:
				if need_check_status:
					await check_status(response)
					return await response.text()
				else:
					return response.status, await response.text()
		except Exception as ex:
			checker.down(error='{}\n{}'.format(url, data), exception=ex)

	async def register(self, username=None, password=None):
		can_retry = username is None
		request = {'user': checker.get_value_or_rand_string(username, 8), 'password': checker.get_value_or_rand_string(password, 16)}
		status, text = await self.post('/api/login', request, need_check_status = False)
		if status == 200:
			return request['user'], request['password']
		if status == 400 and can_retry:
			while status == 400:
				request['user'] = checker.get_rand_string(16)
				request['password'] = checker.get_rand_string(32)
				status, text = await self.post('/api/login', request, need_check_status = False)
			return request['user'], request['password']
		checker.mumble(error='error while login: status {}, response {}'.format(status, text))

	async def login(self, username, password):
		request = {'user': username, 'password': password}
		await self.post('/api/login', request)

	async def get_public_points(self):
		return checker.parse_json(await self.get('/api/publics'))

	async def get_points(self):
		return checker.parse_json(await self.get('/api/points'))

	def get_listener(self):
		url = self.get_url('publics', proto='ws')
		try:
			connection = self.session.ws_connect(url, origin=self.get_url(''))
		except Exception as ex:
			checker.down(exception=ex)
		helper = WSHelper(connection)
		helper.start()
		return helper

	async def put_point(self, x = None, y = None, message = None, is_public = None, user = None):
		point = {
			'x' : checker.get_value_or_rand_string(x, 13, checker.printable), 
			'y' : checker.get_value_or_rand_string(y, 13, checker.printable), 
			'message' : checker.get_value_or_rand_string(message, 50), 
			'public' : is_public if is_public is not None else random.choice([True, False])}
		point['id'] = await self.post('/api/add', point)
		point['user'] = user
		return point

	async def get_path(self, start, finish, inners):
		response = await self.post('/api/path', {
			'start': start,
			'finish': finish,
			'sub': inners
		})
		return checker.parse_json(response)