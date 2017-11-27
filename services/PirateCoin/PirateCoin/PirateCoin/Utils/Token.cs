using System.Runtime.Serialization;

namespace PirateCoin.Utils
{
	[DataContract(Namespace = "")]
	internal class Token
	{
		[DataMember(Name = "login", Order = 1)] public string Login;
	}
}