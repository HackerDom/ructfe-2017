import serialize from "form-serialize";
import { login } from "../store/actions";
import { bindActionCreators } from "redux";
import store from "../store";
const loginAction = bindActionCreators(login, store.dispatch);
let withHandler = false;

export default user => {
  let wrapper = document.querySelector(".userForm");
  if (!withHandler) {
    wrapper.addEventListener("submit", async e => {
      const { user, password } = serialize(e.target, {
        hash: true,
        empty: true
      });
      loginAction(user, password);
      e.preventDefault();
      return false;
    });
    withHandler = true;
  }

  if (user) {
    wrapper.innerText = "";
  } else {
    return wrapper;
  }
};
