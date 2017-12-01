using System;
using System.Collections.Concurrent;
using PirateCoin.http;

namespace BlackMarket
{
	public static class AntiFlood
	{
		public static long TotalSeconds(this DateTime dt)
		{
			return dt.Ticks / 10000000;
		}

		public static void CheckFlood(string key, int duration = CheckIntervalDurationSeconds, int count = MaxCountInInterval)
		{
			var checkTime = DateTime.UtcNow.TotalSeconds() / duration;
			Dict.AddOrUpdate(key, new FloodCheck { Time = checkTime, Count = 1 }, (l, check) =>
			{
				lock(check)
				{
					if(check.Time == checkTime)
					{
						if(++check.Count > count)
							throw new HttpException(403, $"Too fast, wait {DateTime.UtcNow.TotalSeconds() - checkTime * duration + 1} sec pls");
					}
					else
					{
						check.Time = checkTime;
						check.Count = 1;
					}
					return check;
				}
			});
		}

		private class FloodCheck
		{
			public long Time;
			public int Count;
		}

		private const int CheckIntervalDurationSeconds = 10;
		private const int MaxCountInInterval = 10;

		private static readonly ConcurrentDictionary<string, FloodCheck> Dict = new ConcurrentDictionary<string, FloodCheck>(StringComparer.InvariantCultureIgnoreCase);
	}
}
