using System.Net;
using TreasureMap.Crypto;
using TreasureMap.Http;
using vtortola.WebSockets;

namespace TreasureMap.Handlers.Helpers
{
	public static class SecureCookieHelper
	{
		private const string LoginField = "login";

		public static void SetLoginCookie(this HttpListenerContext context, string login) 
			=> context.SetSignedCookie(LoginField, login);

		public static string GetLogin(this HttpListenerContext context)
		{
			var login = context.Request.Cookies[LoginField]?.Value;
			var sign = context.Request.Cookies[LoginField + ".sig"]?.Value;
			return GetLogin(login, sign);
		}

		public static string GetLogin(this WebSocketHttpRequest request)
		{
			var login = request.Cookies?[LoginField]?.Value;
			var sign = request.Cookies?[LoginField + ".sig"]?.Value;
			return GetLogin(login, sign);
		}

		private static string GetLogin(string login, string sign)
		{
			var cookie = GetCookieString(LoginField, login);
			if (login == null || sign != GetSign(cookie))
				return null;
			return login;
		}

		private static void SetSignedCookie(this HttpListenerContext context, string name, string value)
		{
			var cookie = GetCookieString(name, value);
			context.Response.Headers.Add(HttpResponseHeader.SetCookie, cookie);
			context.SetCookie(name + ".sig", GetSign(cookie), true);
		}

		private static string GetCookieString(string name, string value)
			=> $"{name}={value}; path=/";

		private static string GetSign(string data)
		{
			using (var hmac = HMAC_RHHE.CreateNew())
			{
				return hmac.ComputeHash(data);
			}
		}
	}
}