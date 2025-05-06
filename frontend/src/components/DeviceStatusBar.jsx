import { useLamp } from "../context/LampContext.jsx";
import "./DeviceStatusBar.css";

const DEV_KEYS = ["Lamp1", "Lamp2", "Lamp3", "Lamp4", "Lamp5", "Lamp6", "Lamp7", "Lamp8", "Lamp9", "Lamp10"];

export default function DeviceStatusBar() {
  const { ledStates } = useLamp();

  return (
    <div className="device-bar-container">
      {DEV_KEYS.map((device) => {
        const state = ledStates[device] || { status: "off", brightness: 0 };
        const isOn = state.status === "on";

        return (
          <div key={device} className={`device-box ${isOn ? "on" : "off"}`}>
            <div className="device-title">{device}</div>
            <div className="device-detail">밝기: {state.brightness}</div>
            <div className="device-detail">상태: {state.status}</div>
          </div>
        );
      })}
    </div>
  );
}
