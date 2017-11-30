import serialize from "form-serialize";
import { putNewPoint } from "../services/backend";
import { bindActionCreators } from "redux";
import store from "../store";
import { createPoint } from "../store/actions";
const getFormLine = (title, value) => {
  const wrapper = document.createElement("div");
  const text = document.createElement("span");
  const input = document.createElement("input");
  text.textContent = title + ":";
  input.name = title;
  if (value) {
    input.value = value;
  }
  wrapper.appendChild(text);
  wrapper.appendChild(input);
  return wrapper;
};

const getCheckbox = () => {
  const wrapper = document.createElement("div");
  const text = document.createElement("span");
  const input = document.createElement("input");
  input.type = "checkbox";
  input.name = "public";
  text.textContent = "isPublic: ";
  wrapper.appendChild(text);
  wrapper.appendChild(input);
  return wrapper;
};

const getSubmit = () => {
  const input = document.createElement("input");
  input.type = "submit";
  return input;
};

export default (lat, lng, popup) => {
  const form = document.createElement("form");
  form.action = "#";

  form.appendChild(getFormLine("y", lat));
  form.appendChild(getFormLine("x", lng));
  form.appendChild(getFormLine("message"));
  form.appendChild(getCheckbox());
  form.appendChild(getSubmit());

  form.addEventListener("submit", async e => {
    const data = serialize(e.target, { hash: true, empty: true });
    let id = await putNewPoint(data);
    bindActionCreators(createPoint, store.dispatch)({
      id,
      ...data
    });
    e.preventDefault();
    popup.remove();
    return false;
  });
  return form;
};
