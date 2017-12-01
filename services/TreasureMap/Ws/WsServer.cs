using System;
using System.Collections.Concurrent;
using System.Collections.Generic;
using System.Linq;
using System.Net;
using System.Threading;
using System.Threading.Tasks;
using log4net;
using TreasureMap.Db;
using TreasureMap.Db.Models;
using TreasureMap.Handlers.Helpers;
using TreasureMap.Utils;
using vtortola.WebSockets;
using vtortola.WebSockets.Rfc6455;

namespace TreasureMap.Ws
{
	internal class WsServer
	{
		public WsServer(int port)
		{
			var timeout = TimeSpan.FromSeconds(3);
			var readWriteTimeout = TimeSpan.FromSeconds(1);
			var options = new WebSocketListenerOptions
			{
				UseNagleAlgorithm = false,
				PingMode = PingModes.BandwidthSaving,
				PingTimeout = timeout,
				NegotiationTimeout = timeout,
				
				WebSocketSendTimeout = readWriteTimeout,
				WebSocketReceiveTimeout = readWriteTimeout,
				SubProtocols = new[] {"text"}
			};

			endpoint = new IPEndPoint(IPAddress.Any, port);
			listener = new WebSocketListener(endpoint, options);
			listener.Standards.RegisterStandard(new WebSocketFactoryRfc6455(listener));
		}

		public async Task AcceptLoopAsync(CancellationToken token)
		{
			token.Register(() =>
			{
				listener.Dispose();
				Log.Error("WebSocketServer stopped");
			});

			listener.Start();
			Log.Info($"WebSocketServer started at '{endpoint}'");
			while(!token.IsCancellationRequested)
			{
				try
				{
					var ws = await listener.AcceptWebSocketAsync(token).ConfigureAwait(false);
					if(ws == null)
						continue;
#pragma warning disable CS4014 // Because this call is not awaited, execution of the current method continues before the call is completed
					Task.Run(() => TryRegister(ws, token), token);
#pragma warning restore CS4014 // Because this call is not awaited, execution of the current method continues before the call is completed
				} catch {}
			}
		}

		public Task BroadcastAsync(Point point, string msg, CancellationToken token)
		{
			if (msg == null)
				msg = point.ToJsonString();
			return
				Task.WhenAll(
					sockets
						.Where(pair =>
						{
							var ws = pair.Key;
							if(ws.IsConnected)
								return true;
							Remove(ws);
							return false;
						})
						.Select(pair => TrySendAsync(pair.Key, pair.Value, point, token, msg)));
		}

		private async Task TryRegister(WebSocket ws, CancellationToken token)
		{
//			await Task.Delay(250, token).ConfigureAwait(false); //NOTE: ws4py issue workaround =\
			try
			{
				Log.Info($"request for {ws.HttpRequest.RequestUri.AbsolutePath}");
				var connection = CreateConnection(ws);
				if (!connection.HasValue)
					throw new UnauthorizedAccessException();
				await ws.WriteStringAsync(HelloMessage, token).ConfigureAwait(false);
				var conn = connection.Value;
				sockets[ws] = conn;
				Log.Info($"request for {ws.HttpRequest.RequestUri.AbsolutePath} registered");
				conn.InitData.ForEach(point => TrySendAsync(ws, conn, point, token).Wait(token));
			}
			catch
			{
				ws.Dispose();
			}
		}

		private async Task TrySendAsync(WebSocket ws, Connection connection, Point point, CancellationToken token, string msg = null)
		{
			try
			{
				if (!connection.NeedSend(point))
					return;
				msg = msg ?? point.Convert().ToJsonString();
				using(await connection.Lock.AcquireAsync(token).ConfigureAwait(false))
					await ws.WriteStringAsync(msg, token).ConfigureAwait(false);
			}
			catch
			{
				Remove(ws);
			}
		}

		private void Remove(WebSocket ws)
		{
			if (!sockets.TryRemove(ws, out Connection state))
				return;
			state.Lock.Dispose();
			ws.Dispose();
		}

		private struct Connection
		{
			public Predicate<Point> NeedSend;
			public AsyncLockSource Lock;
			public IEnumerable<Point> InitData;
		}

		private static Connection? CreateConnection(WebSocket ws)
		{
			var login = ws.HttpRequest.GetLogin();
			if (login == null)
				return null;
			if (ws.HttpRequest.RequestUri.AbsolutePath == "/ws/pubic")
				return new Connection
				{
					NeedSend = point => point.IsPublic,
					Lock = new AsyncLockSource(),
					InitData = PointHolder.GetPublics()
				};
			if (ws.HttpRequest.RequestUri.AbsolutePath == "/ws/points")
				return new Connection
				{
					NeedSend = point => point.User == login,
					Lock = new AsyncLockSource(),
					InitData = PointHolder.GetPublics()
				};
			return null;
		}

		private const string HelloMessage = "hello";
		private readonly ConcurrentDictionary<WebSocket, Connection> sockets = new ConcurrentDictionary<WebSocket, Connection>();
		private readonly WebSocketListener listener;
		private readonly IPEndPoint endpoint;

		private static readonly ILog Log = LogManager.GetLogger(typeof(Program));
	}
}