import { createAction } from "redux-actions";
import * as actions from "./actionsNames";
import {
  login as loginHandler,
  buildPath as buildPathHandler
} from "../services/backend";

export const dataFetched = createAction(actions.DATA_FETCHED);
export const pathPointSelect = createAction(actions.PATH_POINT_SELECT);
export const clearPath = createAction(actions.PATH_CLEAR);
export const createPoint = createAction(actions.CREATE_POINT);
export const removePoint = createAction(actions.REMOVE_POINT);
export const loginOk = createAction(actions.LOGIN);
export const logoutOk = createAction(actions.LOGOUT);

export const login = (user, password) => {
  return async dispatch => {
    let res = await loginHandler(user, password);
    if (res) {
      dispatch(loginOk(user));
    }
  };
};

export const buildPath = () => {
  return async (dispatch, getState) => {
    const { startPoint, endPoint, sub } = getState().path;
    if (startPoint && endPoint) {
      let path = await buildPathHandler(startPoint, endPoint, sub);
      if (path) {
        dispatch(createAction(actions.PATH_BUILD)(path));
      }
    }
  };
};
