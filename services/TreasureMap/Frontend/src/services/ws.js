import { createPoint, removePoint } from "../store/actions";
import store from "../store";

const onMsg = ({ data }) => {
  try {
    let res = JSON.parse(data);
    if (res.user) {
      store.dispatch(createPoint(res));
    } else {
      store.dispatch(removePoint(res));
    }
  } catch (e) {
    console.log("💩");
  }
};

let pointsSocket = new WebSocket(`ws://${location.host}/ws/points`);
let publicSocket = new WebSocket(`ws://${location.host}/ws/publics`);
pointsSocket.onmessage = onMsg;
publicSocket.onmessage = onMsg;
