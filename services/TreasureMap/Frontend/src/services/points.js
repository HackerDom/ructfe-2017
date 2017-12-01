export const encodeCoordinates = coord => {
  coord = (coord + 1) / 2;
  let res = "";
  for (let i = 0; i < 16; ++i) {
    coord = coord * 94;
    res += String.fromCharCode(Math.floor(coord) + 33);
    coord %= 1;
  }
  return res;
};

export const decodeCoordinates = coord => {
  let res = 0;
  for (let i = coord.length - 1; i >= 0; --i) {
    res = res / 94 + coord.charCodeAt(i) - 33;
  }
  return res * 2 - 1;
};

export const xyToCoordinates = ({ x, y }) => [
  decodeCoordinates(parseFloat(x) / 180),
  decodeCoordinates(parseFloat(y) / 90)
];

export const getCoordinatesFromPoint = ({ x, y, ...rest }) => ({
  x: decodeCoordinates(x) * 180,
  y: decodeCoordinates(y) * 90,
  ...rest
});
