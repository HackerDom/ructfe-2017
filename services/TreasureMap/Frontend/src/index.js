import "babel-core/register";
import "babel-polyfill";

import "./index.css";
import "mapbox-gl/dist/mapbox-gl.css";
import map from "./map";

import loginForm from "./components/updateLoginForm";
import path from "./components/pathRenderer";
import renderPoint from "./components/pointsRenderer";
import pathControlInit from "./components/pathControl";
import store from "./store";

import { dataFetched } from "./store/actions";
import { fetchData as fetchDataService } from "./services/backend";

window.updatePeriod = 60;

export const fetchData = async () => {
  let res = await fetchDataService();
  if (res) {
    store.dispatch(dataFetched(res));
  }
  return true;
};

const updateDataCycle = async () => {
  await fetchData();
  setTimeout(updateDataCycle, 1000 * updatePeriod);
};

updateDataCycle();
let prevUser = store.getState().user;
loginForm(prevUser);
pathControlInit();

store.subscribe(() => {
  const state = store.getState();
  renderPoint(state.points);
  // Object.entries(state.points).map(([_, point]) => {
  //   addPointToMap(point);
  // });
  if (prevUser !== state.user) {
    fetchData();
    prevUser = state.user;
  }
  loginForm(state.user);
  path(state.path, state.points);
});
