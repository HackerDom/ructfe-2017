using System.Net;
using System.Threading.Tasks;

namespace TreasureMap.Handlers.Helpers
{
	public abstract class NeedAuthorizeHandler : BaseHandler
	{
		public override async Task Handle(HttpListenerContext context)
		{
			var login = context.GetLogin();
			if (login == null)
			{
				context.Response.StatusCode = (int) HttpStatusCode.Forbidden;
				return;
			}
			await HandleInternal(context, login).ConfigureAwait(false);
		}

		protected abstract Task HandleInternal(HttpListenerContext context, string login);
	}
}