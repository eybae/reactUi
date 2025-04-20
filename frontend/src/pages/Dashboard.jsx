import { useEffect, useState, useRef } from "react";
import io from "socket.io-client";
import L from "leaflet";
import "leaflet/dist/leaflet.css";

const socket = io("http://localhost:5050");

export default function Dashboard() {
  const [devices, setDevices] = useState(
    Array.from({ length: 10 }, (_, i) => ({
      id: i + 1,
      status: "off",
      brightness: 0,
    }))
  );

  const mapRef = useRef(null);
  const leafletMap = useRef(null);

  useEffect(() => {
    socket.on("device_status_update", (data) => {
      const id = parseInt(data.device.replace("LED ", ""));
      setDevices((prev) =>
        prev.map((dev) =>
          dev.id === id
            ? {
                ...dev,
                status: data.status,
                brightness: data.brightness,
              }
            : dev
        )
      );
    });

    return () => {
      socket.off("device_status_update");
    };
  }, []);

  useEffect(() => {
    if (!leafletMap.current && mapRef.current) {
      leafletMap.current = L.map(mapRef.current).setView(
        [37.5665, 126.978],
        13
      );

      L.tileLayer("https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png", {
        attribution: "© OpenStreetMap",
      }).addTo(leafletMap.current);

      L.marker([37.5665, 126.978], {
        icon: L.icon({
          iconUrl:
            devices.some((d) => d.status === "on")
              ? "https://maps.google.com/mapfiles/ms/icons/green-dot.png"
              : "https://maps.google.com/mapfiles/ms/icons/red-dot.png",
          iconSize: [32, 32],
        }),
      }).addTo(leafletMap.current);
    }
  }, [devices]);

  return (
    <div style={{ display: "flex", flexDirection: "column", gap: "2rem" }}>
      {/* 장비 상태 상단 */}
      <div>
        <h2>Lamp 상태</h2>
        <div style={{ display: "flex", flexWrap: "wrap", gap: "1rem" }}>
          {devices.map((dev) => (
            <div
              key={dev.id}
              style={{
                border: "1px solid #ccc",
                borderRadius: "8px",
                padding: "1rem",
                width: "100px",
                backgroundColor: dev.status === "on" ? "#d1fae5" : "#f3f4f6",
              }}
            >
              <strong>lamp {dev.id}</strong>
              <p>전원: {dev.status}</p>
              <p>밝기: {dev.brightness}</p>
            </div>
          ))}
        </div>
      </div>

      {/* 지도 + 카메라 하단 */}
      <div
        style={{
          display: "flex",
          justifyContent: "space-between",
          gap: "1rem",
          alignItems: "flex-start",
        }}
      >
        {/* 지도 (왼쪽) */}
        <div style={{ flex: 1 }}>
          <h3>디바이스 지도</h3>
          <div
            ref={mapRef}
            id="map"
            style={{
              width: "100%",
              height: "480px",        // 카메라와 동일한 높이로 고정
              borderRadius: "8px",
              border: "1px solid #ccc",
            }}
          ></div>
        </div>

        {/* 카메라 (오른쪽) */}
        <div style={{ flex: 1 }}>
          <h3>카메라 스트리밍</h3>
          <img
            src="http://localhost:5050/stream.mjpg"
            alt="카메라 스트리밍"
            style={{
              width: "100%",
              height: "480px",          // 지도와 동일
              objectFit: "cover",
              border: "1px solid #ccc",
              borderRadius: "8px",
            }}
          />        
        </div>
      </div>
    </div>
  );
}
