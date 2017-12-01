import { createAction } from "redux-actions";
import * as actions from "./actionsNames";
import {
  fetchData as fetchDataService,
  login as loginHandler,
  buildPath as buildPathHandler
} from "../services/backend";

const dataFetched = createAction(actions.DATA_FETCHED);
export const pathPointSelect = createAction(actions.PATH_POINT_SELECT);
export const clearPath = createAction(actions.PATH_CLEAR);
export const createPoint = createAction(actions.CREATE_POINT);
const dataFetchedFail = createAction(actions.DATA_FETCHED + actions.FAIL);
export const loginOk = createAction(actions.LOGIN);

export const fetchData = () => {
  return async dispatch => {
    try {
      dispatch(dataFetched(await fetchDataService()));
    } catch (e) {
      dispatch(dataFetchedFail());
    }
  };
};

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
