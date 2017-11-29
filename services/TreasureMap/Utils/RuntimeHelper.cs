using System;

namespace TreasureMap.Utils
{
	internal static class RuntimeHelper
	{
		static RuntimeHelper()
		{
			IsMono = Type.GetType("Mono.Runtime") != null;
		}

		public static readonly bool IsMono;
	}
}