using System.Collections.Generic;
using System.Linq;
using TreasureMap.Handlers.Models;

namespace TreasureMap.PathFinders
{
	public class FastPathFinder : IPathFinder
	{
		private readonly DrawPoint start;
		private readonly List<DrawPoint> inner;
		private readonly DrawPoint finish;

		public FastPathFinder(DrawPoint start, List<DrawPoint> inner, DrawPoint finish)
		{
			this.start = start;
			this.inner = inner;
			this.finish = finish;
		}

		public List<DrawPoint> Find()
		{
			var pointGroups = inner.GroupBy(point => point.X).OrderBy(g => g.Key).Select(g => g.OrderBy(point => point.Y));
			if (string.CompareOrdinal(start.X, finish.X) > 0)
				pointGroups = pointGroups.Reverse();
			var res = new List<DrawPoint>(inner.Count + 2) {start};

			foreach (var group in pointGroups)
			{
				var g = group.ToList();
				if (g.Count == 1)
				{
					res.Add(g.First());
					continue;
				}

				if (DrawPoint.GetDistance(res.Last(), g.First()) > DrawPoint.GetDistance(res.Last(), g.Last()))
					g.Reverse();
				res.AddRange(g);
			}

			res.Add(finish);
			return res;
		}
	}
}