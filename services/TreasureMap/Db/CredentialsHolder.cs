using System;
using System.Collections.Concurrent;
using System.IO;
using System.Linq;
using System.Text;
using log4net;
using TreasureMap.Crypto;
using TreasureMap.Db.Helpers;
using TreasureMap.Db.Models;
using TreasureMap.Utils;

namespace TreasureMap.Db
{
	public static class CredentialsHolder
	{
		private static readonly ConcurrentDictionary<string, User> DataBase = new ConcurrentDictionary<string, User>();

		public static void Init(string path, int sleep)
		{
			DataLoader.Load<User>(path, user => DataBase.TryAdd(user.Login, user));
			new PeriodicSaver<User>(path, sleep, () => DataBase.Select(pair => pair.Value));
		}

		public static User GetUser(string login)
		{
			return DataBase.GetOrDefault(login);
		}

		public static bool AddUser(string login, string password)
		{
			return DataBase.TryAdd(login, new User {Login = login, Hash = password});
		}

		public static string GetPassHashed(string login, string pass)
		{
			using (var hmac = HmacCalculator.CreateNew())
			{
				return hmac.ComputeHash(login + "|" + pass);
			}
		}
	}
}