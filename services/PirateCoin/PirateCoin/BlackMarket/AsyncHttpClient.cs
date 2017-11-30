using System;
using System.Collections.Specialized;
using System.Diagnostics;
using System.IO;
using System.Net;
using System.Net.Http;
using System.Threading.Tasks;

namespace BlackMarket
{
	internal static class AsyncHttpClient
	{
		public static async Task<HttpResult> DoRequestAsync(Uri uri, string method, string contentType, byte[] data, int timeout = 10000, bool keepAlive = true)
		{
			HttpResult result;
			var stopwatch = new Stopwatch();
			try
			{
				var request = CreateWebRequest(uri, method, keepAlive, contentType);

				stopwatch.Start();
				var task = DoRequestAsync(request, data);
				if(ReferenceEquals(task, await Task.WhenAny(task, Task.Delay(timeout))))
					result = task.Result;
				else
				{
					try { request.Abort(); } catch { }
					result = HttpResult.Timeout;
				}
			}
			catch(Exception e)
			{
				result = HttpResult.Unknown;
				result.Exception = e;
			}

			stopwatch.Stop();
			result.ElapsedTicks = stopwatch.Elapsed.Ticks;

			return result;
		}

		private static async Task<HttpResult> DoRequestAsync(HttpWebRequest request, byte[] data)
		{
			if(data == null)
				request.ContentLength = 0L;
			else
			{
				request.ContentLength = data.Length;
				if(data.Length > 0)
				{
					using(var stream = await request.GetRequestStreamAsync())
						await stream.WriteAsync(data, 0, data.Length);
				}
			}

			using(var response = await request.TryGetResponseAsync())
			{
				if(response == null)
					return HttpResult.Unknown;

				var result = new HttpResult { StatusCode = ((HttpWebResponse)response).StatusCode };
				var stream = response.GetResponseStream();
				var ms = new MemoryStream();
				if(stream != null)
					await stream.CopyToAsync(ms);
				result.ResponseBytes = ms.ToArray();
				result.cookieCollection = ((HttpWebResponse)response).Cookies;
				return result;
			}
		}

		private static async Task<WebResponse> TryGetResponseAsync(this WebRequest request)
		{
			try
			{
				return await request.GetResponseAsync();
			}
			catch(WebException we)
			{
				return we.Response;
			}
		}

		private static HttpWebRequest CreateWebRequest(Uri uri, string method, bool keepAlive, string contentType = null)
		{
			var request = WebRequest.CreateHttp(uri);
			request.Method = method;
			request.KeepAlive = keepAlive;
			request.Proxy = null;
			request.ServicePoint.UseNagleAlgorithm = false;
			request.ServicePoint.ConnectionLimit = 150;
			request.ServicePoint.Expect100Continue = false;
			request.AllowReadStreamBuffering = false;
			request.AllowWriteStreamBuffering = false;
			if(contentType != null)
				request.ContentType = contentType;
			return request;
		}
	}

	internal struct HttpResult
	{
		public HttpStatusCode StatusCode;
		public byte[] ResponseBytes;
		public long ElapsedTicks;

		public Exception Exception;
		public CookieCollection cookieCollection;

		public static readonly HttpResult Timeout = new HttpResult { StatusCode = (HttpStatusCode)499 };
		public static readonly HttpResult Unknown = new HttpResult();
	}
}