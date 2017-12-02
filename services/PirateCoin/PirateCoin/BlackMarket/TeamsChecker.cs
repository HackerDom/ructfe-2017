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
		public TeamsChecker(string parityRpcUrl, string gethRpcUrl, string bankContractAbiFilepath, string GethPass)
		{
			this.parityRpcUrl = parityRpcUrl;
			this.gethRpcUrl = gethRpcUrl;
			this.bankContractAbi = File.ReadAllText(bankContractAbiFilepath);
			this.gethPass = GethPass;

			CoinbaseAddress = new Web3(gethRpcUrl).Eth.CoinBase.SendRequestAsync().Result;
			log.Info($"Got Geth coinbase {CoinbaseAddress}");
		}

		private Web3 ConnectToGethNode()
		{
			while(true)
			{
				try
				{
					var senderAccount = new ManagedAccount(CoinbaseAddress, gethPass);
					return new Web3(senderAccount, gethRpcUrl);
				}
				catch(Exception e)
				{
					log.Info("Failed to connect to Geth node with specified coinbase password. Sleeping and retrying", e);
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
					log.Info($"New team '{vulnboxIp}' checking started. Waiting {random}sec before start");
					Thread.Sleep(TimeSpan.FromSeconds(random));

					var web3 = ConnectToGethNode();
					log.Info($"Successfully connected to parity node '{parityRpcUrl}' via RPC");

					var lastContractCheckStartTime = DateTime.MinValue;
					while(true)
					{
						var secondsToSleep = Math.Max(0, contractDeployPeriod.Subtract(DateTime.UtcNow.Subtract(lastContractCheckStartTime)).TotalSeconds);
						if(secondsToSleep > 0)
						{
							log.Info($"Waiting {secondsToSleep}sec. before checking vulnbox '{vulnboxIp}");
							Thread.Sleep(TimeSpan.FromSeconds(secondsToSleep));
						}
						lastContractCheckStartTime = DateTime.UtcNow;

						try
						{
							log.Info($"Checking vulnbox '{vulnboxIp}' contract '{contractAddr}'");

							var contract = web3.Eth.GetContract(bankContractAbi, contractAddr);

							var transactionPolling = web3.TransactionManager.TransactionReceiptService;

							var transactionSendReceipt = transactionPolling.SendRequestAsync(() => contract.GetFunction("addToBalance").SendTransactionAsync(CoinbaseAddress, contactCallGas, contactTransactAmount)).Result;
							log.Info($"Sent {contactTransactAmount.Value} wei to team '{vulnboxIp}' contract '{contractAddr}' transaction '{transactionSendReceipt.TransactionHash}' in block {transactionSendReceipt.BlockNumber.Value}");

							var transactionWithdrawReceipt = transactionPolling.SendRequestAsync(() => contract.GetFunction("withdrawBalance").SendTransactionAsync(CoinbaseAddress, contactCallGas, new HexBigInteger(0))).Result;
							log.Info($"Sent withdraw receipt from team '{vulnboxIp}' contract '{contractAddr}' transaction '{transactionWithdrawReceipt.TransactionHash}' in block {transactionWithdrawReceipt.BlockNumber.Value}");

							//NOTE to have parity synchronized with blockchain
							Thread.Sleep(TimeSpan.FromSeconds(5));
							var trace = TransactionTracer.TraceTransactionAsync(transactionWithdrawReceipt.TransactionHash, parityRpcUrl).Result;

							var moneyReturns = (trace ?? new List<TraceResponseItem>())
								.Select(item => item.action)
								.Select(action => new
								{
									fromAddr = action.fromAddr?.ToLowerInvariant(),
									toAddr = action.toAddr?.ToLowerInvariant(),
									sum = BigInteger.Parse("0" + (action.value?.Substring(2) ?? "0"), NumberStyles.AllowHexSpecifier)
								})
								.Where(mt => mt.fromAddr == contractAddr && mt.toAddr == CoinbaseAddress && mt.sum > 0)
								.ToList();

							var totalSumReturned = new BigInteger(0);
							foreach(var mr in moneyReturns)
								totalSumReturned += mr.sum;

							bool illegallyPatched = false;
							if(totalSumReturned < contactTransactAmount)
							{
								log.Info($"Witdrawal team '{vulnboxIp}' contract '{contractAddr}' transaction '{transactionWithdrawReceipt.TransactionHash}' tracing returned {totalSumReturned} < we sent {contactTransactAmount}. Considering vulnbox illegaly patched");
								teamsStatus[vulnboxIp] = DateTime.UtcNow;
								illegallyPatched = true;
							}

							var msg = illegallyPatched ? "ILLEGAL PATCH" : "OK";
							log.Warn($"Checked team '{vulnboxIp}' contract '{contractAddr}' -> {msg}");
						}
						catch(Exception e)
						{
							log.Error($"Unexpected error while checking vulnbox '{vulnboxIp}' contract '{contractAddr}'", e);
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
		private string gethRpcUrl;
		private string bankContractAbi;
		private string gethPass;

		private string CoinbaseAddress;

		private static readonly ILog log = LogManager.GetLogger(typeof(TeamsChecker));
	}
}