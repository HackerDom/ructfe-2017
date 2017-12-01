import { getCoordinatesFromPoint } from "./points";
import map from "../map";
import { point, featureCollection } from "turf";
import mapboxgl from "mapbox-gl";
import { pathPointSelect } from "../store/actions";
import store from "../store";
import { bindActionCreators } from "redux";
let allLayers = [];
export const addPointToMap = rawPoint => {
  const { id, x, y, message: description } = getCoordinatesFromPoint(rawPoint);
  // allLayers.map(layer => layer.remove())
  const layer = {
    id,
    type: "symbol",
    source: {
      type: "geojson",
      data: featureCollection([
        {
          ...point([x, y]),
          properties: {
            description,
            icon: "marker"
          }
        }
      ])
    },
    layout: {
      "icon-image": "{icon}-15",
      "icon-allow-overlap": true,
      "text-field": "{title}",
      "text-font": ["Open Sans Semibold", "Arial Unicode MS Bold"],
      "text-offset": [0, 0.6],
      "text-anchor": "top"
    }
  };
  try {
    const addedLayer = map.addLayer(layer).on("click", id, e => {
      map.isOpenNewPointForm = true;
      // trigger PATH_POINT_SELECT here
      bindActionCreators(pathPointSelect, store.dispatch)({
        type: "point",
        id
      });
      if (e.features[0].properties.description) {
        new mapboxgl.Popup()
          .setLngLat(e.features[0].geometry.coordinates)
          .setText(e.features[0].properties.description)
          .addTo(map)
          .on("close", () => (map.isOpenNewPointForm = false));
      } else {
        map.isOpenNewPointForm = false;
      }
    });
    allLayers.push(addedLayer);
  } catch (e) {
    switch (e.message) {
      case "There is already a source with this ID":
        break;
      case "Style is not done loading":
        map.on("load", () => {
          map.isOpenNewPointForm = true;
          const addedLayer = map.addLayer(layer).on("click", id, e => {
            bindActionCreators(pathPointSelect, store.dispatch)({
              type: "point",
              id
            });
            if (e.features[0].properties.description) {
              new mapboxgl.Popup()
                .setLngLat(e.features[0].geometry.coordinates)
                .setText(e.features[0].properties.description)
                .on("close", () => (map.isOpenNewPointForm = false))
                .addTo(map);
            } else {
              map.isOpenNewPointForm = false;
            }
          });
          allLayers.push(addedLayer);
        });
        break;
      default:
        console.error(e);
    }
  }
};
