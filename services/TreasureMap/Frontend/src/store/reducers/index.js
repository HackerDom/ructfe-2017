import { combineReducers } from "redux";

import points from "./points";
import user from "./user";
import path from "./path";

export default combineReducers({
  points,
  user,
  path
});
