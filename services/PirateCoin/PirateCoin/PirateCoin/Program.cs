using System;
using System.Net;
using System.Net.Http;
using System.Threading;
using log4net;
using log4net.Config;
using PirateCoin.http;

namespace PirateCoin
{
	class Program
	{
		static void Main(string[] args)
		{
			XmlConfigurator.Configure();
			try
			{
				var contractsUpdater = new ContractsUpdater(abiFilepath, contractByteCodePath, Settings.GethRpcUrl, Settings.CoinbasePass, Settings.ContactCreationGas, Settings.ContractDeployPeriod);
				contractsUpdater.Start();

				var httpServer = new HttpServer(port);
				httpServer
					.AddHandler(HttpMethod.Get.ToString(), latestContractHttpPath, context => context.WriteStringAsync(contractsUpdater.MostRecentContract?.Address))
					.AddHandler(HttpMethod.Get.ToString(), coinbaseHttpPath, async context =>
					{
						var coinbaseAddress = contractsUpdater.CoinbaseAddress;
						if(coinbaseAddress == null)
						{
							context.Close((int)HttpStatusCode.NotFound);
							return;
						}
						await context.WriteStringAsync(contractsUpdater.CoinbaseAddress);
					})
					.AcceptLoopAsync(CancellationToken.None)
					.Wait();
			}
			catch(Exception e)
			{
				log.Fatal("Unexpected App Error", e);
			}
		}

		const string latestContractHttpPath = "/latestContract";
		const string coinbaseHttpPath = "/coinbase";

		const string abiFilepath = "contracts/contract.abi.json";
		const string contractByteCodePath = "contracts/contract.bytecode.hex";
		private const int port = 14473;

		private static readonly ILog log = LogManager.GetLogger(typeof(Program));
	}
}
