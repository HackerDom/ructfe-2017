import { handleActions } from "redux-actions";
import * as actions from "../actionsNames";

export default handleActions(
  {
    [actions.PATH_POINT_SELECT]: (state, { payload }) => {
      if (payload.type === "coordinates") {
        return {
          ...state,
          path: [],
          startPoint: state.startPoint ? state.startPoint : payload.coordinates,
          endPoint: state.startPoint ? payload.coordinates : undefined
        };
      } else {
        if (payload.type === "point") {
          return {
            ...state,
            startPoint: state.startPoint ? state.startPoint : payload.point,
            endPoint: state.startPoint ? payload.point : undefined,
            sub: [...state.sub, payload.point.id]
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
