using System.Collections.Generic;
using System.Net;
using System.Net.Http;
using System.Threading.Tasks;
using TreasureMap.Db;
using TreasureMap.Handlers.Helpers;

namespace TreasureMap.Handlers
{
	public class LoginHandler : BaseHandler
	{
		public static readonly BaseHandler Instance = new LoginHandler();

		public override IEnumerable<HttpMethod> Methods => new[] {HttpMethod.Post};
		public override string Path => "/api/login";

		public override async Task Handle(HttpListenerContext context)
		{
			var credentials = await context.GetCredentialsAsync().ConfigureAwait(false);
			if (credentials == null)
				return;

			var user = CredentialsHolder.GetUser(credentials.Login);
			var hash = CredentialsHolder.GetPassHashed(credentials.Login, credentials.Password);
			if (user == null)
			{
				if (!CredentialsHolder.AddUser(credentials.Login, hash))
				{
					context.Response.StatusCode = (int)HttpStatusCode.Conflict;
					return;
				}
				context.SetLoginCookie(credentials.Login);
				return;
			}

			if (user.Hash != hash)
			{
				context.Response.StatusCode = (int) HttpStatusCode.Unauthorized;
				return;
			}

			context.SetLoginCookie(user.Login);
		}
	}
}