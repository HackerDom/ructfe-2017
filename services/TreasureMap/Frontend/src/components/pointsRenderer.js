import { xyToCoordinates } from "../services/points";
import map from "../map";
import { featureCollection, point } from "turf";
import { pathPointSelect } from "../store/actions";
import store from "../store";
import * as mapboxgl from "mapbox-gl";

let hiddenData;

const addLayers = () => {
  map
    .addSource("allPoints", {
      type: "geojson",
      data: hiddenData ? hiddenData : featureCollection([point([0, 0])]),
      cluster: true,
      clusterMaxZoom: 14,
      clusterRadius: 50
    })
    .addLayer({
      id: "allPoints",
      type: "symbol",
      data: featureCollection([point([0, 0])]),
      source: "allPoints",
      filter: ["!has", "point_count"],
      layout: {
        "icon-image": "{icon}-15",
        "icon-allow-overlap": true
      }
    })
    .addLayer({
      id: "allPointsCluster",
      type: "circle",
      source: "allPoints",
      filter: ["has", "point_count"],
      paint: {
        "circle-opacity": 0.5,
        "circle-color": {
          property: "point_count",
          type: "interval",
          stops: [
            [0, "#b294ff"],
            [5, "#57e6e6"],
            [10, "#51bbd6"],
            [20, "#f1f075"],
            [50, "#f28cb1"]
          ]
        },
        "circle-radius": {
          property: "point_count",
          type: "interval",
          stops: [[0, 20], [5, 25], [10, 30], [20, 35], [50, 40]]
        }
      }
    })
    .addLayer({
      id: "cluster-count",
      type: "symbol",
      source: "allPoints",
      filter: ["has", "point_count"],
      layout: {
        "icon-image": "castle-15",
        "icon-allow-overlap": true,
        "icon-offset": [6, 0],
        "text-offset": [-0.6, 0],
        "icon-anchor": "center",
        "text-anchor": "center",
        "text-field": "{point_count_abbreviated}",
        "text-font": ["Arial Unicode MS Bold"],

        "text-size": 12
      },
      paint: {
        "text-color": "white"
      }
    });

  let popup = new mapboxgl.Popup();
  map
    .on("click", "allPoints", e => {
      store.dispatch(
        pathPointSelect({
          type: "point",
          point: store.getState().points[e.features[0].properties.id]
        })
      );
    })
    .on("mouseenter", "allPoints", e => {
      if (e.features[0].properties.description) {
        popup
          .setLngLat(e.features[0].geometry.coordinates)
          .setText(e.features[0].properties.description)
          .addTo(map);
      }
    })
    .on("mouseleave", "allPoints", function() {
      popup.remove();
    });
};
if (map.loaded()) {
  addLayers();
} else {
  map.on("load", addLayers);
}

const getPointView = _ => ({
  ...point(xyToCoordinates(_)),
  properties: {
    id: _.id,
    description: _.message,
    icon: "castle"
  }
});

const existFilter = item => item !== undefined;

export default points => {
  if (!Object.keys(points).length) {
    return;
  }

  let data = featureCollection(
    Object.entries(points)
      .map(([_, point]) => {
        return getPointView(point);
      })
      .filter(existFilter)
  );
  if (map.getSource("allPoints")) {
    map.getSource("allPoints").setData(data);
  } else {
    hiddenData = data;
  }
};
