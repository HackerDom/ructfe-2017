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
  try {
    let [publics, privates] = await Promise.all([
      _fetch("/api/publics"),
      _fetch("/api/points")
    ]);
    let data = [...publics, ...privates];
    return normalize(data, points).entities.point;
  } catch (e) {
    return [];
  }
};

export const putNewPoint = async data => {
  // типа айдишник
  return Date.now().toString();
};

export const buildPath = async (start, end, sub) => {
  return [start, end];
};

export const login = async (user, password) => {
  try {
    let res = await fetch("/api/login", {
      body: JSON.stringify({ user, password }),
      method: "POST",
      credentials: "includes"
    });
    return !!res.ok;
  } catch (e) {
    return false;
  }
};
