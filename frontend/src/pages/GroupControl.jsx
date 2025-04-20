import { useState } from "react";
import axios from "axios";
import DeviceStatusBar from "../components/DeviceStatusBar";

export default function GroupControl() {
  const [state, setState] = useState("off");
  const [brightness, setBrightness] = useState(1);
  const [onTime, setOnTime] = useState("19:00");
  const [offTime, setOffTime] = useState("05:00");

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
      <DeviceStatusBar />

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
