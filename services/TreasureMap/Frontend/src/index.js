import "babel-core/register";
import "babel-polyfill";
import "mapbox-gl/dist/mapbox-gl.css";

import "./index.css";
import "./map";
import connect from "./services/ws";

import loginForm from "./components/updateLoginForm";
import path from "./components/pathRenderer";
import renderPoint from "./components/pointsRenderer";
import pathControlInit from "./components/pathControl";
import store from "./store";

let prevUser = store.getState().user;
if (prevUser) {
  connect();
}
loginForm(prevUser);
pathControlInit();

store.subscribe(() => {
  const state = store.getState();
  renderPoint(state.points);
  if (prevUser !== state.user) {
    connect();
    prevUser = state.user;
  }
  loginForm(state.user);
  path(state.path, state.points);
});
