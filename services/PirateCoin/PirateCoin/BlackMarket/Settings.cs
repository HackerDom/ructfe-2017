using System.Configuration;

namespace BlackMarket
{
	class Settings
	{
		public static string ParityRpcUrl => ConfigurationManager.AppSettings["parityRpcUrl"];
		public static string SourceAccount => ConfigurationManager.AppSettings["sourceAccount"];
		public static string Pass => ConfigurationManager.AppSettings["pass"];
	}
}
