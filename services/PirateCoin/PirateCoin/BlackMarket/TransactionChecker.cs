using System;
using System.Collections.Generic;
using System.Globalization;
using System.IO;
using System.Linq;
using System.Net;
using System.Runtime.Serialization;
using System.Threading.Tasks;
using log4net;
using Nethereum.Web3;
using BigInteger = System.Numerics.BigInteger;

namespace BlackMarket
{
	partial class TransactionChecker
	{
		public TransactionChecker(string bankContractAbiFilepath, string bankAttackerContractAbiFilepath, string parityRpcUrl)
		{
			this.bankContractAbi = File.ReadAllText(bankContractAbiFilepath);
			this.bankAttackerContractAbi = File.ReadAllText(bankAttackerContractAbiFilepath);
			this.parityRpcUrl = parityRpcUrl;
		}

		public async Task<string> FindHackerContractOwnerIp(string contractAddr)
		{
			var web3 = new Web3(Settings.ParityRpcUrl);

			var contract = web3.Eth.GetContract(bankAttackerContractAbi, contractAddr);

			var ownerIp = await contract.GetFunction("ownerIp").CallAsync<uint>();
			return new IPAddress(BitConverter.GetBytes(ownerIp)).ToString();
		}

		public async Task<string> CheckTransactionAndFindHackerContractAddr(string transaction, string contractAddr, decimal flagSumEth)
		{
			var trace = await TransactionTracer.TraceTransactionAsync(transaction, parityRpcUrl);
			if(trace == null)
			{
				log.Info($"Refused addr {contractAddr} hacking transaction candidate {transaction}: transaction trace returned zero result");
				return null;
			}

			var moneyTransfersDict = trace
				.Select(item => item.action)
				.Select(action => new
				{
					fromAddr = action.fromAddr?.ToLowerInvariant(),
					toAddr = action.toAddr?.ToLowerInvariant(),
					sum = BigInteger.Parse("0" + (action.value?.Substring(2) ?? "0"), NumberStyles.AllowHexSpecifier)
				})
				.Where(mt => mt.fromAddr == contractAddr && mt.sum > 0)
				.GroupBy(mt => mt.toAddr)
				.ToDictionary(grouping => grouping.Key, grouping => grouping);

			if(moneyTransfersDict.Count != 1)
			{
				log.Info($"Refused addr {contractAddr} hacking transaction candidate {transaction}: has {moneyTransfersDict.Count} money recepients, but expected 1");
				return null;
			}

			var hacker = moneyTransfersDict.First();
			var hackerAddr = hacker.Key;

			BigInteger receivedSumInWei = 0;
			foreach(var mt in hacker.Value)
				receivedSumInWei += mt.sum;

			var ten = new BigInteger(10);
			var weisInEth = BigInteger.Pow(ten, 18);
			var flagSumWei = new BigInteger(flagSumEth) * weisInEth;

			if(receivedSumInWei < flagSumWei)
			{
				log.Info($"Refused addr {contractAddr} hacking transaction candidate {transaction}: hacker contract address {hackerAddr} received {receivedSumInWei} wei < expected {flagSumEth} eth");
				return null;
			}

			return hackerAddr;
		}

		public async Task<bool> CheckContractBalanceIsHacked(string contractAddr)
		{
			var web3 = new Web3(Settings.ParityRpcUrl);

			var contract = web3.Eth.GetContract(bankContractAbi, contractAddr);

			var totalBankBalance = await contract.GetFunction("totalBankBalance").CallAsync<BigInteger>();
			var totalEthBalance = (await web3.Eth.GetBalance.SendRequestAsync(contractAddr)).Value;

			return totalEthBalance < totalBankBalance;
		}

		

		private string bankContractAbi;
		private string bankAttackerContractAbi;
		private string parityRpcUrl;

		private static readonly ILog log = LogManager.GetLogger(typeof(TransactionChecker));
	}

	[DataContract]
	class TraceResponse
	{
		[DataMember] public List<TraceResponseItem> result;
		[DataMember] public int id;
		[DataMember] public string jsonrpc;
	}

	[DataContract]
	public class TraceResponseItem
	{
		[DataMember] public TraceAction action;
	}

	[DataContract]
	public class TraceAction
	{
		[DataMember] public string callType;
		[DataMember(Name = "from")] public string fromAddr;
		[DataMember(Name = "to")] public string toAddr;
		[DataMember] public string input;
		[DataMember] public string value;
	}

	[DataContract]
	class TraceRequest
	{
		[DataMember] public string method;
		[DataMember] public List<string> @params;
		[DataMember] public int id;
		[DataMember] public string jsonrpc;
	}
}
