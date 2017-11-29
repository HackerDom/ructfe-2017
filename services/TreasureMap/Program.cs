using System;
using System.Security.Cryptography;
using System.Threading;
using log4net;
using log4net.Config;
using TreasureMap.Crypto;
using TreasureMap.Db;
using TreasureMap.Handlers;
using TreasureMap.Http;
using TreasureMap.Utils;

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

				CryptoConfig.AddAlgorithm(typeof(HashImplememtation), HashImplememtation.Name);

				var sleepPeriod = int.Parse(settings.GetValue("sleep"));
				var ttl = int.Parse(settings.GetValue("ttl"));

				SecretHolder.Init(settings.GetValue("secret")); 
				CredentialsHolder.Init(settings.GetValue("credentials"), sleepPeriod);
				PointHolder.Init(settings.GetValue("points"), sleepPeriod, ttl);

				var port = int.Parse(settings.GetValue("port"));
				var server = new HttpServer(port);

				server
					.AddHandler(RegisterHandler.Instanse)
					.AddHandler(LoginHandler.Instance)
					.AddHandler(AddPointHandler.Instance)
					.AddHandler(GetAllPublicsHandler.Instance)
					.AddHandler(GetPointsHandler.Instance);

				server.AcceptLoopAsync(new CancellationToken()).Wait();
			}
			catch (Exception ex)
			{
				Console.Error.WriteLine(ex);
				Log.Fatal("Unexpected exception", ex);
				Environment.Exit(ex.HResult == 0 ? ex.HResult : -1);
			}
		}

		private static readonly ILog Log = LogManager.GetLogger(typeof(Program));
	}
}

