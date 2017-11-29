using System.Runtime.Serialization;

namespace TreasureMap.Handlers.Models
{
	[DataContract(Namespace = "")]
	public class Credentials
	{
		[DataMember(Name = "user", Order = 1)] public string Login;
		[DataMember(Name = "password", Order = 1)] public string Password;
	}
}