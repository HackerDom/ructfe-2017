import { handleActions } from "redux-actions";
import * as actions from "../actionsNames";

export default handleActions(
  {
    [actions.PATH_POINT_SELECT]: (state, { payload }) => {
      if (payload.type === "coordinates") {
        if (!state.startPoint) {
          return {
            ...state,
            startPoint: payload.coordinates,
            path: []
          };
        } else {
          return {
            ...state,
            endPoint: payload.coordinates
          };
        }
      } else {
        if (payload.type === "point" && state.startPoint) {
          return {
            ...state,
            sub: [...state.sub, payload.id]
          };
        }
      }
      return state;
    },
    [actions.PATH_CLEAR]: () => ({
      startPoint: undefined,
      endPoint: undefined,
      path: [],
      sub: []
    }),
    [actions.PATH_BUILD]: (state, { payload }) => ({
      startPoint: undefined,
      endPoint: undefined,
      sub: [],
      path: payload
    })
  },
  {
    startPoint: undefined,
    endPoint: undefined,
    path: [],
    sub: []
  }
);
