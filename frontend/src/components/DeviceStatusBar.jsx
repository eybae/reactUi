import { useEffect, useState } from "react";
import io from "socket.io-client";
import "./DeviceStatusBar.css"; // 👈 스타일 파일 따로 분리 (아래에 작성)

const socket = io("http://localhost:5050");

export default function DeviceStatusBar() {
  const [ledStates, setLedStates] = useState({});

  useEffect(() => {
    socket.on("device_status_update", (data) => {
      setLedStates((prev) => ({
        ...prev,
        [data.device]: {
          status: data.status,
          brightness: data.brightness,
        },
      }));
    });

    return () => socket.off("device_status_update");
  }, []);

  return (
    <div className="device-bar-container">
      {Array.from({ length: 10 }, (_, i) => {
        const key = `LED ${i + 1}`;
        const state = ledStates[key] || { status: "unknown", brightness: "-" };
        const isOn = state.status === "on";

        return (
          <div
            key={key}
            className={`device-box ${isOn ? "on" : "off"}`}
          >
            <div className="device-title">{key}</div>
            <div className="device-detail">밝기: {state.brightness}</div>
            <div className="device-detail">상태: {state.status}</div>
          </div>
        );
      })}
    </div>
  );
}
