import React, { useState } from "react";
import axios from "axios";

const directions = [
  { name: "↑", action: "up" },
  { name: "↓", action: "down" },
  { name: "←", action: "left" },
  { name: "→", action: "right" },
];

const zoomControls = [
  { name: "Zoom In", action: "zoom_in" },
  { name: "Zoom Out", action: "zoom_out" },
];

export default function CameraControl() {
  const [presetId, setPresetId] = useState(1);

  // 현재 접속된 주소에서 호스트(IP 또는 도메인)를 가져와 백엔드 주소 구성
  const backendHost = window.location.hostname;
  const backendPort = 5050;
  const backendUrl = `http://${backendHost}:${backendPort}`;

  const handleControl = async (action) => {
    try {
      await axios.post(`${backendUrl}/ptz/control`, {
        action,
        speed: 3,
      });
    } catch (error) {
      console.error("PTZ 제어 실패:", error);
    }
  };

  const handleMouseDown = (action) => handleControl(action);
  const handleMouseUp = () => handleControl("stop");

  const handleZoomClick = async (action) => {
    await handleControl(action);
    setTimeout(() => handleControl("stop"), 300);
  };

  const handleStorePreset = async () => {
    try {
      await axios.post(`${backendUrl}/ptz/preset/store`, {
        preset_id: presetId,
      });
      alert(`📌 위치 ${presetId} 저장됨`);
    } catch (err) {
      console.error("프리셋 저장 실패", err);
    }
  };

  const handleCallOsdMenu = async () => {
      try {
  await axios.post(`${backendUrl}/ptz/osd`);
      alert("📺 OSD 메뉴 호출됨 — 카메라 화면에서 설정 변경하세요.");
        } catch (err) {
  console.error("OSD 호출 실패", err);
    }
  };

  const handleRecallPreset = async () => {
    try {
      await axios.post(`${backendUrl}/ptz/preset/recall`, {
        preset_id: presetId,
      });
    } catch (err) {
      console.error("프리셋 이동 실패", err);
    }
  };

  const handleOsdConfirmIris = async () => {
    await axios.post(`${backendUrl}/ptz/osd/confirm/iris`);
  };
  
    const handleOsdCancel = async () => {
    await axios.post(`${backendUrl}/ptz/osd/cancel`);
  };

  const handleOsdCancelZoom = async () => {
    await axios.post(`${backendUrl}/ptz/osd/cancel/zoom`);
  };
  

  return (
    <div style={{ padding: 20 }}>
      <h2>🎮 카메라 제어</h2>

      {/* 방향 제어 버튼 */}
      <div style={{ display: "flex", flexWrap: "wrap", gap: 10, marginBottom: 20 }}>
        {directions.map((btn) => (
          <button
            key={btn.action}
            onMouseDown={() => handleMouseDown(btn.action)}
            onMouseUp={handleMouseUp}
            style={{
              padding: "10px 20px",
              fontSize: 16,
              borderRadius: 8,
              backgroundColor: "#222",
              color: "#fff",
              border: "1px solid #888",
              cursor: "pointer",
            }}
          >
            {btn.name}
          </button>
        ))}
      </div>

      {/* 줌 버튼 */}
      <div style={{ display: "flex", gap: 10, marginBottom: 20 }}>
        {zoomControls.map((btn) => (
          <button
            key={btn.action}
            onClick={() => handleZoomClick(btn.action)}
            style={{
              padding: "10px 20px",
              fontSize: 16,
              borderRadius: 8,
              backgroundColor: "#444",
              color: "#fff",
              border: "1px solid #888",
              cursor: "pointer",
            }}
          >
            {btn.name}
          </button>
        ))}
        <button
          onClick={() => handleControl("stop")}
          style={{
            padding: "10px 20px",
            fontSize: 16,
            borderRadius: 8,
            backgroundColor: "#888",
            color: "#fff",
            border: "1px solid #ccc",
            cursor: "pointer",
          }}
        >
          🔴 Stop
        </button>
      </div>

      {/* 프리셋 제어 */}
      <div style={{ display: "flex", alignItems: "center", gap: 10, marginBottom: 20 }}>
        <input
          type="number"
          min="1"
          max="10"
          value={presetId}
          onChange={(e) => setPresetId(e.target.value)}
          style={{ padding: 5, fontSize: 16, width: 60 }}
        />
        <button onClick={handleStorePreset}>📌 위치 저장</button>
        <button onClick={handleRecallPreset}>📍 위치 이동</button>
      </div>
      
      <button onClick={handleCallOsdMenu}>📺 OSD 메뉴 호출</button>
      
      <div style={{ display: "flex", gap: 10, marginBottom: 20 }}>
        <button onClick={handleOsdConfirmIris}>✅ 선택 (Iris Open)</button>
        <button onClick={handleOsdCancel}>↩️ 취소 (Iris Close)</button>
        <button onClick={handleOsdCancelZoom}>↩️ 취소 (Zoom Out)</button>
      </div>

      {/* 카메라 스트리밍 */}
      <div style={{ border: "2px solid #ccc", padding: 10, maxWidth: 640 }}>
        <img
          src={`${backendUrl}/stream.mjpg`}
          alt="카메라 스트리밍"
          style={{ width: "100%", borderRadius: 10 }}
        />
      </div>
    </div>
  );
}
