using System;
using System.Collections.Generic;
using System.Net.Http;
using System.Text;
using System.Threading.Tasks;
using PirateCoin.Utils;

namespace BlackMarket
{
	public static class TransactionTracer
	{
		public static async Task<List<TraceResponseItem>> TraceTransactionAsync(string transaction, string parityRpcUrl)
		{
			var httpResult = await AsyncHttpClient.DoRequestAsync(new Uri(parityRpcUrl), HttpMethod.Post.ToString(), "application/json",
				Encoding.UTF8.GetBytes(new TraceRequest { method = "trace_transaction", @params = new List<string> { transaction }, id = 1, jsonrpc = "2.0" }.ToJsonString()));

			var traceResponse = JsonHelper.ParseJson<TraceResponse>(httpResult.ResponseBytes);
			return traceResponse.result;
		}
	}
	
}
