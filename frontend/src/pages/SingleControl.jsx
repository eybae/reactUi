// 📁 src/pages/SingleControl.jsx
import { useState } from "react";
import { useLamp } from "../context/LampContext.jsx";
import axios from "axios";

const DEVICE_LIST = {
  Lamp1: "0080e1150000be14",
  Lamp2: "0080e1150000cda3",
  Lamp3: "0080e1150000c318",
  Lamp4: "0080e1150000ce98",
  Lamp5: "0080e1150000cf78",
  Lamp6: "0080e1150000aaa2",
  Lamp7: "0080e1150000a553",
  Lamp8: "0080e1150000a2f4",
  Lamp9: "0080e11500009f15",
  Lamp10: "0080e11500009bd6",
};

export default function SingleControl() {
  const { ledStates } = useLamp();

  const [lampSettings, setLampSettings] = useState(() => {
    const initial = {};
    for (const [name, devEui] of Object.entries(DEVICE_LIST)) {
      initial[devEui] = {
        state: "off",
        brightness: 1,
        onTime: "00:00",
        offTime: "00:00",
        selected: false,
      };
    }
    return initial;
  });

  const toggleSelect = (devEui) => {
    setLampSettings((prev) => ({
      ...prev,
      [devEui]: {
        ...prev[devEui],
        selected: !prev[devEui].selected,
      },
    }));
  };

  const updateSetting = (devEui, field, value) => {
    setLampSettings((prev) => ({
      ...prev,
      [devEui]: {
        ...prev[devEui],
        [field]: value,
      },
    }));
  };

  const handleSend = async () => {
    for (const [devEui, setting] of Object.entries(lampSettings)) {
      if (!setting.selected) continue;
      try {
        await axios.post("http://localhost:5050/single/control", {
          devEui,
          ...setting,
        });
        console.log("✅ 전송 완료:", devEui);
      } catch (err) {
        console.error("❌ 전송 실패:", devEui, err);
      }
    }
  };

  return (
    <div style={{ padding: "20px", maxWidth: "1000px", margin: "0 auto" }}>
      <h2>💡 개별 제어</h2>

      <div style={{
        display: "flex",
        flexWrap: "wrap",
        gap: "1rem",
        marginBottom: "2rem",
      }}>
        {Object.entries(DEVICE_LIST).map(([name, devEui]) => {
          const actual = ledStates[name] || { status: "off", brightness: 0 };
          const isOn = actual.status === "on";
          return (
            <div
              key={devEui}
              style={{
                width: "100px",
                padding: "0.5rem",
                border: "1px solid #ccc",
                borderRadius: "6px",
                backgroundColor: isOn ? "#d1fae5" : "#f3f4f6",
                textAlign: "center",
              }}
            >
              <strong>{name}</strong>
              <div style={{ fontSize: "0.9rem" }}>전원: {actual.status}</div>
              <div style={{ fontSize: "0.9rem" }}>밝기: {actual.brightness}</div>
            </div>
          );
        })}
      </div>

      {Object.entries(DEVICE_LIST).map(([name, devEui]) => {
        const actual = ledStates[name] || { status: "off", brightness: 0 };
        const setting = lampSettings[devEui];
        const match =
          actual.status === setting.state &&
          actual.brightness === setting.brightness;

        return (
          <div
            key={devEui}
            style={{
              border: "1px solid #ccc",
              padding: "1rem",
              marginBottom: "1rem",
              background: setting.selected ? "#f0f9ff" : "#f9fafb",
            }}
          >
            <label>
              <input
                type="checkbox"
                checked={setting.selected}
                onChange={() => toggleSelect(devEui)}
                style={{ marginRight: "0.5rem" }}
              />
              <strong>{name}</strong>
            </label>

            <div style={{ marginTop: "0.5rem" }}>
              <label>전원:
                <select
                  value={setting.state}
                  onChange={(e) => updateSetting(devEui, "state", e.target.value)}
                >
                  <option value="on">ON</option>
                  <option value="off">OFF</option>
                </select>
              </label>

              <label style={{ marginLeft: "1rem" }}>
                밝기:
                <input
                  type="range"
                  min="1"
                  max="5"
                  value={setting.brightness}
                  onChange={(e) => updateSetting(devEui, "brightness", parseInt(e.target.value))}
                />
                {setting.brightness}
              </label>

              <label style={{ marginLeft: "1rem" }}>
                ON 시간:
                <input
                  type="time"
                  value={setting.onTime}
                  onChange={(e) => updateSetting(devEui, "onTime", e.target.value)}
                />
              </label>

              <label style={{ marginLeft: "1rem" }}>
                OFF 시간:
                <input
                  type="time"
                  value={setting.offTime}
                  onChange={(e) => updateSetting(devEui, "offTime", e.target.value)}
                />
              </label>

              <span
                style={{
                  marginLeft: "1rem",
                  color: match ? "green" : "red",
                  fontWeight: "bold",
                }}
              >
                [{match ? "일치" : "불일치"}]
              </span>
            </div>
          </div>
        );
      })}

      <button
        onClick={handleSend}
        style={{
          padding: "0.75rem 1.5rem",
          backgroundColor: "#2563eb",
          color: "white",
          border: "none",
          borderRadius: "6px",
          fontSize: "1rem",
          cursor: "pointer",
          marginTop: "1rem"
        }}
      >
        🚀 선택된 램프 전송
      </button>
    </div>
  );
}
