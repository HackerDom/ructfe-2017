using System;
using System.Security.Cryptography;
using System.Threading;
using System.Threading.Tasks;
using log4net;
using log4net.Config;
using TreasureMap.Crypto;
using TreasureMap.Db;
using TreasureMap.Handlers;
using TreasureMap.Http;
using TreasureMap.Utils;
using TreasureMap.Ws;

namespace TreasureMap
{
	internal static class Program
	{
		private static void Main()
		{
			XmlConfigurator.Configure();
			try
			{
				var settings = SimpleSettings.Create("settings");

				CryptoConfig.AddAlgorithm(typeof(RHHE), RHHE.Name);

				var sleepPeriod = int.Parse(settings.GetValue("sleep"));
				var ttl = int.Parse(settings.GetValue("ttl"));

				var server = PrepareServer(settings);
				var wsServer = PrepareWsServer(settings);

				SecretHolder.Init(settings.GetValue("secret"));
				CredentialsHolder.Init(settings.GetValue("credentials"), sleepPeriod);
				PointHolder.Init(settings.GetValue("points"), sleepPeriod, ttl, (point, msg) => wsServer.BroadcastAsync(point, msg, CancellationToken.None));

				Task
					.WhenAll(
						server.AcceptLoopAsync(CancellationToken.None),
						wsServer.AcceptLoopAsync(CancellationToken.None)
					)
					.Wait();
			}
			catch (Exception ex)
			{
				Console.Error.WriteLine(ex);
				Log.Fatal("Unexpected exception", ex);
				Environment.Exit(ex.HResult == 0 ? ex.HResult : -1);
			}
		}

		private static HttpServer PrepareServer(SimpleSettings settings)
		{
			var port = int.Parse(settings.GetValue("port"));

			var server = new HttpServer(port);

			server
				.AddHandler(LoginHandler.Instance)
				.AddHandler(AddPointHandler.Instance)
				.AddHandler(GetAllPublicsHandler.Instance)
				.AddHandler(GetPointsHandler.Instance)
				.AddHandler(ShortestPathHandler.Instance);

			return server;
		}

		private static WsServer PrepareWsServer(SimpleSettings settings)
		{
			var port = int.Parse(settings.GetValue("ws-port"));
			return new WsServer(port);
		}

		private static readonly ILog Log = LogManager.GetLogger(typeof(Program));
	}
}

