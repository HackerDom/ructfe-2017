using System.Runtime.Serialization;

namespace TreasureMap.Handlers.Models
{
	[DataContract(Namespace = "")]
	public class Point
	{
		[DataMember(Name = "id")] public string Id;
		[DataMember(Name = "x")] public string X;
		[DataMember(Name = "y")] public string Y;
		[DataMember(Name = "message")] public string Message;
		[DataMember(Name = "user", EmitDefaultValue = false)] public string User;
		[DataMember(Name = "public")] public bool? IsPublic;
	}
}