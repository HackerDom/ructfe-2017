import mapboxgl from "mapbox-gl";
import newPointForm from "./components/newPointForm";
import { pathPointSelect } from "./store/actions";
import { lngLatToXY, normalize } from "./services/points";
import store from "./store";
import { bindActionCreators } from "redux";

mapboxgl.accessToken =
  "pk.eyJ1Ijoic2xvZ2dlciIsImEiOiIwNjY2ZmUxMmRlNzJlNmNhMzE1YjFjOGY1MmQ2ZDY0ZSJ9.TDV9k1MtJSGG1srdycqkmA";

const map = new mapboxgl.Map({
  container: document.querySelector(".map"),
  style: "mapbox://styles/mapbox/dark-v9",
  center: [60.6, 56.8],
  zoom: 1
});

map.doubleClickZoom.disable();

map
  .on("click", e => {
    map.clicked = (map.clicked || 0) + 1;
    setTimeout(function() {
      if (map.clicked === 1 && !map.popupIsOpen) {
        map.clicked = 0;
        bindActionCreators(pathPointSelect, store.dispatch)({
          type: "coordinates",
          coordinates: lngLatToXY(e.lngLat)
        });
      }
    }, 300);
  })
  .on("load", () => {
    document.querySelector(".userForm").hidden = false;
    document.querySelector(".pathControll").hidden = false;
  });

map.on("dblclick", e => {
  map.clicked = 0;
  map.popupIsOpen = true;
  const popup = new mapboxgl.Popup().setLngLat(e.lngLat);
  popup
    .setDOMContent(newPointForm(e.lngLat.lat, normalize(e.lngLat.lng), popup))
    .addTo(map)
    .on("close", () => (map.popupIsOpen = false));
});

export default map;
