import { handleActions } from "redux-actions";
import * as actions from "../actionsNames";

export default handleActions(
  {
    [actions.DATA_FETCHED]: (state, { payload }) => ({
      ...payload
    }),
    [actions.CREATE_POINT]: (state, { payload }) => ({
      ...state,
      [payload.id]: payload
    }),
    [actions.REMOVE_POINT]: (state, { payload }) => ({
      ...state,
      [payload.id]: undefined
    })
  },
  {}
);
