using System;
using System.Collections.Generic;
using System.IO;
using System.Linq;
using System.Text;
using System.Threading;
using log4net;
using TreasureMap.Utils;

namespace TreasureMap.Db.Helpers
{
	public class PeriodicSaver<T>
	{
		public PeriodicSaver(string path, int sleep, Func<IEnumerable<T>> getter)
		{
			path = Path.Combine(AppDomain.CurrentDomain.BaseDirectory, path);
			var worker = new Thread(() => Save(path, sleep, getter));
			worker.Start();
		}

		private static void Save(string path, int sleep, Func<IEnumerable<T>> getter)
		{
			while (true)
			{
				try
				{
					File.WriteAllLines(path + ".tmp", getter().Select(user => user.ToJsonString()), Encoding);
					if (File.Exists(path))
						File.Delete(path);
					File.Move(path + ".tmp", path);
				}
				catch (Exception ex)
				{
					Log.Warn($"Exception while saving file '{path}'", ex);
				}
				Thread.Sleep(sleep);
			}
		}

		private static readonly Encoding Encoding = Encoding.UTF8;
		private static readonly ILog Log = LogManager.GetLogger(typeof(PeriodicSaver<T>));
	}
}