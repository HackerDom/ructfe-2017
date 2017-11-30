import { getCoordinatesFromPoint } from "./points";
import map from "../map";
import { point } from "turf";
import { featureCollection } from "turf";
import mapboxgl from "mapbox-gl";
export const addPointToMap = rawPoint => {
  const { id, x, y, message } = getCoordinatesFromPoint(rawPoint);
  console.log(map.querySourceFeatures(id));
  if (map.getSource(id)) {
    map.removeSource(id);
  }
  map.on("load", () => {
    try {
      const layer = {
        id,
        type: "symbol",
        source: {
          type: "geojson",
          data: featureCollection([
            {
              ...point([x, y]),
              properties: {
                description: message,
                icon: "marker"
              }
            }
          ])
        },
        layout: {
          "icon-image": "{icon}-15",
          "text-field": "{title}",
          "text-font": ["Open Sans Semibold", "Arial Unicode MS Bold"],
          "text-offset": [0, 0.6],
          "text-anchor": "top"
        }
      };

      map.addLayer(layer).on("click", id, e => {
        new mapboxgl.Popup()
          .setLngLat(e.features[0].geometry.coordinates)
          .setText(e.features[0].properties.description)
          .addTo(map);
      });
    } catch (e) {
      console.error(e);
    }
  });
};
