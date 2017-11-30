﻿using System;
using System.Collections.Generic;
using System.Globalization;
using System.IO;
using System.Linq;
using System.Net.Http;
using System.Net;
using System.Runtime.Serialization;
using System.Text;
using System.Threading.Tasks;
using log4net;
using Nethereum.Web3;
using PirateCoin.Utils;
using BigInteger = System.Numerics.BigInteger;

namespace BlackMarket
{
	class TransactionChecker
	{
		public TransactionChecker(string bankContractAbiFilepath, string bankAttackerContractAbiFilepath, string parityRpcUrl)
		{
			this.bankContractAbiFilepath = bankContractAbiFilepath;
			this.bankAttackerContractAbiFilepath = bankAttackerContractAbiFilepath;
			this.parityRpcUrl = parityRpcUrl;
		}

		public async Task<string> FindHackerContractOwnerIp(string contractAddr)
		{
			var web3 = new Web3(Settings.ParityRpcUrl);

			var contract = web3.Eth.GetContract(File.ReadAllText(bankAttackerContractAbiFilepath), contractAddr);

			var ownerIp = await contract.GetFunction("ownerIp").CallAsync<uint>();
			return new IPAddress(BitConverter.GetBytes(ownerIp)).ToString();
		}

		public async Task<string> CheckTransactionAndFindHackerContractAddr(string transaction, string contractAddr, decimal flagSumEth)
		{
			var httpResult = await AsyncHttpClient.DoRequestAsync(new Uri(parityRpcUrl), HttpMethod.Post.ToString(), "application/json", 
				Encoding.UTF8.GetBytes(new TraceRequest {method = "trace_transaction", @params = new List<string>{transaction}, id = 1, jsonrpc = "2.0" }.ToJsonString()));

			var traceResponse = JsonHelper.ParseJson<TraceResponse>(httpResult.ResponseBytes);
			if(traceResponse.result == null)
			{
				log.Info($"Refused addr {contractAddr} hacking transaction candidate {transaction}: transaction trace returned zero result");
				return null;
			}

			var moneyTransfersDict = traceResponse.result
				.Select(item => item.action)
				.Select(action =>
				{
					return new
					{
						fromAddr = action.fromAddr?.ToLowerInvariant(),
						toAddr = action.toAddr?.ToLowerInvariant(),
						sum = BigInteger.Parse("0" + (action.value?.Substring(2) ?? "0"), NumberStyles.AllowHexSpecifier)
					};
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

			var contract = web3.Eth.GetContract(File.ReadAllText(bankContractAbiFilepath), contractAddr);

			var totalBankBalance = await contract.GetFunction("totalBankBalance").CallAsync<BigInteger>();
			var totalEthBalance = (await web3.Eth.GetBalance.SendRequestAsync(contractAddr)).Value;

			return totalEthBalance < totalBankBalance;
		}

		[DataContract]
		class TraceResponse
		{
			[DataMember] public List<TraceResponseItem> result;
			[DataMember] public int id;
			[DataMember] public string jsonrpc;
		}

		[DataContract]
		class TraceResponseItem
		{
			[DataMember] public TraceAction action;
		}

		[DataContract]
		class TraceAction
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

		private string bankContractAbiFilepath;
		private string bankAttackerContractAbiFilepath;
		private string parityRpcUrl;

		private static readonly ILog log = LogManager.GetLogger(typeof(TransactionChecker));
	}
}
