using System.Collections.Generic;
using TreasureMap.Handlers;
using TreasureMap.Handlers.Models;
using TreasureMap.Utils;

namespace TreasureMap.PathFinders
{
	public static class PathFinder
	{
		public static List<DrawPoint> Find(DrawPoint start, List<DrawPoint> inner, DrawPoint finish)
		{
			if (inner.IsNullOrEmpty())
				return new List<DrawPoint> { start, finish };

			if (inner.Count == 1)
				return new List<DrawPoint> { start, inner[0], finish };

			var finder = inner.Count <= HeuristicPathFinder.MaxVertexes
				? (IPathFinder) new HeuristicPathFinder(start, inner, finish)
				: new FastPathFinder(start, inner, finish);

			return finder.Find();
		}
	}
}