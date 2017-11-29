using TreasureMap.Handlers.Helpers;

namespace TreasureMap.Http
{
	internal static class HttpServerExtentions
	{
		public static HttpServer AddHandler(this HttpServer server, BaseHandler handler)
		{
			foreach (var method in handler.Methods)
				server.AddHandler(method.ToString(), handler.Path, handler.Handle);
			return server;
		}
	}
}