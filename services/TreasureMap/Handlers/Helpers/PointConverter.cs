using TreasureMap.Handlers.Models;

namespace TreasureMap.Handlers.Helpers
{
	public static class PointConverter
	{
		public static Point Convert(this Db.Models.Point point)
		{
			return new Point
			{
				Id = point.Id,
				X = point.X,
				Y = point.Y,
				Message = point.Message,
				User = point.User,
				IsPublic =  point.IsPublic
			};
		}
	}
}