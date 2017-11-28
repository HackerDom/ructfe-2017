﻿using System.Security.Cryptography;
using System.Text;

namespace PirateCoin.Utils
{
	class CryptUtils
	{
		public static string CalcHash(string str)
		{
			using(var sha1 = SHA1.Create())
			{
				var buff = Encoding.UTF8.GetBytes(str);
				return sha1.TransformFinalBlock(buff, 0, buff.Length).ToHex();
			}
		}
	}
}
