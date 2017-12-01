import { stringify } from "querystring";
import { normalize, schema } from "normalizr";

const point = new schema.Entity("point");
const points = new schema.Array(point);

const getParams = {
  credentials: "include"
};

const $get = async url => {
  return fetch(url, getParams);
};

const $post = async (url, data) => {
  return fetch(url, {
    ...getParams,
    method: "post",
    body: JSON.stringify(data)
  });
};

export const fetchData = async () => {
  try {
    let [publics, privates] = await Promise.all([
      $get("/api/publics"),
      $get("/api/points")
    ]);
    let data = [...publics, ...privates];
    return normalize(data, points).entities.point;
  } catch (e) {
    return [];
  }
};

export const putNewPoint = async data => {
  try {
    return await $post("/api/add", data).text();
  } catch (e) {
    return "";
  }
};

export const buildPath = async (start, finish, sub) => {
  try {
    return await $post("/api/path", { start, finish, sub }).json();
  } catch (e) {
    return false;
  }
};

export const login = async (user, password) => {
  try {
    let res = await $post("/api/login", { user, password });
    return !!res.ok;
  } catch (e) {
    return false;
  }
};
