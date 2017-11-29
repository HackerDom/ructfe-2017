using System;
using System.Collections.Generic;
using System.Security.Cryptography;

namespace TreasureMap.Crypto
{
	public class RHHE : HashAlgorithm
	{
		public const string Name = "RHHE";

		private readonly uint[] state;
		private readonly byte[] buffer;
		private long count;
		private readonly uint[] expandbuffer;

		public const int InputBlockLength = 64;
		private const int ExpandSize = 80;

		public override int InputBlockSize => InputBlockLength;
		public override int OutputBlockSize => HashSize / 8;

		public RHHE()
		{
			HashSizeValue = 160;

			state = new uint[HashSizeValue / 8 / 4];
			buffer = new byte[InputBlockLength];
			expandbuffer = new uint[ExpandSize];

			InitializeState();
		}

		public override void Initialize()
		{
			InitializeState();
			Array.Clear(buffer, 0, buffer.Length);
		}

		protected override void HashCore(byte[] array, int offset, int length)
		{
			var bufferLen = (int)(count % InputBlockLength);
			count += length;

			if (bufferLen > 0 && bufferLen + length >= InputBlockLength)
			{
				Array.Copy(array, offset, buffer, bufferLen, InputBlockLength - bufferLen);
				offset += InputBlockLength - bufferLen;
				length -= InputBlockLength - bufferLen;
				HashTranform(expandbuffer, state, buffer);
				bufferLen = 0;
			}

			while (length >= InputBlockLength)
			{
				Array.Copy(array, offset, buffer, 0, InputBlockLength);
				offset += InputBlockLength;
				length -= InputBlockLength;
				HashTranform(expandbuffer, state, buffer);
			}

			if (length > 0)
				Array.Copy(array, offset, buffer, bufferLen, length);
		}

		protected override byte[] HashFinal()
		{
			var padSize = InputBlockLength - (int) (count % InputBlockLength) - 8;
			if (padSize <= 0)
				padSize += InputBlockLength;
			var pad = new byte[padSize];
			pad[0] = 0x80;
			HashCore(pad, 0, padSize);
			HashCore(BitConverter.GetBytes(count), 0, 8);

			var result = new byte[HashSizeValue / 8];
			for(var i = 0; i < HashSizeValue / 8; i += 4)
				Array.Copy(BitConverter.GetBytes(state[i / 4]), 0, result, i, 4);
			return result;
		}

		private void InitializeState()
		{
			count = 0;

			state[0] = 0x758b5c38u;
			state[1] = 0x111138b2u;
			state[2] = 0x1676e3c6u;
			state[3] = 0x64a6d960u;
			state[4] = 0x236b3098u;
		}

		private static void HashTranform(IList<uint> expandbuffer, IList<uint> state, byte[] buffer)
		{
			for (var i = 0; i < InputBlockLength; i += 4)
				expandbuffer[i / 4] = BitConverter.ToUInt32(buffer, i);

			HashExpand(expandbuffer);

			var a = state[0];
			var b = state[1];
			var c = state[2];
			var d = state[3];
			var e = state[4];

			for (var i = 0; i < 20; ++i)
			{
				var tmp = a ^ expandbuffer[i];
				a = Rol(b, 5) ^ e ^ ~c;
				b = tmp ^ ~d;
				c = ~d;
				d = ~Rol(e, 17);
				e = tmp;
			}

			for (var i = 20; i < 40; ++i)
			{
				var tmp = Rol(a ^ c ^ e, 7) ^ expandbuffer[i];
				a = b;
				b = Rol(c, 3);
				c = d;
				d = ~e;
				e = tmp;
			}

			for (var i = 40; i < 60; ++i)
			{
				var tmp = a ^ expandbuffer[i];
				a = Rol(b, 5) ^ e ^ ~c;
				b = tmp ^ ~d;
				c = ~d;
				d = ~Rol(e, 17);
				e = tmp;
			}

			for (var i = 20; i < 40; ++i)
			{
				var tmp = Rol(a ^ c ^ e, 3) ^ expandbuffer[i];
				a = ~b ^ e;
				b = Rol(c, 7);
				c = d;
				d = ~e;
				e = tmp;
			}

			state[0] = a;
			state[1] = b;
			state[2] = c;
			state[3] = d;
			state[4] = e;
		}

		private static void HashExpand(IList<uint> expandbuffer)
		{
			for (var i = InputBlockLength / 4; i < ExpandSize; ++i)
			{
				var tmp = expandbuffer[i - 2] ^ expandbuffer[i - 9] ^ expandbuffer[i - 13] ^ expandbuffer[i - 16];
				expandbuffer[i] = Rol(tmp, 3);
			}
		}

		private static uint Rol(uint x, int sh)
		{
			sh = sh % 32;
			return (x << sh) | (x >> (32 - sh));
		}
	}
}