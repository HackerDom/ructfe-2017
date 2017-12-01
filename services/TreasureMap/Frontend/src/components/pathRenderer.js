import { decodeCoordinates } from "../services/points";
import map from "../map";
import { lineString } from "turf";

const xyToCoordinates = ({ x, y }) => [
  decodeCoordinates(x),
  decodeCoordinates(y)
];

export default ({ startPoint, endPoint, path, sub }, points) => {
  let data = {};
  if (path.length) {
    data = lineString(path.map(xyToCoordinates));
  } else {
    if (startPoint && (endPoint || sub.length)) {
      data = lineString([
        xyToCoordinates(startPoint),
        ...sub.map(id => xyToCoordinates(points[id])),
        xyToCoordinates(endPoint)
      ]);
    }
  }

  try {
    map.addSource("path", { type: "geojson", data });
    const layer = {
      id: "path",
      type: "line",
      source: "path",
      paint: {
        "line-color": "yellow",
        "line-opacity": 0.75,
        "line-width": 5
      }
    };
    map.addLayer(layer);
  } catch (e) {
    map.getSource("path").setData(data);
  }
};
