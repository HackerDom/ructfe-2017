#!/usr/bin/env python3

import sys
from checker import Checker
import checker
from networking import State
import random
import json
import time
import asyncio

PORT = 7483

def check_points_list(l, expected=[]):
	if not type(l) is list:
		checker.mumble(error='list of points not a list, {}'.format(type(l)))
	error = []
	for i in range(len(l)):
		if not type(l[i]) is dict:
			checker.mumble(error='point #{} is not a dict, {}'.format(i, type(l[i])))
		for field in expected:
			if field not in l[i]:
				error.append(field)
		if len(error) > 0:
			checker.mumble(error='not all expected fields have founded in point #{}. {}'.format(i, str(errors)))

def get_point(points, id):
	for p in points:
		if p['id'] == id:
			return p

def compare(p1, p2, fields):
	error = []
	for f in fields:
		if p1[f] != p2[f]:
			error.append(f)
	if len(error) > 0:
		checker.mumble(error='points are different in fields {}: {} vs {}'.format(error, p1, p2))
		
FIELDS = ['id', 'x', 'y', 'message', 'public', 'user']

async def check_one(username, sender, viewer, is_public):
	point = await sender.put_point(is_public = True)
	point['user'] = username
	if is_public:
		points = await viewer.get_public_points()
	else:
		points = await viewer.get_points()
	check_points_list(points, FIELDS)
	p = get_point(points, point['id'])
	if p is None:
		checker.mumble(error='can\'t find point with id "{}" in {} points'.format(point['id'], 'public' if is_public else 'private'))
	compare(point, p, FIELDS)

async def handler_check(hostname):

	for i in range(2):
		viewer = State(hostname, PORT)
		state = State(hostname, PORT)
		await viewer.register()
		username, password = await state.register()
		tasks = []

		tasks.append(asyncio.ensure_future(check_one(username, state, viewer, True)))
		tasks.append(asyncio.ensure_future(check_one(username, state, state, False)))
		await asyncio.gather(*tasks)

	checker.ok()

async def handler_get_1(hostname, id, flag):
	id = json.loads(id)
	state = State(hostname, PORT)
	await state.login(id['username'], id['password'])
	points = await state.get_points()
	check_points_list(points, FIELDS)
	p = get_point(points, id['id'])
	if p is None:
		checker.mumble(error='can\'t find point with id "{}"'.format(id['id']))
	if p['message'] != flag:
		checker.corrupt(message="Bad flag: expected {}, found {}".format(flag, p['message']))
	checker.ok()

async def handler_put_1(hostname, id, flag):
	state = State(hostname, PORT)
	username, password = await state.register()
	point = await state.put_point(message=flag, is_public=False)
	await state.put_point(is_public=True)
	checker.ok(message=json.dumps({'username': username, 'password': password, 'id': point['id']}))

def main():
	checker = Checker(handler_check, [(handler_put_1, handler_get_1)])
	checker.process(sys.argv)

if __name__ == "__main__":
	main()
