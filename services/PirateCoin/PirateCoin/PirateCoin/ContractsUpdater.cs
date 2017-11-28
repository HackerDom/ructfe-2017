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
		public ContractsUpdater(string abiFilepath, string contractByteCodePath)
		{
			this.abiFilepath = abiFilepath;
			this.contractByteCodePath = contractByteCodePath;
		}

		private void ConnectToGethNode()
		{
			while(true)
			{
				try
				{
					var coinBaseAddress = new Web3(Settings.GethRpcUrl).Eth.CoinBase.SendRequestAsync().Result;
					accountAddress = coinBaseAddress;

					var senderAccount = new ManagedAccount(accountAddress, Settings.CoinbasePass);
					web3 = new Web3(senderAccount, Settings.GethRpcUrl);
					break;
				}
				catch(Exception e)
				{
					log.Info("Failed to connect to geth node with specified coinbase password. Sleeping and retrying", e);
					Thread.Sleep(5000);
				}
			}
		}

		public void Start()
		{
			worker = new Thread(() =>
			{
				ConnectToGethNode();
				log.Info($"Successfully connected to geth node {Settings.GethRpcUrl} via RPC");

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
						var receipt = web3.Eth.DeployContract.SendRequestAndWaitForReceiptAsync(abi, byteCode, accountAddress, contractDeployGas).Result;
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

		private readonly HexBigInteger contractDeployGas = new HexBigInteger(Settings.ContactCreationGas);
		private readonly TimeSpan contractDeployPeriod = TimeSpan.FromSeconds(Settings.ContractDeployPeriod);

		private static readonly ILog log = LogManager.GetLogger(typeof(ContractsUpdater));

		private Thread worker;

		private Web3 web3;
		private string contractByteCodePath;
		private string abiFilepath;
		private string accountAddress;
	}
}
