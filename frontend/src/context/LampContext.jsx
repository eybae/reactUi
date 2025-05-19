// ✅ LampContext.jsx 개선 버전
import { createContext, useContext, useEffect, useState } from "react";
import axios from "axios";
import socket from "../socket";

const LampContext = createContext();

export function LampProvider({ children }) {
  const [ledStates, setLedStates] = useState({});

  useEffect(() => {
    // 1. 초기 상태 수신
    axios.get("http://localhost:5050/api/devices/status").then((res) => {
      setLedStates(res.data);
      console.log("📥 초기 상태 수신 완료:", res.data);
    });

    // 2. 일반 상태 업데이트 수신
    socket.on("device_status_update", ({ device, status, brightness, pending }) => {
      console.log("📥 상태 업데이트:", device, status, brightness, pending);
      setLedStates((prev) => ({
        ...prev,
        [device]: { status, brightness, pending },
      }));
    });

    // 3. txack 수신 시 선반영 (예: pending 상태 true로 전환)
    socket.on("device_txack", ({ device }) => {
      console.log("📡 txack 수신:", device);
      setLedStates((prev) => ({
        ...prev,
        [device]: {
          ...(prev[device] || { status: "off", brightness: 0 }),
          pending: true,
        },
      }));
    });

    return () => {
      socket.off("device_status_update");
      socket.off("device_txack");
    };
  }, []);

  return (
    <LampContext.Provider value={{ ledStates, setLedStates, socket }}>
      {children}
    </LampContext.Provider>
  );
}

export const useLamp = () => useContext(LampContext);
