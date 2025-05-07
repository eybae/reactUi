// 📁 src/pages/GroupControl.jsx
import { useEffect } from "react";
import axios from "axios";
import { useLamp } from "../context/LampContext.jsx";
import { useLampSettings } from "../context/LampSettingsContext.jsx";

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

export default function GroupControl() {
  const { socket, ledStates } = useLamp();
  const {
    state,
    setState,
    brightness,
    setBrightness,
    onTime,
    setOnTime,
    offTime,
    setOffTime,
  } = useLampSettings();

  useEffect(() => {
    const handleUpdate = (data) => {
      if (data.status !== state || data.brightness !== brightness) {
        alert(`❌ ${data.device} 설정 불일치! (상태:${data.status}, 밝기:${data.brightness})`);
      } else {
        console.log(`✅ ${data.device} 상태 정상 수신됨`);
      }
    };

    socket.on("device_status_update", handleUpdate);
    return () => socket.off("device_status_update", handleUpdate);
  }, [socket, state, brightness]);

  const handleSubmit = async () => {
    try {
      const payload = {
        mode: 0,
        cmd: 1,
        state,
        brightness,
        onTime,
        offTime,
      };

      const res = await axios.post("http://localhost:5050/group/control", payload);
      console.log("✅ 전송 성공:", res.data);
      alert("일괄 제어 명령이 전송되었습니다.");
    } catch (err) {
      console.error("❌ 전송 실패:", err);
      alert("전송 중 오류 발생");
    }
  };

  return (
    <div>
      <div style={{
        display: "flex",
        flexWrap: "wrap",
        gap: "1rem",
        padding: "1rem",
      }}>
        {Object.entries(DEVICE_LIST).map(([name]) => {
          const actual = ledStates[name] || { status: "off", brightness: 0 };
          const isOn = actual.status === "on";
          return (
            <div
              key={name}
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

      <div style={{ padding: "20px", maxWidth: "600px", margin: "0 auto" }}>
        <h2>💡 일괄 제어</h2>

        <div style={{ marginTop: "16px" }}>
          <label>전원 상태:</label>
          <div>
            <button
              onClick={() => setState("on")}
              style={{
                marginRight: "10px",
                backgroundColor: state === "on" ? "#4caf50" : "#ddd",
                color: state === "on" ? "#fff" : "#000",
                padding: "8px 16px",
                border: "none",
                borderRadius: "6px",
                cursor: "pointer",
              }}
            >
              ON
            </button>
            <button
              onClick={() => setState("off")}
              style={{
                backgroundColor: state === "off" ? "#f44336" : "#ddd",
                color: state === "off" ? "#fff" : "#000",
                padding: "8px 16px",
                border: "none",
                borderRadius: "6px",
                cursor: "pointer",
              }}
            >
              OFF
            </button>
          </div>
        </div>

        <div style={{ marginTop: "16px" }}>
          <label>밝기: {brightness}</label>
          <input
            type="range"
            min="1"
            max="5"
            value={brightness}
            onChange={(e) => setBrightness(parseInt(e.target.value))}
            style={{ width: "100%" }}
          />
        </div>

        <div style={{ marginTop: "16px" }}>
          <label>ON 시간:</label>
          <input
            type="time"
            value={onTime}
            onChange={(e) => setOnTime(e.target.value)}
            style={{ marginLeft: "10px" }}
          />
        </div>

        <div style={{ marginTop: "8px" }}>
          <label>OFF 시간:</label>
          <input
            type="time"
            value={offTime}
            onChange={(e) => setOffTime(e.target.value)}
            style={{ marginLeft: "10px" }}
          />
        </div>

        <div style={{ marginTop: "20px" }}>
          <button
            onClick={handleSubmit}
            style={{
              backgroundColor: "#2196f3",
              color: "#fff",
              padding: "10px 20px",
              border: "none",
              borderRadius: "6px",
              cursor: "pointer",
            }}
          >
            명령 전송
          </button>
        </div>
      </div>
    </div>
  );
}
