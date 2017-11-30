import { createAction } from "redux-actions";
import * as actions from "./actionsNames";
import {
  fetchData as fetchDataService,
  login as loginHandler
} from "../services/backend";

const dataFetched = createAction(actions.DATA_FETCHED);
export const createPoint = createAction(actions.CREATE_POINT);
const dataFetchedFail = createAction(actions.DATA_FETCHED + actions.FAIL);
export const loginOk = createAction(actions.LOGIN);
const loginFail = createAction(actions.LOGIN + actions.FAIL);

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
