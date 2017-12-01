import { handleActions } from "redux-actions";
import cookie from "../../cookie";
import * as actions from "../actionsNames";

export default handleActions(
  {
    [actions.LOGIN]: (state, { payload }) => payload,
    [actions.LOGOUT]: () => ""
  },
  cookie("login") || ""
);
