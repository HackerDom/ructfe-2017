import { getCoordinatesFromPoint } from "./points";
import map from "../map";
import { point, featureCollection } from "turf";
import mapboxgl from "mapbox-gl";
import { pathPointSelect } from "../store/actions";
import store from "../store";
import { bindActionCreators } from "redux";

export const addPointToMap = rawPoint => {
  const { id, x, y, message: description } = getCoordinatesFromPoint(rawPoint);

  const data = featureCollection([
    {
      ...point([x, y]),
      properties: {
        description,
        icon: "castle"
      }
    }
  ]);

  if (map.getSource(id)) {
    map.getSource(id).setData(data);
  } else {
    const addLayers = () => {
      map
        .addSource(id, { type: "geojson", data })
        .addLayer({
          id,
          type: "symbol",
          source: id,
          layout: {
            "icon-image": "{icon}-15",
            "icon-allow-overlap": true,
            "text-field": "{title}",
            "text-font": ["Open Sans Semibold", "Arial Unicode MS Bold"],
            "text-offset": [0, 0.6],
            "text-anchor": "top"
          }
        })
        .on("click", id, e => {
          // trigger PATH_POINT_SELECT here
          bindActionCreators(pathPointSelect, store.dispatch)({
            type: "point",
            id
          });
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
