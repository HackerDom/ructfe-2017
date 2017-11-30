using System.Collections.Generic;
using TreasureMap.Handlers.Models;

namespace TreasureMap.PathFinders
{
	public interface IPathFinder
	{
		List<DrawPoint> Find();
	}
}