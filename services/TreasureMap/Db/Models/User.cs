using System.Runtime.Serialization;

namespace TreasureMap.Db.Models
{
	[DataContract(Namespace = "")]
	public class User
	{
		[DataMember(Name = "login")] public string Login;
		[DataMember(Name = "hash")] public string Hash;
	}
}