import { getCoordinatesFromPoint } from "./points";
import map from "../map";
import { point, featureCollection } from "turf";
import mapboxgl from "mapbox-gl";

export const addPointToMap = rawPoint => {
  const { id, x, y, message: description } = getCoordinatesFromPoint(rawPoint);

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
    map.addLayer(layer).on("click", id, e => {
      if (e.features[0].properties.description) {
        new mapboxgl.Popup()
          .setLngLat(e.features[0].geometry.coordinates)
          .setText(e.features[0].properties.description)
          .addTo(map);
      }
    });
  } catch (e) {
    switch (e.message) {
      case "There is already a source with this ID":
        break;
      case "Style is not done loading":
        map.on("load", () => {
          map.addLayer(layer).on("click", id, e => {
            new mapboxgl.Popup()
              .setLngLat(e.features[0].geometry.coordinates)
              .setText(e.features[0].properties.description)
              .addTo(map);
          });
        });
        break;
      default:
        console.error(e);
    }
  }
};
