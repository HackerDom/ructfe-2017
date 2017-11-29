using System.Collections.Generic;
using System.Net;
using System.Net.Http;
using System.Threading.Tasks;
using TreasureMap.Db;
using TreasureMap.Handlers.Helpers;

namespace TreasureMap.Handlers
{
	public class RegisterHandler : BaseHandler
	{
		public static readonly BaseHandler Instanse = new RegisterHandler();

		public override IEnumerable<HttpMethod> Methods => new[] {HttpMethod.Post};
		public override string Path => "/api/register";

		public override async Task Handle(HttpListenerContext context)
		{
			var credentials = await context.GetCredentialsAsync().ConfigureAwait(false);
			if (credentials == null)
				return;

			if (CredentialsHolder.GetUser(credentials.Login) != null)
			{
				context.Response.StatusCode = (int) HttpStatusCode.Conflict;
				return;
			}

			var hash = CredentialsHolder.GetPassHashed(credentials.Login, credentials.Password);
			if (!CredentialsHolder.AddUser(credentials.Login, hash))
			{
				context.Response.StatusCode = (int)HttpStatusCode.Conflict;
				return;
			}

			context.SetLoginCookie(credentials.Login);
		}
	}
}