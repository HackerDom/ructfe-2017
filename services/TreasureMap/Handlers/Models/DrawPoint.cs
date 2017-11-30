using System;
using System.Runtime.Serialization;

namespace TreasureMap.Handlers.Models
{
	[DataContract(Namespace = "")]
	public class DrawPoint
	{
		[DataMember(Name = "x")] public string X;
		[DataMember(Name = "y")] public string Y;

		public static bool operator ==(DrawPoint left, DrawPoint right)
		{
			if (ReferenceEquals(left, null) && ReferenceEquals(right, null))
				return true;
			if (ReferenceEquals(left, null) || ReferenceEquals(right, null))
				return false;
			return left.X == right.X && left.Y == right.Y;
		}

		public static bool operator !=(DrawPoint left, DrawPoint right)
		{
			return !(left == right);
		}

		public static int GetDistance(DrawPoint p1, DrawPoint p2)
			=> GetDistance(p1.X, p2.X) + GetDistance(p1.Y, p2.Y);

		private static int GetDistance(string x1, string x2)
			=> Math.Abs(ToInt(x1) - ToInt(x2));

		private static int ToInt(string s)
			=> (s[0] - ' ') * 94 + (s.Length < 2 ? 0 : s[1] - ' ');

	}
}