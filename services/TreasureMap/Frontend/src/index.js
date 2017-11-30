import "./index.css";
// import WebSocket from "ws";
import "mapbox-gl/dist/mapbox-gl.css";
import map from "./map";
import { bindActionCreators } from "redux";
import store from "./store";

import { fetchData } from "./store/actions";
import { addPointToMap } from "./services/map";

const f = bindActionCreators(fetchData, store.dispatch);

f();

store.subscribe(() => {
  Object.entries(store.getState().points).map(([_, point]) => {
    addPointToMap(point);
  });
});
