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
	public class GetPointsHandler : NeedAuthorizeHandler
	{
		public static readonly BaseHandler Instance = new GetPointsHandler();

		public override IEnumerable<HttpMethod> Methods => new[] {HttpMethod.Get};
		public override string Path => "/api/points";

		protected override Task HandleInternal(HttpListenerContext context, string login)
			=> context.Response.WriteObjectAsync(PointHolder.GetPoints(login).Select(PointConverter.Convert).ToList());
	}
}