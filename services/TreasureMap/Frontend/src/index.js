import "babel-core/register";
import "babel-polyfill";
import "mapbox-gl/dist/mapbox-gl.css";

import "./index.css";
import "./map";
import "./services/ws";

import loginForm from "./components/updateLoginForm";
import path from "./components/pathRenderer";
import renderPoint from "./components/pointsRenderer";
import pathControlInit from "./components/pathControl";
import store from "./store";

import { dataFetched } from "./store/actions";
import { fetchData as fetchDataService } from "./services/backend";

// export const fetchData = async () => {
//   let res = await fetchDataService();
//   if (res) {
//     store.dispatch(dataFetched(res));
//   }
//   return true;
// };

// fetchData();
let prevUser = store.getState().user;
loginForm(prevUser);
pathControlInit();

store.subscribe(() => {
  const state = store.getState();
  renderPoint(state.points);
  if (prevUser !== state.user) {
    // fetchData();
    prevUser = state.user;
  }
  loginForm(state.user);
  path(state.path, state.points);
});
