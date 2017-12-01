using System.Collections.Generic;
using System.Linq;
using System.Net;
using System.Net.Http;
using System.Threading.Tasks;
using TreasureMap.Db;
using TreasureMap.Handlers.Helpers;
using TreasureMap.Handlers.Models;
using TreasureMap.Http;
using TreasureMap.PathFinders;
using TreasureMap.Utils;

namespace TreasureMap.Handlers
{
	public class ShortestPathHandler : NeedAuthorizeHandler
	{
		public static readonly BaseHandler Instance = new ShortestPathHandler();

		public override IEnumerable<HttpMethod> Methods => new[] {HttpMethod.Post};
		public override string Path => "/api/path";

		private const int MaxRequest = 10000;

		protected override async Task HandleInternal(HttpListenerContext context, string login)
		{
			var request = await JsonHelper.TryParseJsonAsync<PathRequest>(context.Request.InputStream).ConfigureAwait(false);

			if (request.Inner != null && request.Inner.Count > MaxRequest)
			{
				context.Response.StatusCode = (int) HttpStatusCode.RequestEntityTooLarge;
				return;
			}

			if (!IsCorrectPoint(request.Start) || !IsCorrectPoint(request.Finish))
			{
				context.Response.StatusCode = (int)HttpStatusCode.BadRequest;
				return;
			}

			var inner = request.Inner?
				.Select(PointHolder.GetPoint)
				.WhereNotNull()
				.Select(point => new DrawPoint {X = point.X, Y = point.Y})
				.Distinct()
				.ToList();

			var points = PathFinder.Find(request.Start, inner, request.Finish);
			var path = PathDrawer.Draw(points);

			await context.Response.WriteObjectAsync(path).ConfigureAwait(false);
		}


		private static bool IsCorrectPoint(DrawPoint point)
			=> point != null && AddPointHandler.IsCorrentCoordinate(point.X) && AddPointHandler.IsCorrentCoordinate(point.Y);
	}
}