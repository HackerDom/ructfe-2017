using System;
using System.Collections.Generic;
using System.Diagnostics;
using System.IO;
using System.Linq;
using System.Text;
using System.Threading;
using System.Threading.Tasks;
using log4net;
using Nethereum.Contracts;
using Nethereum.Hex.HexTypes;
using Nethereum.Web3;

namespace PirateCoin
{
	class ContractsUpdater
	{
		public ContractsUpdater(Web3 web3, string accountAddress, string abiFilepath, string contractByteCodePath)
		{
			this.web3 = web3;
			this.abiFilepath = abiFilepath;
			this.accountAddress = accountAddress;
			this.contractByteCodePath = contractByteCodePath;
		}

		public Contract MostRecentContract { get; set; }

		public void Start()
		{
			worker = new Thread(() =>
			{
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
			});
			worker.Start();
		}

		private readonly HexBigInteger contractDeployGas = new HexBigInteger(900000);
		private readonly TimeSpan contractDeployPeriod = TimeSpan.FromSeconds(30);

		private static readonly ILog log = LogManager.GetLogger(typeof(ContractsUpdater));

		private Thread worker;

		private Web3 web3;
		private string contractByteCodePath;
		private string abiFilepath;
		private string accountAddress;
	}
}
