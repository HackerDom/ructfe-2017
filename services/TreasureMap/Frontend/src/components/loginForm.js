import serialize from "form-serialize";
import { login } from "../store/actions";
import { bindActionCreators } from "redux";
import store from "../store";
const loginAction = bindActionCreators(login, store.dispatch);
export default user => {
  let wrapper;
  if (document.querySelector(".userForm")) {
    wrapper = document.querySelector(".userForm");
  } else {
    wrapper = document.createElement("form");
    document.querySelector("body").appendChild(wrapper);
    const login = document.createElement("input");
    const pass = document.createElement("input");
    const btn = document.createElement("input");
    btn.type = "submit";
    btn.textContent = "enter";
    login.name = "user";
    login.placeholder = "login";
    pass.name = "password";
    pass.placeholder = "password";
    wrapper.appendChild(login);
    wrapper.appendChild(pass);
    wrapper.appendChild(btn);
    wrapper.classList.add("userForm");
    wrapper.addEventListener("submit", async e => {
      const { user, password } = serialize(e.target, {
        hash: true,
        empty: true
      });
      loginAction(user, password);
      e.preventDefault();
      return false;
    });
  }

  if (user) {
    wrapper.innerText = "";
  } else {
    return wrapper;
  }
};
