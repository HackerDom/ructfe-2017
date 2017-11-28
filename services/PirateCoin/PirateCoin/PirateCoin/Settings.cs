using System.Configuration;

namespace PirateCoin
{
	class Settings
	{
		public static string CoinbasePass => ConfigurationManager.AppSettings["coinbasePass"];
		public static int ContactCreationGas => int.Parse(ConfigurationManager.AppSettings["contactCreationGas"]);
		public static int ContractDeployPeriod => int.Parse(ConfigurationManager.AppSettings["contractDeployPeriod"]);
		public static string GethRpcUrl => ConfigurationManager.AppSettings["gethRpcUrl"];
	}
}
