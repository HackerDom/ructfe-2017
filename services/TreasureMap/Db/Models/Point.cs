using System;
using System.Globalization;
using System.Runtime.Serialization;

namespace TreasureMap.Db.Models
{
	[DataContract(Namespace = "")]
	public class Point
	{
		[DataMember(Name = "id")] public string Id;
		[DataMember(Name = "x")] public string X;
		[DataMember(Name = "y")] public string Y;
		[DataMember(Name = "message")] public string Message;
		[DataMember(Name = "user", EmitDefaultValue = false)] public string User;
		[DataMember(Name = "public")] public bool IsPublic;
		[DataMember(Name = "dt")] public string dt;

		[IgnoreDataMember] public DateTime Dt;

		[OnSerializing]
		public void OnSerializing(StreamingContext context)
		{
			dt = Dt.ToString("s");
		}

		[OnDeserialized]
		public void OnDeserialized(StreamingContext context)
		{
			DateTime.TryParseExact(dt, "s", CultureInfo.InvariantCulture,
				DateTimeStyles.AssumeUniversal | DateTimeStyles.AdjustToUniversal, out Dt);
			dt = null;
		}
	}
}