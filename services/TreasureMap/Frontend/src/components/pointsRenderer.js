import { xyToCoordinates } from "../services/points";
import map from "../map";
import { featureCollection, point } from "turf";
import { pathPointSelect } from "../store/actions";
import store from "../store";
import * as mapboxgl from "mapbox-gl";

// const isSameCoordinates = (a, b) => a.x === b.x && a.y === b.y;

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
    window.getMap = () => map;
    const addLayers = () => {
      map
        .addSource("allPoints", {
          type: "geojson",
          data,
          cluster: true,
          clusterMaxZoom: 14,
          clusterRadius: 50
        })

        .addLayer({
          id: "allPoints",
          type: "symbol",
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
          // type: "background",
          source: "allPoints",
          filter: ["has", "point_count"],
          paint: {
            // "background-color": {
            "circle-color": {
              property: "point_count",
              type: "interval",
              stops: [[0, "#51bbd6"], [100, "#f1f075"], [750, "#f28cb1"]]
            },
            "circle-radius": {
              property: "point_count",
              type: "interval",
              stops: [[0, 20], [100, 30], [750, 40]]
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
          }
        });
      map.on("click", "allPoints", e => {
        store.dispatch(
          pathPointSelect({
            type: "point",
            id: e.features[0].properties.id
          })
        );
        if (e.features[0].properties.description) {
          map.popupIsOpen = true;
          map.clicked = 0;
          new mapboxgl.Popup()
            .setLngLat(e.features[0].geometry.coordinates)
            .setText(e.features[0].properties.description)
            .addTo(map)
            .on("close", () => (map.popupIsOpen = false));
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
