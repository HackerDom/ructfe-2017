﻿using System;
using System.Net;

using PirateCoin.Utils;

namespace PirateCoin.http
{
	internal static class HttpContextHelper
	{
		static HttpContextHelper()
		{
			if(!RuntimeHelper.IsMono)
				abort = ReflectionUtils.GetMethodInvoker<HttpListenerContext>("Abort");
			else
			{
				var method = ReflectionUtils.GetFieldMethodInvoker<HttpListenerContext, object>("cnc", "OnTimeout");
				abort = ctx => method(ctx, null);
			}
		}

		public static void AbortConnection(this HttpListenerContext context)
		{
			try
			{
				abort(context);
			}
			catch {}
		}

		public static void Close(this HttpListenerContext context, int status)
		{
			try
			{
				context.Response.StatusCode = status;
				context.Response.KeepAlive = false;
				context.Response.Close();
			}
			catch {}
		}

		private static readonly Action<HttpListenerContext> abort;
	}
}