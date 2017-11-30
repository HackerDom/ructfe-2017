using System.Collections.Generic;
using System.Linq;
using TreasureMap.Handlers.Models;
using TreasureMap.Utils;

namespace TreasureMap.Handlers
{
	public static class PathDrawer
	{
		public static List<DrawPoint> Draw(List<DrawPoint> points)
		{
			var path = new List<DrawPoint>(2 * points.Count - 1)
			{
				points.First()
			};

			var verical = true;

			for (var i = 1; i < points.Count; ++i)
			{
				path.Add(verical
					? new DrawPoint {X = path.Last().X, Y = points[i].Y}
					: new DrawPoint {X = points[i].X, Y = path.Last().Y});
				path.Add(points[i]);
				verical = !verical;
			}

			var res = new List<DrawPoint>(2 * points.Count - 1)
			{
				path[0]
			};

			for (var i = 1; i < path.Count; ++i)
			{
				if (path[i] == res.Last())
					continue;
				while (res.Count >= 2 && BadState(res.PreLast(), res.Last(), path[i]))
					res.RemoveAt(res.Count - 1);
				res.Add(path[i]);
			}

			return res;
		}

		private static bool BadState(DrawPoint p1, DrawPoint p2, DrawPoint p3)
			=> Equals(p1.X, p2.X, p3.X) && InOrder(p1.Y, p2.Y, p3.Y)
			   || Equals(p1.Y, p2.Y, p3.Y) && InOrder(p1.X, p2.X, p3.X);

		private static bool Equals(string x, string y, string z)
			=> x == y && y == z;

		private static bool InOrder(string x, string y, string z)
			=> string.CompareOrdinal(x, y) <= 0 && string.CompareOrdinal(y, z) <= 0 || string.CompareOrdinal(x, y) >= 0 && string.CompareOrdinal(y, z) >= 0;
	}
}