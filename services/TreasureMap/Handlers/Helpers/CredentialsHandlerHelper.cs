using System.Net;
using System.Threading.Tasks;
using TreasureMap.Handlers.Models;
using TreasureMap.Utils;

namespace TreasureMap.Handlers.Helpers
{
	public static class CredentialsHandlerHelper
	{
		public static async Task<Credentials> GetCredentialsAsync(this HttpListenerContext context)
		{
			var credentials = await JsonHelper.TryParseJsonAsync<Credentials>(context.Request.InputStream).ConfigureAwait(false);

			if (credentials != null && credentials.Login.IsSignificant() && credentials.Password.IsSignificant())
				return credentials;

			context.Response.StatusCode = (int)HttpStatusCode.BadRequest;
			return null;
		}
	}
}