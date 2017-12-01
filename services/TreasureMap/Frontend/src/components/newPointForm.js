import serialize from "form-serialize";
import { putNewPoint } from "../services/backend";
import { encodeCoordinates } from "../services/points";
import { bindActionCreators } from "redux";
import store from "../store";
import { createPoint } from "../store/actions";

function getFormLine(title, value) {
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
}

const getCheckbox = () => {
  const wrapper = document.createElement("div");
  const text = document.createElement("span");
  const input = document.createElement("input");
  input.type = "checkbox";
  input.name = "public";
  text.textContent = "public: ";
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
  form.appendChild(getFormLine("y", encodeCoordinates(parseFloat(lat) / 90)));
  form.appendChild(getFormLine("x", encodeCoordinates(parseFloat(lng) / 180)));
  form.appendChild(getFormLine("message"));
  form.appendChild(getCheckbox());
  form.appendChild(getSubmit());

  form.addEventListener("submit", async e => {
    e.preventDefault();
    const data = serialize(e.target, {
      hash: true,
      empty: true,
      serializer: (res, key, value) => ({
        ...res,
        [key]: key === "public" ? value === "on" : value
      })
    });
    let id = await putNewPoint(data);
    if (id) {
      bindActionCreators(createPoint, store.dispatch)({
        id,
        ...data
      });
      popup.remove();
    }

    return false;
  });
  return form;
};
