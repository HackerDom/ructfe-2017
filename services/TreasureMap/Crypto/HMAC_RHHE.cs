using System;
using System.Security.Cryptography;
using System.Text;
using TreasureMap.Db;

namespace TreasureMap.Crypto
{
	public class HMAC_RHHE : HMAC
	{
		private static readonly Encoding Encoding = Encoding.UTF8;

		public static byte[] GetNewSecret()
		{
			var rand = new RNGCryptoServiceProvider();
			var res = new byte[RHHE.InputBlockLength];
			rand.GetNonZeroBytes(res);
			return res;
		}

		public static HMAC_RHHE CreateNew()
			=> new HMAC_RHHE
			{
				HashName = RHHE.Name,
				Key = SecretHolder.Secret
			};

		public string ComputeHash(string data)
		{
			var bytes = Encoding.GetBytes(data);
			var res = ComputeHash(bytes);
			return Convert.ToBase64String(res).Replace('+', '-').Replace('/', '_');
		}
	}
}