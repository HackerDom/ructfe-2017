using System.Collections.Generic;
using System.Runtime.Serialization;

namespace TreasureMap.Handlers.Models
{
	[DataContract(Namespace = "")]
	public class PathRequest
	{
		[DataMember(Name = "start")] public DrawPoint Start;
		[DataMember(Name = "finish")] public DrawPoint Finish;
		[DataMember(Name = "sub")] public List<string> Inner;
	}
}