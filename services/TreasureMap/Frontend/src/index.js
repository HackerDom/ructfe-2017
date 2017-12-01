import "./index.css";
import "mapbox-gl/dist/mapbox-gl.css";
import map from "./map";

import loginForm from "./components/updateLoginForm";
import path from "./components/pathRenderer";
import pathControlInit from "./components/pathControl";
import store from "./store";

import { dataFetched, fetchData } from "./store/actions";
import { fetchData as fetchDataService } from "./services/backend";
import { addPointToMap } from "./services/map";

window.updatePeriod = 60;

const updateDataCycle = async () => {
  let res = await fetchDataService();
  if (res) {
    store.dispatch(dataFetched(res));
  }
  setTimeout(updateDataCycle, 1000 * updatePeriod);
};

updateDataCycle();
loginForm(store.getState().user);
pathControlInit();

store.subscribe(() => {
  const state = store.getState();
  Object.entries(state.points).map(([_, point]) => {
    addPointToMap(point);
  });
  loginForm(state.user);
  path(state.path, state.points);
});
