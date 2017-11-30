using System;
using System.IO;
using TreasureMap.Crypto;

namespace TreasureMap.Db
{
	public static class SecretHolder
	{
		public static byte[] Secret { get; private set; }

		public static void Init(string path)
		{
			path = Path.Combine(AppDomain.CurrentDomain.BaseDirectory, path);
			if (!File.Exists(path))
			{
				Secret = HMAC_RHHE.GetNewSecret();
				File.WriteAllBytes(path, Secret);
			}
			else
				Secret = File.ReadAllBytes(path);
		}
	}
}