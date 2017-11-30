using System;
using System.Collections.Generic;
using System.Collections.Specialized;
using System.Globalization;
using System.Linq;
using System.Net.Http;
using System.Runtime.Serialization;
using System.Text;
using System.Threading;
using System.Threading.Tasks;
using log4net;
using Nethereum.Web3;
using Org.BouncyCastle.Math;
using PirateCoin.Utils;
using BigInteger = System.Numerics.BigInteger;

namespace BlackMarket
{
	class TransactionChecker
	{
		public TransactionChecker(string abiFilepath, string parityRpcUrl)
		{
			this.abiFilepath = abiFilepath;
			this.parityRpcUrl = parityRpcUrl;
		}

		private void ConnectToParityNode()
		{
			while(true)
			{
				try
				{
					web3 = new Web3(parityRpcUrl);
					break;
				}
				catch(Exception e)
				{
					log.Info("Failed to connect to Parity node with specified coinbase password. Sleeping and retrying", e);
					Thread.Sleep(5000);
				}
			}
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

		public async Task<string> FindHackerContractAddr(string transaction, string contractAddr, decimal flagSumEth)
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

			log.Info("Go");

			var hackerKv = moneyTransfersDict.First();
			var hackerAddr = hackerKv.Key;

			BigInteger receivedSumInWei = 0;
			foreach(var mt in hackerKv.Value)
				receivedSumInWei += mt.sum;

			var ten = new BigInteger(10);
			var weiInEth = BigInteger.Pow(ten, 18);
			var flagSumWei = new BigInteger(flagSumEth) * weiInEth;

			if(receivedSumInWei < flagSumWei)
			{
				log.Info($"Refused addr {contractAddr} hacking transaction candidate {transaction}: hacker contract address {hackerAddr} received {receivedSumInWei} wei < expected {flagSumEth} eth");
				return null;
			}

			return hackerAddr;
		}

		private string abiFilepath;
		private string parityRpcUrl;
		private Web3 web3;

		private static readonly ILog log = LogManager.GetLogger(typeof(TransactionChecker));
	}
}
