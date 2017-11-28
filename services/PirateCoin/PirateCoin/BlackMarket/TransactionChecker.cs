using System;
using System.Threading;
using System.Threading.Tasks;
using log4net;
using Nethereum.Web3;

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

		public async Task<bool> Check(string transaction, string contractAddr)
		{
			var responseString = await web3.Client.SendRequestAsync<string>("trace_transaction", null, transaction);
			Console.WriteLine(responseString);
			return true;
		}

		private string abiFilepath;
		private string parityRpcUrl;
		private Web3 web3;

		private static readonly ILog log = LogManager.GetLogger(typeof(TransactionChecker));
	}
}
