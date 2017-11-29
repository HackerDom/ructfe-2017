using System;
using System.Security.Cryptography;
using System.Text;
using TreasureMap.Db;

namespace TreasureMap.Crypto
{
	public class HmacCalculator : HMAC
	{
		private static readonly Encoding Encoding = Encoding.UTF8;

		public static byte[] GetNewSecret()
		{
			var rand = new RNGCryptoServiceProvider();
			var res = new byte[HashImplememtation.InputBlockLength];
			rand.GetNonZeroBytes(res);
			return res;
		}

		public static HmacCalculator CreateNew()
			=> new HmacCalculator
			{
				HashName = HashImplememtation.Name,
				Key = SecretHolder.Secret
			};

		public string ComputeHash(string data)
		{
			var bytes = Encoding.GetBytes(data);
			var res = ComputeHash(bytes);
			return Convert.ToBase64String(res);
		}
	}
}