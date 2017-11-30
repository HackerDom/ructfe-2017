import mapboxgl from "mapbox-gl";

mapboxgl.accessToken =
  "pk.eyJ1Ijoic2xvZ2dlciIsImEiOiIwNjY2ZmUxMmRlNzJlNmNhMzE1YjFjOGY1MmQ2ZDY0ZSJ9.TDV9k1MtJSGG1srdycqkmA";

const map = new mapboxgl.Map({
  container: document.querySelector(".map"),
  style: "mapbox://styles/mapbox/dark-v9",
  center: [60.6, 56.8],
  zoom: 10
});

export default map;
