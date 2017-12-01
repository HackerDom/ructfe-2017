import "./index.css";
// import WebSocket from "ws";
import "mapbox-gl/dist/mapbox-gl.css";
import map from "./map";

import { bindActionCreators } from "redux";
import loginForm from "./components/updateLoginForm";
import path from "./components/pathRenderer";
import pathControlInit from "./components/pathControl";
import store from "./store";

import { fetchData } from "./store/actions";
import { addPointToMap } from "./services/map";

const f = bindActionCreators(fetchData, store.dispatch);
loginForm();
pathControlInit();
f();

store.subscribe(() => {
  const state = store.getState();
  Object.entries(state.points).map(([_, point]) => {
    addPointToMap(point);
  });
  loginForm(state.user);
  path(state.path, state.points);
});
