import { handleActions } from "redux-actions";
import * as actions from "../actionsNames";

export default handleActions(
  {
    [actions.DATA_FETCHED]: (state, { payload }) => ({
      ...payload
    })
  },
  {}
);
