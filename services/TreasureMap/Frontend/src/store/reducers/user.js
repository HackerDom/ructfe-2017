import { handleActions } from "redux-actions";
import * as actions from "../actionsNames";

export default handleActions(
  {
    [actions.LOGIN]: (state, { payload }) => payload
  },
  ""
);
