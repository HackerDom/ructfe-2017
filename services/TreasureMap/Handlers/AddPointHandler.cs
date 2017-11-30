using System.Collections.Generic;
using System.Net;
using System.Net.Http;
using System.Threading.Tasks;
using TreasureMap.Db;
using TreasureMap.Handlers.Helpers;
using TreasureMap.Handlers.Models;
using TreasureMap.Http;
using TreasureMap.Utils;

namespace TreasureMap.Handlers
{
	public class AddPointHandler : NeedAuthorizeHandler
	{
		public static readonly BaseHandler Instance = new AddPointHandler();

		public override IEnumerable<HttpMethod> Methods => new[] {HttpMethod.Post};
		public override string Path => "/api/add";

		private const int CoordinateLength = 20;
		private const int MessageLength = 512;

		protected override async Task HandleInternal(HttpListenerContext context, string login)
		{
			var point = await JsonHelper.TryParseJsonAsync<Point>(context.Request.InputStream).ConfigureAwait(false);

			if (!IsCorrectRequest(point))
			{
				context.Response.StatusCode = (int) HttpStatusCode.BadRequest;
				return;
			}

			var p = new Db.Models.Point
			{
				X = point.X,
				Y = point.Y,
				Message = point.Message,
				IsPublic = point.IsPublic != null && point.IsPublic.Value,
				User = login
			};

			var id = PointHolder.Add(p);

			await context.WriteStringAsync(id).ConfigureAwait(false);
		}

		private static bool IsCorrectRequest(Point point)
			=> point != null
			   && IsCorrentCoordinate(point.X)
			   && IsCorrentCoordinate(point.Y)
			   && IsCorrectMessage(point.Message)
			   && point.IsPublic.HasValue
			   && point.User == null
			   && point.Id == null;

		public static bool IsCorrentCoordinate(string str)
			=> str != null && str.Length >= 0 && str.Length <= CoordinateLength && str.AllSymbolsAsciiPrinted();

		private static bool IsCorrectMessage(string message)
			=> message == null || message.Length <= MessageLength;
	}
}