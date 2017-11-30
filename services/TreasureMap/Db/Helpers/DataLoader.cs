using System;
using System.IO;
using System.Linq;
using System.Text;
using log4net;
using TreasureMap.Utils;

namespace TreasureMap.Db.Helpers
{
	public static class DataLoader
	{
		public static void Load<T>(string path, Action<T> add)
		{
			path = Path.Combine(AppDomain.CurrentDomain.BaseDirectory, path);

			if (File.Exists(path))
			{
				var lines = 0;
				File.ReadLines(path, Encoding)
					.Select(s =>
					{
						++lines;
						return s;
					})
					.AsParallel()
					.Select(JsonHelper.ParseJson<T>)
					.ForAll(add);

				Log.Info($"Load {lines} lines");
			}
			else
			{
				Log.Info($"file {path} not found");
			}
		}

		private static readonly Encoding Encoding = Encoding.UTF8;
		private static readonly ILog Log = LogManager.GetLogger(typeof(DataLoader));
	}
}