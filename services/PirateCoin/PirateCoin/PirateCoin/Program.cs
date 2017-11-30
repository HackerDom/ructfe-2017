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
					.AddHandler(HttpMethod.Get.ToString(), "/", async context =>
					{
						context.Response.ContentType = "text/plain";
						await context.WriteStringAsync(@"Hello! This is PirateCoin service. It's a smart contracts deploying service, based on Ethereum blockchain.
This service does not store any flag by itself, it only serves as a coins wallet.
You can rather buy flags on BlackMarket after you steal coins from other team's smart contracts.

Check blockchain and find other team's smart contracts, which are regularly populated by checksystem with coins,
and try to steal that coins from them. If you manage to convince BlackMarket that you stole coins
from other team's contract, you'll be given team's flag(s).

NOTE that:
 * 'steal' means: withdraw more than you deposited
 * The steal should be a result of a single transaction rather than a result of complex set of your actions 
 * Your smart contract, which helps you steal coins, will be checked by BlackMarket according to this ABI:
   [{""constant"":true,""inputs"":[],""name"":""ownerIp"",""outputs"":[{""name"":"""",""type"":""uint32""}],""payable"":false,""stateMutability"":""view"",
   ""type"":""function""},{""payable"":true,""stateMutability"":""payable"",""type"":""fallback""}]{""payable"":true,""stateMutability"":""payable"",""type"":""fallback""}]

   -> so it should contain a public variable named 'ownerIp' with any packed ip-address from your team's subnet.
      'packed' means BlackMarket will unpack it with: new IPAddress(BitConverter.GetBytes(ownerIp)).ToString()

Use /checkTransaction?transaction=<STEALING_TRANSACTION_HASH>&contractAddr=<VICTIM_SMART_CONTRACT_ADDR>
on http://blackmarket.piratecoin.ructfe.org:14474 (which is http://10.10.10.101:14474) after you steal the coins.

GL HF");
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
