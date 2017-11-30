using System;
using System.Linq;
using System.Net;
using System.Net.Http;
using System.Text;
using System.Threading;
using System.Threading.Tasks;
using log4net;
using log4net.Config;
using PirateCoin;
using PirateCoin.http;

namespace BlackMarket
{
	class Program
	{
		static void Main(string[] args)
		{
			XmlConfigurator.Configure();
			try
			{
				stateManager = new StateManager("state.json");
				transactionChecker = new TransactionChecker(null, Settings.ParityRpcUrl);

				var httpServer = new HttpServer(port);
				httpServer
					.AddHandler(HttpMethod.Get.ToString(), putFlagHttpPath, PutFlagCallback)
					.AddHandler(HttpMethod.Get.ToString(), checkFlagHttpPath, CheckFlagCallback)
					.AddHandler(HttpMethod.Get.ToString(), checkTransactionHttpPath, CheckTransactionCallback)
					.AcceptLoopAsync(CancellationToken.None)
					.Wait();
			}
			catch(Exception e)
			{
				log.Fatal("Unexpected App Error", e);
			}
		}

		private static async Task PutFlagCallback(HttpListenerContext context)
		{
			var flag = context.Request.QueryString["flag"];
			var contractAddr = context.Request.QueryString["contractAddr"]?.ToLowerInvariant();
			var sumStr = context.Request.QueryString["sum"];

			if(flag == null || contractAddr == null || !decimal.TryParse(sumStr, out var sum))
			{
				context.Close((int)HttpStatusCode.BadRequest);
				return;
			}

			stateManager.Insert(new FlagData { contractAddr = contractAddr, flag = flag, sum = sum });
		}

		private static async Task CheckTransactionCallback(HttpListenerContext context)
		{
			var transaction = context.Request.QueryString["transaction"];
			var contractAddr = context.Request.QueryString["contractAddr"]?.ToLowerInvariant();
			if(transaction == null || contractAddr == null)
			{
				context.Close((int)HttpStatusCode.BadRequest);
				return;
			}

			var flagsData = stateManager.FindByContractAddr(contractAddr);
			if(flagsData == null)
			{
				context.Close((int)HttpStatusCode.NotFound);
				return;
			}

			var flags = string.Join(",", flagsData.Select(data => data.flag));

			var requestIp = context.Request.RemoteEndPoint.Address.ToString();
			var hackerIp = flagsData.FirstOrDefault(data => data.hackerIp != null)?.hackerIp;
			if(IsSameTeam(requestIp, hackerIp))
			{
				await context.WriteStringAsync(flags);
				return;
			}

			if(hackerIp != null)
			{
				context.Close((int)HttpStatusCode.Gone);
				return;
			}

			//NOTE race condition, but it's ok. just giving concurrnt hackers their flags
			var hackerContractAddr = await transactionChecker.FindHackerContractAddr(transaction, contractAddr, flagsData.First().sum);
			if(hackerContractAddr !=  null)
			{
				foreach(var flagData in flagsData)
				{
					flagData.hackerIp = requestIp;
					stateManager.Insert(flagData);
				}
				await context.WriteStringAsync(flags);
				return;
			}

			context.Close((int)HttpStatusCode.Unauthorized);
		}

		private static bool IsSameTeam(string ipA, string ipB)
		{
			if(ipA == ipB)
				return true;
			if(ipA == null || ipB == null)
				return false;

			return ipA.Substring(0, ipA.LastIndexOf(".")) == ipB.Substring(0, ipB.LastIndexOf("."));
		}

		private static async Task CheckFlagCallback(HttpListenerContext context)
		{
			var flag = context.Request.QueryString["flag"];
			var contractAddr = context.Request.QueryString["contractAddr"]?.ToLowerInvariant();
			if(flag == null || contractAddr == null)
			{
				context.Close((int)HttpStatusCode.BadRequest);
				return;
			}

			var flagsData = stateManager.FindByContractAddr(contractAddr);
			FlagData flagData;
			if(flagsData == null || (flagData = flagsData.FirstOrDefault(fd => flag == fd.flag)) == null)
			{
				context.Close((int)HttpStatusCode.NotFound);
				return;
			}

			if(flagData.hackerIp != null)
				await context.WriteStringAsync(flagData.hackerIp);
		}

		const string putFlagHttpPath = "/putFlag";
		const string checkFlagHttpPath = "/checkFlag";
		const string checkTransactionHttpPath = "/checkTransaction";

		private const int port = 14474;

		private static StateManager stateManager;
		private static TransactionChecker transactionChecker;

		private static readonly ILog log = LogManager.GetLogger(typeof(Program));
	}
}
