using System;
using System.Globalization;
using System.Linq;
using System.Net;
using System.Net.Http;
using System.Threading;
using System.Threading.Tasks;
using log4net;
using log4net.Config;
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
				transactionChecker = new TransactionChecker(bankContractAbiFilepath, bankAttackerContractAbiFilepath, Settings.ParityRpcUrl);
				teamsChecker = new TeamsChecker(Settings.ParityRpcUrl, bankContractAbiFilepath, Settings.SourceAccount, Settings.Pass);

				var httpServer = new HttpServer(port);
				httpServer
					.AddHandler(HttpMethod.Get.ToString(), putFlagHttpPath, PutFlagCallback)
					.AddHandler(HttpMethod.Get.ToString(), checkFlagHttpPath, CheckFlagCallback)
					.AddHandler(HttpMethod.Get.ToString(), checkTransactionHttpPath, CheckTransactionCallback)
					.AddHandler(HttpMethod.Get.ToString(), checkTeamHttpPath, CheckTeamCallback)
					.AcceptLoopAsync(CancellationToken.None)
					.Wait();
			}
			catch(Exception e)
			{
				log.Fatal("Unexpected App Error", e);
			}
		}

		private static async Task CheckTeamCallback(HttpListenerContext context)
		{
			var vulnboxIp = context.Request.QueryString["vulnboxIp"];
			if(vulnboxIp == null)
				throw new HttpException((int)HttpStatusCode.BadRequest, "expected params 'vulnboxIp'");

			if(!teamsChecker.teamsStatus.TryGetValue(vulnboxIp, out var secondsAfterLastMumble))
				secondsAfterLastMumble = int.MaxValue;

			await context.WriteStringAsync(secondsAfterLastMumble.ToString());
		}

		private static async Task PutFlagCallback(HttpListenerContext context)
		{
			var flag = context.Request.QueryString["flag"];
			var contractAddr = context.Request.QueryString["contractAddr"]?.ToLowerInvariant();
			var sumStr = context.Request.QueryString["sum"];
			var vulnboxIp = context.Request.QueryString["vulnboxIp"];

			if(flag == null || contractAddr == null || !decimal.TryParse(sumStr, NumberStyles.Any, CultureInfo.InvariantCulture, out var sum) || vulnboxIp == null)
				throw new HttpException((int)HttpStatusCode.BadRequest, "expected params 'flag', 'contractAddr', 'sum', 'vulnboxIp'");

			stateManager.Insert(new FlagData { contractAddr = contractAddr, flag = flag, sum = sum });
			teamsChecker.UpdateLatestTeamContract(vulnboxIp, contractAddr);

			await context.WriteStringAsync("Done");
		}

		
		private static async Task CheckTransactionCallback(HttpListenerContext context)
		{
			var requestIp = context.Request.RemoteEndPoint.Address.ToString();
			var team = GetNormalizedTeamSubnetFromIp(requestIp);

			AntiFlood.CheckFlood(team, 60, 768);

			var transaction = context.Request.QueryString["transaction"];
			var contractAddr = context.Request.QueryString["contractAddr"]?.ToLowerInvariant();
			if(transaction == null || contractAddr == null)
				throw new HttpException((int)HttpStatusCode.BadRequest, "expected params 'transaction', 'contractAddr'");

			var flags = stateManager.FindByContractAddr(contractAddr);
			if(flags == null)
				throw new HttpException((int) HttpStatusCode.NotFound, $"don't have flags for contract '{contractAddr}'");

			var flagsString = string.Join(",", flags.Select(data => data.flag));

			var hackerIp = flags.FirstOrDefault(data => data.hackerIp != null)?.hackerIp;
			if(hackerIp != null)
			{
				if(IsSameTeam(requestIp, hackerIp))
					await context.WriteStringAsync(flagsString);
				else
					throw new HttpException((int)HttpStatusCode.Gone, $"flag(s) from this contract are already stolen and not by your team, your ip: {requestIp}");
				return;
			}

			var isContactBalanceHacked = await transactionChecker.CheckContractBalanceIsHacked(contractAddr);
			if(!isContactBalanceHacked)
				throw new HttpException((int) HttpStatusCode.Unauthorized,
					"contract does not look being hacked (total balance on all deposits seems equal to contract balance)");

			var hackerContractAddr = await transactionChecker.CheckTransactionAndFindHackerContractAddr(transaction, contractAddr, flags.First().sum);
			if(hackerContractAddr ==  null)
				throw new HttpException((int)HttpStatusCode.Unauthorized,
					"contract does not look being hacked (your transaction should show stealing coins to single recipient addr and amount not less than we deposited)");

			var hackerContractOwnerIp = await transactionChecker.FindHackerContractOwnerIp(hackerContractAddr);
			if(hackerContractOwnerIp == null || !IsSameTeam(requestIp, hackerContractOwnerIp))
			{
				throw new HttpException((int)HttpStatusCode.Unauthorized,
					$"contract looks hacked by somebody else ({hackerContractOwnerIp}), not by your team, your ip: {requestIp}");
			}

			foreach(var flagData in flags)
			{
				flagData.hackerIp = requestIp;
				stateManager.Insert(flagData);
			}
			await context.WriteStringAsync(flagsString);
		}

		const string bankContractAbiFilepath = "contracts/bank.abi.json";
		const string bankAttackerContractAbiFilepath = "contracts/bankattacker.abi.json";

		private static string GetNormalizedTeamSubnetFromIp(string ip)
		{
			if(ip == null)
				return null;

			int idx;
			if((idx = ip.LastIndexOf(".", StringComparison.Ordinal)) == -1)
				return null;

			var subnet = ip.Substring(0, idx);
			return subnet.Replace("10.8", "10.6");//FUCK YEAH, ugly shit to save teams, posting requests from their router
		}

		private static bool IsSameTeam(string ipA, string ipB)
		{
			if(ipA == ipB)
				return true;
			return GetNormalizedTeamSubnetFromIp(ipA).Equals(GetNormalizedTeamSubnetFromIp(ipB), StringComparison.Ordinal);
		}

		private static async Task CheckFlagCallback(HttpListenerContext context)
		{
			var flag = context.Request.QueryString["flag"];
			var contractAddr = context.Request.QueryString["contractAddr"]?.ToLowerInvariant();
			if(flag == null || contractAddr == null)
				throw new HttpException((int)HttpStatusCode.BadRequest, "expected params 'flag', 'contractAddr'");

			var flagsData = stateManager.FindByContractAddr(contractAddr);
			FlagData flagData;
			if(flagsData == null || (flagData = flagsData.FirstOrDefault(fd => flag == fd.flag)) == null)
				throw new HttpException((int)HttpStatusCode.NotFound, $"can't find flag for provided params flag '{flag}', contractAddr '{contractAddr}'");

			if(flagData.hackerIp != null)
				await context.WriteStringAsync("stolen");
		}

		const string putFlagHttpPath = "/putFlag_C6EDEE7179BD4E2887A5887901F23060";
		const string checkFlagHttpPath = "/checkFlag_C6EDEE7179BD4E2887A5887901F23060";
		const string checkTransactionHttpPath = "/checkTransaction";
		const string checkTeamHttpPath = "/checkTeam";

		private const int port = 14474;

		private static StateManager stateManager;
		private static TransactionChecker transactionChecker;

		private static readonly ILog log = LogManager.GetLogger(typeof(Program));
		private static TeamsChecker teamsChecker;
	}
}
