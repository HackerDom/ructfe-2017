using System;
using System.Collections.Generic;
using System.IO;
using System.Linq;
using System.Net;
using System.Net.Http;
using System.Text;
using System.Threading;
using System.Threading.Tasks;
using log4net;
using log4net.Config;
using Nethereum.Web3;
using Nethereum.Web3.Accounts.Managed;
using Nethereum.Hex.HexTypes;
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
				var gethRpcUrl = Settings.GethRpcUrl;
				var coinBaseAddress = new Web3(gethRpcUrl).Eth.CoinBase.SendRequestAsync().Result;

				var senderAccount = new ManagedAccount(coinBaseAddress, Settings.CoinbasePass);
				var web3 = new Web3(senderAccount, gethRpcUrl);

				var abiFilepath = "contracts/contract.abi.json";
				var contractByteCodePath = "contracts/contract.bytecode.hex";

				var contractsUpdater = new ContractsUpdater(web3, coinBaseAddress, abiFilepath, contractByteCodePath);
				contractsUpdater.Start();

				var httpServer = new HttpServer(port);
				httpServer
					.AddHandler(HttpMethod.Get.ToString(), latestContractHttpPath,
						delegate(HttpListenerContext context)
						{
							return context.WriteStringAsync(contractsUpdater.MostRecentContract?.Address);
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

		private const int port = 14473;

		private static readonly ILog log = LogManager.GetLogger(typeof(Program));
	}
}
