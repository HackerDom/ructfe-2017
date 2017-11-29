using System.Configuration;

namespace BlackMarket
{
	class Settings
	{
		public static string ParityRpcUrl => ConfigurationManager.AppSettings["parityRpcUrl"];
	}
}
