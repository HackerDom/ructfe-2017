import { createAction } from "redux-actions";
import * as actions from "./actionsNames";
import { fetchData as fetchDataService } from "../services/backend";

const dataFetched = createAction(actions.DATA_FETCHED);
const dataFetchedFail = createAction(actions.DATA_FETCHED + actions.FAIL);

export const fetchData = () => {
  return async dispatch => {
    try {
      dispatch(dataFetched(await fetchDataService()));
    } catch (e) {
      dispatch(dataFetchedFail());
    }
  };
};
