import { stringify } from "querystring";
import { normalize, schema } from "normalizr";
import { logoutOk } from "../store/actions";
const point = new schema.Entity("point");
const points = new schema.Array(point);
import store from "../store";
const getParams = {
  credentials: "include"
};

const $get = async url => {
  return await fetch(url, getParams);
};

const $post = async (url, data) => {
  return await fetch(url, {
    ...getParams,
    method: "post",
    body: JSON.stringify(data)
  });
};

export const fetchData = async () => {
  try {
    let [publicsRes, privatesRes] = await Promise.all([
      $get("/api/publics"),
      $get("/api/points")
    ]);
    if (publicsRes.status === 403 || privatesRes.status === 403) {
      store.dispatch(logoutOk());
      return false;
    }

    if (publicsRes.ok && privatesRes.ok) {
      let publics = (await publicsRes.json()) || [];
      let privates = (await privatesRes.json()) || [];
      let data = [...publics, ...privates];
      return normalize(data, points).entities.point;
    } else {
      return false;
    }
  } catch (e) {
    return false;
  }
};

export const putNewPoint = async data => {
  try {
    let res = await $post("/api/add", data);
    if (res.status === 403) {
      store.dispatch(logoutOk());
      return "";
    }
    if (res.ok) {
      return await res.text();
    } else {
      return Date.now();
    }
  } catch (e) {
    return "";
  }
};

export const buildPath = async (start, finish, sub) => {
  try {
    let res = await $post("/api/path", { start, finish, sub });
    if (res.status === 403) {
      store.dispatch(logoutOk());
      return false;
    }
    return await res.json();
  } catch (e) {
    return false;
  }
};

export const login = async (user, password) => {
  try {
    let res = await $post("/api/login", { user, password });
    if (res.status === 403) {
      store.dispatch(logoutOk());
      return false;
    }
    return !!res.ok;
  } catch (e) {
    return false;
  }
};
