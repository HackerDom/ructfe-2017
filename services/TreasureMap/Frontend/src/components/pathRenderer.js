import { xyToCoordinates } from "../services/points";
import map from "../map";
import { lineString, featureCollection, point } from "turf";

const isSameCoordinates = (a, b) => a.x === b.x && a.y === b.y;

const getPointView = _ => ({
  ...point(xyToCoordinates(_)),
  properties: {
    icon: "circle"
  }
});

const existFilter = item => item !== undefined;

export default ({ startPoint, endPoint, path, sub }, pointsData) => {
  let points = null;
  let lines = null;

  if (!startPoint && !endPoint && !sub.length && !path.length) {
    if (map.getSource("lines")) {
      map.setLayoutProperty("lines", "visibility", "none");
    }
    if (map.getSource("points")) {
      map.setLayoutProperty("points", "visibility", "none");
    }
  } else {
    if (map.getSource("lines") && (sub.length || endPoint)) {
      map.setLayoutProperty("lines", "visibility", "visible");
    }
    if (map.getSource("points") && startPoint) {
      map.setLayoutProperty("points", "visibility", "visible");
    }
  }
  if (path.length) {
    lines = lineString(path.map(xyToCoordinates));
  } else {
    if (startPoint && (endPoint || sub.length)) {
      lines = lineString(
        [
          xyToCoordinates(startPoint),
          ...sub.map(id => xyToCoordinates(pointsData[id])),
          endPoint ? xyToCoordinates(endPoint) : undefined
        ].filter(existFilter)
      );
    }
    if (startPoint) {
      let endPointView = endPoint
        ? sub.some(point => isSameCoordinates(point, endPoint))
          ? undefined
          : getPointView(endPoint)
        : undefined;
      points = featureCollection(
        [getPointView(startPoint), endPointView].filter(existFilter)
      );
    }
  }
  if (map.getSource("lines") || map.getSource("points")) {
    if (lines !== null) {
      map.getSource("lines").setData(lines);
      map.setLayoutProperty("lines", "visibility", "visible");
    } else {
      map.setLayoutProperty("lines", "visibility", "none");
    }
    if (points !== null) {
      map.getSource("points").setData(points);
    }
  } else {
    const addLayers = () => {
      map
        .addSource("lines", { type: "geojson", data: lines })
        .addLayer({
          id: "lines",
          type: "line",
          source: "lines",
          paint: {
            "line-color": "yellow",
            "line-opacity": 0.75,
            "line-width": 5
          }
        })
        .addSource("points", { type: "geojson", data: points })
        .addLayer({
          id: "points",
          type: "symbol",
          source: "points",
          layout: {
            "icon-image": "{icon}-15",
            "icon-allow-overlap": true
          }
        });
    };
    if (map.loaded()) {
      addLayers();
    } else {
      map.on("load", addLayers);
    }
  }
};
