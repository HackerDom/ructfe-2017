using System.Collections.Generic;
using System.Linq;
using System.Net;
using System.Net.Http;
using System.Threading.Tasks;
using TreasureMap.Db;
using TreasureMap.Handlers.Helpers;
using TreasureMap.Http;

namespace TreasureMap.Handlers
{
	public class GetAllPublicsHandler : NeedAuthorizeHandler
	{
		public static readonly BaseHandler Instance = new GetAllPublicsHandler();

		public override IEnumerable<HttpMethod> Methods => new[] {HttpMethod.Get};
		public override string Path => "/api/publics";

		protected override Task HandleInternal(HttpListenerContext context, string login)
			=> context.Response.WriteObjectAsync(PointHolder.GetPublics().Select(PointConverter.Convert).ToList());
	}
}