using System.Configuration;

namespace BlackMarket
{
	class Settings
	{
		public static string ParityRpcUrl => ConfigurationManager.AppSettings["parityRpcUrl"];
		public static string GethRpcUrl => ConfigurationManager.AppSettings["gethRpcUrl"];
		public static string GethPass => ConfigurationManager.AppSettings["gethPass"];
	}
}
