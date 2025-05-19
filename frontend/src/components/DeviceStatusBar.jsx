import React from "react";
import { useLamp } from "../context/LampContext";
import "./DeviceStatusBar.css";

const DeviceStatusBar = ({ id }) => {
  const { ledStates } = useLamp();
  const dev = ledStates[id] ?? { status: "off", brightness: 0 };

  const getStatusColor = () => {
    if (dev.pending) return "bg-yellow-400"; // txack 수신 상태
    if (dev.status === "on") return "bg-green-500";
    if (dev.status === "off") return "bg-gray-400";
    return "bg-gray-300";
  };

  return (
    <div className="device-bar p-2 rounded border shadow">
      <div className="flex justify-between items-center mb-1">
        <span className="font-semibold">{id}</span>
        <span className={`status-dot ${getStatusColor()}`}></span>
      </div>
      <div className="text-sm">
        상태: {dev.status}<br />
        밝기: {dev.brightness}
      </div>
    </div>
  );
};

export default DeviceStatusBar;
