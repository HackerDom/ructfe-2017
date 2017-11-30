export const encodeCoordinates = coord => coord;
export const decodeCoordinates = coord => coord;

export const getCoordinatesFromPoint = ({ x, y, ...rest }) => ({
  x: decodeCoordinates(x),
  y: decodeCoordinates(y),
  ...rest
});
