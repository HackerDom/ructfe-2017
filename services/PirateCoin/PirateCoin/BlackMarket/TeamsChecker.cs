using System;
using System.Collections.Concurrent;
using System.Collections.Generic;
using System.Globalization;
using System.IO;
using System.Linq;
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
		public TeamsChecker(string parityRpcUrl, string bankContractAbiFilepath, string sendingAccount, string coinbasePass)
		{
			this.parityRpcUrl = parityRpcUrl;
			this.bankContractAbi = File.ReadAllText(bankContractAbiFilepath);
			this.sendingAccount = sendingAccount;
			this.coinbasePass = coinbasePass;
		}

		private Web3 ConnectToParityNode()
		{
			while(true)
			{
				try
				{
					var senderAccount = new ManagedAccount(sendingAccount, coinbasePass);
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
					var random = new Random().Next(30);
					log.Info($"New team {vulnboxIp} checking started. Sleeping {random} sec before start");
					Thread.Sleep(TimeSpan.FromSeconds(random));

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
						lastContractCheckStartTime = DateTime.UtcNow;

						try
						{
							log.Info($"Checking vulnbox {vulnboxIp} contract {contractAddr}");

							var contract = web3.Eth.GetContract(bankContractAbi, contractAddr);

							var transactionPolling = web3.TransactionManager.TransactionReceiptService;

							var transactionSendReceipt = transactionPolling.SendRequestAsync(() => contract.GetFunction("addToBalance").SendTransactionAsync(sendingAccount, contactCallGas, contactTransactAmount)).Result;
							log.Info($"Sent money to contract {contractAddr}, transaction {transactionSendReceipt.TransactionHash} in block {transactionSendReceipt.BlockNumber}");

							var transactionWithdrawReceipt = transactionPolling.SendRequestAsync(() => contract.GetFunction("withdrawBalance").SendTransactionAsync(sendingAccount, contactCallGas, new HexBigInteger(0))).Result;
							log.Info($"Sent withdraw receipt from contract {contractAddr}, transaction {transactionWithdrawReceipt.TransactionHash} in block {transactionWithdrawReceipt.BlockNumber}");

							var trace = TransactionTracer.TraceTransactionAsync(transactionWithdrawReceipt.TransactionHash, parityRpcUrl).Result;

							var moneyReturns = (trace ?? new List<TraceResponseItem>())
								.Select(item => item.action)
								.Select(action => new
								{
									fromAddr = action.fromAddr?.ToLowerInvariant(),
									toAddr = action.toAddr?.ToLowerInvariant(),
									sum = BigInteger.Parse("0" + (action.value?.Substring(2) ?? "0"), NumberStyles.AllowHexSpecifier)
								})
								.Where(mt => mt.fromAddr == contractAddr && mt.toAddr == sendingAccount && mt.sum > 0)
								.ToList();

							var totalSumReturned = new BigInteger(0);
							foreach(var mr in moneyReturns)
								totalSumReturned += mr.sum;

							if(totalSumReturned < contactTransactAmount)
							{
								log.Info($"Witdrawal transaction {transactionWithdrawReceipt.TransactionHash} team {vulnboxIp} contract {contractAddr} tracing returned {totalSumReturned} < we sent {contactTransactAmount}. Considering vulnbox illegaly patched");
								teamsStatus[vulnboxIp] = DateTime.UtcNow;
							}
						}
						catch(Exception e)
						{
							log.Error($"Unexpected error while checking vulnbox {vulnboxIp}", e);
							Thread.Sleep(TimeSpan.FromSeconds(1));
						}
					}
				}){ IsBackground = true }.Start();
		}

		public DateTime GetLastIllegalPatchedDetectedDt(string vulnboxIp)
		{
			if(teamsStatus.TryGetValue(vulnboxIp, out var result))
				return result;
			return DateTime.MinValue;
		}

		private readonly TimeSpan contractDeployPeriod = TimeSpan.FromSeconds(60);

		private ConcurrentDictionary<string, DateTime> teamsStatus = new ConcurrentDictionary<string, DateTime>();
		private ConcurrentDictionary<string, string> teamsContracts = new ConcurrentDictionary<string, string>();


		private readonly HexBigInteger contactCallGas = new HexBigInteger("90000");
		private readonly HexBigInteger contactTransactAmount = new HexBigInteger(new BigInteger(1000000000000000000m));

		private string parityRpcUrl;
		private string bankContractAbi;
		private string sendingAccount;
		private string coinbasePass;

		private static readonly ILog log = LogManager.GetLogger(typeof(TeamsChecker));
	}
}