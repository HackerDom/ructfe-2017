import { stringify } from "querystring";
import { normalize, schema } from "normalizr";

const point = new schema.Entity("point");
const points = new schema.Array(point);

const _fetch = async url => {
  return fetch(url, {
    credentials: "includes"
  });
};

export const fetchData = async () => {
  return Promise.all([_fetch("/api/publics"), _fetch("/api/points")])
    .then(([publics, privates]) => {
      let data = [...publics, ...privates];
      return normalize(data, points).entities.point;
    })
    .then(() => []);
};

export const putNewPoint = async data => {
  // типа айдишник
  return Date.now().toString();
};

export const login = async (user, password) => {
  console.log(user);

  return fetch("/api/login", {
    body: stringify({ user, password }),
    method: "POST",
    credentials: "includes"
  })
    .then(res => {
      return !!res.ok;
    })
    .catch(e => false);
};
