using System;
using System.Diagnostics;
using System.IO;
using System.Threading;
using log4net;
using Nethereum.Contracts;
using Nethereum.Hex.HexTypes;
using Nethereum.Web3;
using Nethereum.Web3.Accounts.Managed;

namespace PirateCoin
{
	class ContractsUpdater
	{
		public ContractsUpdater(string abiFilepath, string contractByteCodePath, string gethRpcUrl, string coinbasePass, int contactCreationGas, int contractDeployPeriod)
		{
			this.abiFilepath = abiFilepath;
			this.contractByteCodePath = contractByteCodePath;

			this.coinbasePass = coinbasePass;
			this.gethRpcUrl = gethRpcUrl;
			this.contactCreationGas = new HexBigInteger(contactCreationGas);
			this.contractDeployPeriod = TimeSpan.FromSeconds(contractDeployPeriod);
		}

		private void ConnectToGethNode()
		{
			while(true)
			{
				try
				{
					CoinbaseAddress = new Web3(gethRpcUrl).Eth.CoinBase.SendRequestAsync().Result;

					var senderAccount = new ManagedAccount(CoinbaseAddress, coinbasePass);
					web3 = new Web3(senderAccount, gethRpcUrl);
					break;
				}
				catch(Exception e)
				{
					log.Info("Failed to connect to Geth node with specified coinbase password. Sleeping and retrying", e);
					Thread.Sleep(5000);
				}
			}
		}

		public void Start()
		{
			var worker = new Thread(() =>
			{
				ConnectToGethNode();
				log.Info($"Successfully connected to geth node {gethRpcUrl} via RPC");

				var lastContractDeployStartTime = DateTime.MinValue;
				while(true)
				{
					var secondsToSleep = Math.Max(0, contractDeployPeriod.Subtract(DateTime.UtcNow.Subtract(lastContractDeployStartTime)).TotalSeconds);
					if(secondsToSleep > 0)
					{
						log.Info($"Waiting {secondsToSleep} sec. before deploying new contract to blockchain");
						Thread.Sleep(TimeSpan.FromSeconds(secondsToSleep));
					}

					try
					{
						var abi = File.ReadAllText(abiFilepath);
						var byteCode = File.ReadAllText(contractByteCodePath);

						log.Info("Deploying new contract to blockchain");
						lastContractDeployStartTime = DateTime.UtcNow;
						var sw = Stopwatch.StartNew();
						var receipt = web3.Eth.DeployContract.SendRequestAndWaitForReceiptAsync(abi, byteCode, CoinbaseAddress, contactCreationGas).Result;
						sw.Stop();
						
						var contract = MostRecentContract = web3.Eth.GetContract(abi, receipt.ContractAddress);
						log.Info($"Contract deployed at address {contract.Address} in {sw.Elapsed}");
					}
					catch(Exception e)
					{
						log.Error("Unexpected error while deploying contract", e);
						Thread.Sleep(TimeSpan.FromSeconds(1));
					}
				}
			}){IsBackground = true};
			worker.Start();
		}

		public Contract MostRecentContract { get; private set; }

		private readonly string coinbasePass;
		private readonly string gethRpcUrl;
		private readonly HexBigInteger contactCreationGas;
		private readonly TimeSpan contractDeployPeriod;

		private static readonly ILog log = LogManager.GetLogger(typeof(ContractsUpdater));

		private Web3 web3;
		private string contractByteCodePath;
		private string abiFilepath;
		public string CoinbaseAddress { get; private set; }
	}
}
