using System;
using System.Collections.Concurrent;
using System.IO;
using System.Numerics;
using System.Threading;
using log4net;
using Nethereum.Hex.HexTypes;
using Nethereum.Web3;
using Nethereum.Web3.Accounts.Managed;

namespace BlackMarket
{
	public class TeamsChecker
	{
		public TeamsChecker(string parityRpcUrl, string bankContractAbiFilepath, string account, string coinbasePass)
		{
			this.parityRpcUrl = parityRpcUrl;
			this.bankContractAbi = File.ReadAllText(bankContractAbiFilepath);
			this.account = account;
			this.coinbasePass = coinbasePass;
		}

		private Web3 ConnectToParityNode()
		{
			while(true)
			{
				try
				{
					var senderAccount = new ManagedAccount(account, coinbasePass);
					return new Web3(senderAccount, parityRpcUrl);
				}
				catch(Exception e)
				{
					log.Info("Failed to connect to Parity node with specified coinbase password. Sleeping and retrying", e);
					Thread.Sleep(5000);
				}
			}
		}

		public void UpdateLatestTeamContract(string vulnboxIp, string contractAddr)
		{
			var alreadyChecking = teamsContracts.ContainsKey(vulnboxIp);
			teamsContracts[vulnboxIp] = contractAddr;

			if(!alreadyChecking)
				new Thread(() =>
				{
					var web3 = ConnectToParityNode();
					log.Info($"Successfully connected to parity node {parityRpcUrl} via RPC");

					var lastContractCheckStartTime = DateTime.MinValue;
					while(true)
					{
						var secondsToSleep = Math.Max(0, contractDeployPeriod.Subtract(DateTime.UtcNow.Subtract(lastContractCheckStartTime)).TotalSeconds);
						if(secondsToSleep > 0)
						{
							log.Info($"Waiting {secondsToSleep} sec. before checking vulnbox {vulnboxIp}");
							Thread.Sleep(TimeSpan.FromSeconds(secondsToSleep));
						}

						try
						{
							log.Info("Sending test deposit");
							lastContractCheckStartTime = DateTime.UtcNow;

							var contract = web3.Eth.GetContract(bankContractAbi, contractAddr);

							var transactionPolling = web3.TransactionManager.TransactionReceiptService;

							var transactionSendReceipt = transactionPolling.SendRequestAsync(() => contract.GetFunction("addToBalance").SendTransactionAsync(account, contactCallGas, contactTransactAmount)).Result;
							log.Info($"Sent money to contract {contractAddr}, transaction {transactionSendReceipt.TransactionHash} in block {transactionSendReceipt.BlockNumber}");

							var transactionAddWithdraw = transactionPolling.SendRequestAsync(() => contract.GetFunction("withdrawBalance").SendTransactionAsync(account, contactCallGas, new HexBigInteger("1"))).Result;
							log.Info($"Sent withdraw receipt from contract {contractAddr}, transaction {transactionAddWithdraw.TransactionHash} in block {transactionAddWithdraw.BlockNumber}");
						}
						catch(Exception e)
						{
							log.Error($"Unexpected error while checking vulnbox {vulnboxIp}", e);
							Thread.Sleep(TimeSpan.FromSeconds(1));
						}
					}
				}){ IsBackground = true }.Start();
		}

		private readonly TimeSpan contractDeployPeriod = TimeSpan.FromSeconds(60);

		public ConcurrentDictionary<string, int> teamsStatus = new ConcurrentDictionary<string, int>();
		public ConcurrentDictionary<string, string> teamsContracts = new ConcurrentDictionary<string, string>();


		private readonly HexBigInteger contactCallGas = new HexBigInteger("90000");
		private readonly HexBigInteger contactTransactAmount = new HexBigInteger(new BigInteger(1000000000000000000m));

		private string parityRpcUrl;
		private string bankContractAbi;
		private string account;
		private string coinbasePass;

		private static readonly ILog log = LogManager.GetLogger(typeof(TeamsChecker));
	}
}