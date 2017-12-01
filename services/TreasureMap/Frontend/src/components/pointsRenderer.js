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
  console.log(points);
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

  console.log(data);

  if (map.getSource("allPoints")) {
    console.log(data);
    map.getSource("allPoints").setData(data);
  } else {
    window.getMap = () => map;
    const addLayers = () => {
      map
        .addSource("allPoints", {
          type: "geojson",
          cluster: true,
          data,
          maxzoom: 100,
          clusterRadius: 0
        })
        .addLayer({
          id: "allPoints",
          type: "symbol",
          source: "allPoints",
          layout: {
            "icon-image": "{icon}-15",
            "icon-allow-overlap": true
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
