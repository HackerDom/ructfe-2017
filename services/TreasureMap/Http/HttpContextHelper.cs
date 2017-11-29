using System;
using System.Net;
using TreasureMap.Utils;

namespace TreasureMap.Http
{
	internal static class HttpContextHelper
	{
		static HttpContextHelper()
		{
			if(!RuntimeHelper.IsMono)
				Abort = ReflectionUtils.GetMethodInvoker<HttpListenerContext>("Abort");
			else
			{
				var method = ReflectionUtils.GetFieldMethodInvoker<HttpListenerContext, object>("cnc", "OnTimeout");
				Abort = ctx => method(ctx, null);
			}
		}

		public static void AbortConnection(this HttpListenerContext context)
		{
			try
			{
				Abort(context);
			}
			catch
			{
				// ignored
			}
		}

		public static void Close(this HttpListenerContext context, int status)
		{
			try
			{
				context.Response.StatusCode = status;
				context.Response.KeepAlive = false;
				context.Response.Close();
			}
			catch
			{
				// ignored
			}
		}

		private static readonly Action<HttpListenerContext> Abort;
	}
}