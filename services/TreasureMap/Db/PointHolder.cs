using System;
using System.Collections.Concurrent;
using System.Collections.Generic;
using System.Linq;
using System.Threading;
using TreasureMap.Db.Helpers;
using TreasureMap.Db.Models;
using TreasureMap.Utils;

namespace TreasureMap.Db
{
	public static class PointHolder
	{
		private static long currentId;
		private static readonly ConcurrentDictionary<string, Point> DataBase = new ConcurrentDictionary<string, Point>();
		private static readonly ConcurrentBag<string> Publics = new ConcurrentBag<string>();
		private static readonly ConcurrentDictionary<string, HashSet<string>> PerUser = new ConcurrentDictionary<string, HashSet<string>>();
		private static Action<Point, string> onAdd;

		public static void Init(string path, int sleep, int ttl, Action<Point, string> _onAdd)
		{
			var deadline = DateTime.UtcNow.AddMilliseconds(-ttl);
			DataLoader.Load<Point>(path, point =>
			{
				if (point.Dt >= deadline)
					AddIntenal(point);
			});

			onAdd = _onAdd;
			DataBase.ForEach(pair => currentId = Math.Max(currentId, long.Parse(pair.Value.Id)));

			new PeriodicSaver<Point>(path, sleep, () =>
			{
				var dl = DateTime.UtcNow.AddMilliseconds(-ttl);
				return DataBase.Select(pair => pair.Value).Where(point => point.Dt >= dl);
			});

			var gc = new Thread(() => Gc(ttl, sleep));
			gc.Start();
		}

		public static string Add(Point point)
		{
			point.Id = Interlocked.Increment(ref currentId).ToString();
			point.Dt = DateTime.UtcNow;

			AddIntenal(point);

			onAdd(point, null);

			return point.Id;
		}

		private static void AddIntenal(Point point)
		{
			DataBase.TryAdd(point.Id, point);

			if (point.IsPublic)
				Publics.Add(point.Id);

			PerUser.AddOrUpdateLocked(point.User, point.Id);
		}

		public static IEnumerable<Point> GetPublics()
		{
			return Publics.Select(id => DataBase.GetOrDefault(id)).WhereNotNull();
		}

		public static IEnumerable<Point> GetPoints(string login)
		{
			return PerUser.GetClonedList(login).EmptyIfNull().Select(id => DataBase.GetOrDefault(id)).WhereNotNull();
		}

		public static Point GetPoint(string id)
		{
			return DataBase.GetOrDefault(id);
		}

		private static void Gc(int ttl, int sleep)
		{
			while (true)
			{
				try
				{
					var deadline = DateTime.UtcNow.AddMilliseconds(-ttl);
					DataBase.Where(pair => pair.Value.Dt < deadline).ForEach(pair =>
					{
						if (!DataBase.TryRemove(pair.Key, out Point p))
							return;
						var deleted = new Point {Id = p.Id};
						onAdd(p, deleted.ToJsonString());
					});
				}
				catch
				{
				}
				Thread.Sleep(sleep);
			}
		}
	}
}