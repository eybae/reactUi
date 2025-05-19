import { io } from "socket.io-client";

const socket = io("http://localhost:5050", {
  transports: ["websocket"],
  reconnection: true,
  reconnectionAttempts: 5,
  reconnectionDelay: 2000,
});

export default socket;

