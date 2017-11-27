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
				var senderAccount = new ManagedAccount(senderAddress, passPhrase);
				var web3 = new Web3(senderAccount, rpcUrl);

				var abiFilepath = "contracts/contract.abi.json";
				var contractByteCodePath = "contracts/contract.bytecode.hex";

				var contractsUpdater = new ContractsUpdater(web3, senderAddress, abiFilepath, contractByteCodePath);
				contractsUpdater.Start();

				var httpServer = new HttpServer(port);
				httpServer
					.AddHandler(HttpMethod.Get.ToString(), latestContractPath,
						delegate(HttpListenerContext context)
						{
							return context.WriteStringAsync(contractsUpdater.MostRecentContract?.Address);
						})
					.AcceptLoopAsync(CancellationToken.None)
					.Wait();
			}
			catch(Exception e)
			{
				log.Fatal("Unexpected app error", e);
			}
			

//			TestTransfer();
//			ShouldBeAbleToDeployAContractUsingPersonalUnlock().Wait();
		}

//		public static async Task ShouldBeAbleToDeployAContractUsingPersonalUnlock()
//		{
//			var multiplier = 7;
//
//			var senderAccount = new ManagedAccount(senderAddress, passPhrase);
//			var web3 = new Web3(senderAccount, rpcUrl);
//
//			var receipt = await web3.Eth.DeployContract.SendRequestAndWaitForReceiptAsync(abi, byteCode, senderAddress, new HexBigInteger(900000), null, multiplier);
//
//			var contract = web3.Eth.GetContract(abi, receipt.ContractAddress);
//
//			var multiplyFunction = contract.GetFunction("multiply");
//
//			var result = await multiplyFunction.CallAsync<int>(7);
//
//			Console.WriteLine($"result: {result}");
//		}
//
//		static void TestTransfer()
//		{
//			var senderAccount = new ManagedAccount(senderAddress, passPhrase);
//			Web3 web3 = new Web3(senderAccount, rpcUrl);
//
//			var transactionPolling = web3.TransactionManager.TransactionReceiptService;
//
//			var currentBalance = web3.Eth.GetBalance.SendRequestAsync(addressTo).Result;
//			Console.WriteLine($"currentBalance: {currentBalance.Value}");
//
//			var transactionReceipt = transactionPolling.SendRequestAsync(() => web3.TransactionManager.SendTransactionAsync(senderAccount.Address, addressTo, new HexBigInteger(amount))).Result;
//
//			var newBalance = web3.Eth.GetBalance.SendRequestAsync(addressTo).Result;
//			Console.WriteLine($"newBalance: {newBalance.Value}");
//		}

		const string latestContractPath = "/latestContract";

		private const int port = 14473;
		const string rpcUrl = "http://10.33.82.141:8545";

		const string senderAddress = "0x3dcbb3e4626f193f6fb097fe616e9d2edb69aca3";
		const string passPhrase = "qwer";

		const string addressTo = "0x8f65301cef3d055f05b69eb636ec8f77bb39988e";
		const int amount = 20;

		const string abi = @"[{""constant"":false,""inputs"":[{""name"":""val"",""type"":""int256""}],""name"":""multiply"",""outputs"":[{""name"":""d"",""type"":""int256""}],""type"":""function""},{""inputs"":[{""name"":""multiplier"",""type"":""int256""}],""type"":""constructor""}]";
		const string byteCode = "0x60606040526040516020806052833950608060405251600081905550602b8060276000396000f3606060405260e060020a60003504631df4f1448114601a575b005b600054600435026060908152602090f3";

		private static readonly ILog log = LogManager.GetLogger(typeof(Program));
	}
}
