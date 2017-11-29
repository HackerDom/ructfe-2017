using System.Collections.Generic;
using System.Runtime.Serialization;

namespace BlackMarket
{
	[DataContract]
	class FlagData
	{
		[DataMember(EmitDefaultValue = false)] public string contractAddr;
		[DataMember(EmitDefaultValue = false)] public string flag;
		[DataMember(EmitDefaultValue = false)] public decimal sum;
		[DataMember(EmitDefaultValue = false)] public string hackerIp;

		public class Comparer : IEqualityComparer<FlagData>
		{
			public bool Equals(FlagData x, FlagData y)
			{
				if(x == y)
					return true;
				if(x == null || y == null)
					return false;
				return x.flag == y.flag;
			}

			public int GetHashCode(FlagData obj)
			{
				return obj?.flag?.GetHashCode() ?? 0;
			}
		}
	}
}