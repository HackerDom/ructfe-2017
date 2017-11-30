import { normalize, schema } from "normalizr";

const point = new schema.Entity("point");
const points = new schema.Array(point);

export const fetchData = async () => {
  const data = [
    {
      id: "abc",
      x: "60.594486",
      y: "56.836739",
      message: Date.now().toString(),
      user: "1",
      public: true
    },
    {
      id: "dfe",
      x: "60.594486",
      y: "56.836739",
      message: Date.now().toString(),
      user: "1",
      public: true
    }
  ];
  return normalize(data, points).entities.point;
};

export const putNewPoint = async data => {
  // типа айдишник
  return Date.now().toString();
};
