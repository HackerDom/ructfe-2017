using System.Collections.Generic;
using System.Linq;
using TreasureMap.Handlers.Models;

namespace TreasureMap.PathFinders
{
	public class HeuristicPathFinder : IPathFinder
	{

		public const int MaxVertexes = 1000;

		public List<DrawPoint> Find()
		{
			var parents = GetTree();
			var edges = GetEdges(parents);

			var order = Euler(edges);
			var res = new List<DrawPoint>(order.Count);
			// ReSharper disable once LoopCanBeConvertedToQuery
			foreach (var ind in order)
				res.Add(GetPoint(ind));
			return res;
		}

		public HeuristicPathFinder(DrawPoint start, List<DrawPoint> inner, DrawPoint finish)
		{
			this.start = start;
			this.inner = inner;
			this.finish = finish;
		}

		private int[] GetTree()
		{
			var dist = new int[VertexCount];
			var parent = new int[VertexCount];
			var used = new bool[VertexCount];
			parent[0] = int.MaxValue;
			for (var i = 1; i < dist.Length; ++i)
			{
				dist[i] = int.MaxValue;
				parent[i] = int.MaxValue;
			}

			for (var t = 0; t < VertexCount; ++t)
			{
				var current = 0;
				for (var i = 0; i < VertexCount; ++i)
					if (used[current] || !used[i] && dist[current] > dist[i])
						current = i;
				used[current] = true;
				for (var i = 0; i < VertexCount; ++i)
				{
					if (used[i])
						continue;
					var d = DrawPoint.GetDistance(GetPoint(current), GetPoint(i));
					if (d < dist[i])
					{
						dist[i] = d;
						parent[i] = current;
					}
				}
			}

			return parent;
		}

		private List<int>[] GetEdges(IList<int> parents)
		{
			var res = new List<int>[VertexCount];
			for (var i = 0; i < VertexCount; ++i)
				res[i] = new List<int>();
			for (var i = 0; i < VertexCount; ++i)
			{
				if (parents[i] == int.MaxValue)
					continue;
				res[i].Add(parents[i]);
				res[parents[i]].Add(i);
			}
			return res;
		}

		private List<int> Euler(IReadOnlyList<List<int>> edges)
		{
			var was = new bool[VertexCount];
			var order = new List<int>(VertexCount + 1);
			Euler(edges, 0, order, was);
			order.Add(VertexCount + 1);
			return order;
		}

		private static void Euler(IReadOnlyList<List<int>> edges, int v, ICollection<int> result, IList<bool> was)
		{
			while (edges[v].Any())
			{
				var u = edges[v].Last();
				edges[v].RemoveAt(edges[v].Count - 1);
				Euler(edges, u, result, was);
			}

			if (was[v])
				return;

			result.Add(v);
			was[v] = true;
		}

		private DrawPoint GetPoint(int index)
		{
			if (index == 0)
				return start;
			return index <= inner.Count ? inner[index - 1] : finish;
		}

		private int VertexCount => inner.Count + 1;

		private readonly DrawPoint start;
		private readonly List<DrawPoint> inner;
		private readonly DrawPoint finish;
	}
}