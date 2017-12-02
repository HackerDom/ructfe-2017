import { xyToCoordinates } from "../services/points";
import map from "../map";
import { lineString, featureCollection, point } from "turf";

const isSameCoordinates = (a, b) => a.x === b.x && a.y === b.y;

const addLayers = () => {
  map
    .addSource("lines", {
      type: "geojson",
      data: featureCollection([point([0, 0])])
    })
    .addLayer({
      id: "lines",
      type: "line",
      source: "lines",
      paint: {
        "line-color": "#b294ff",
        "line-opacity": 0.75,
        "line-width": 5
      }
    })
    .addSource("points", {
      type: "geojson",
      data: featureCollection([point([0, 0])])
    })
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

const toggleLayer = (layer, show) => {
  if (map.getSource(layer)) {
    map.setLayoutProperty(layer, "visibility", show ? "visible" : "none");
  }
};

const setData = (layer, data) => {
  if (map.getSource(layer) && data) {
    map.getSource(layer).setData(data);
  }
};

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
    toggleLayer("lines", false);
    toggleLayer("points", false);
  } else {
    toggleLayer("lines", true);
    toggleLayer("points", true);
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

  setData("lines", lines);
  toggleLayer("lines", lines !== null);
  setData("points", points);
};
