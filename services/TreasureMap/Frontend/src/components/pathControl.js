import { clearPath, buildPath } from "../store/actions";
import { bindActionCreators } from "redux";
import store from "../store";

export default () => {
  document
    .querySelector("#clearPath")
    .addEventListener("click", bindActionCreators(clearPath, store.dispatch));
  document
    .querySelector("#buildPath")
    .addEventListener("click", bindActionCreators(buildPath, store.dispatch));
};
