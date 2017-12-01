using System;
using System.Runtime.Serialization;

namespace TreasureMap.Handlers.Models
{
	[DataContract(Namespace = "")]
	public class DrawPoint : IEquatable<DrawPoint>
	{
		[DataMember(Name = "x")] public string X;
		[DataMember(Name = "y")] public string Y;

		public static int GetDistance(DrawPoint p1, DrawPoint p2)
			=> GetDistance(p1.X, p2.X) + GetDistance(p1.Y, p2.Y);

		private static int GetDistance(string x1, string x2)
			=> Math.Abs(ToInt(x1) - ToInt(x2));

		private static int ToInt(string s)
			=> (s[0] - ' ') * 94 + (s.Length < 2 ? 0 : s[1] - ' ');

		public bool Equals(DrawPoint other)
		{
			if (ReferenceEquals(null, other)) return false;
			if (ReferenceEquals(this, other)) return true;
			return string.Equals(X, other.X) && string.Equals(Y, other.Y);
		}

		public override bool Equals(object obj)
		{
			if (ReferenceEquals(null, obj)) return false;
			if (ReferenceEquals(this, obj)) return true;
			if (obj.GetType() != this.GetType()) return false;
			return Equals((DrawPoint) obj);
		}

		public override int GetHashCode()
		{
			unchecked
			{
				return ((X != null ? X.GetHashCode() : 0) * 397) ^ (Y != null ? Y.GetHashCode() : 0);
			}
		}

		public static bool operator ==(DrawPoint left, DrawPoint right)
		{
			return Equals(left, right);
		}

		public static bool operator !=(DrawPoint left, DrawPoint right)
		{
			return !Equals(left, right);
		}
	}
}