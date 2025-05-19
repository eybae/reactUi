// 📁 src/pages/Dashboard.jsx
import { useRef, useEffect } from "react";
import L from "leaflet";
import "leaflet/dist/leaflet.css";
import DeviceStatusBar from "../components/DeviceStatusBar";
import { useLamp } from "../context/LampContext";

const DEV_KEYS = [
  "Lamp1",
  "Lamp2",
  "Lamp3",
  "Lamp4",
  "Lamp5",
  "Lamp6",
  "Lamp7",
  "Lamp8",
  "Lamp9",
  "Lamp10",
];

export default function Dashboard() {
  const { ledStates } = useLamp();
  const mapRef = useRef(null);
  const leafletMap = useRef(null);
  const markerRef = useRef(null);

  const anyLampOn = Object.values(ledStates).some((d) => d.status === "on");

  useEffect(() => {
    if (!leafletMap.current && mapRef.current) {
      leafletMap.current = L.map(mapRef.current).setView([37.5665, 126.978], 17);
      L.tileLayer("https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png", {
        attribution: "© OpenStreetMap",
      }).addTo(leafletMap.current);

      markerRef.current = L.marker([37.5665, 126.978], {
        icon: L.icon({
          iconUrl: anyLampOn
            ? "https://maps.google.com/mapfiles/ms/icons/green-dot.png"
            : "https://maps.google.com/mapfiles/ms/icons/red-dot.png",
          iconSize: [32, 32],
        }),
      }).addTo(leafletMap.current);
    } else if (markerRef.current) {
      const iconUrl = anyLampOn
        ? "https://maps.google.com/mapfiles/ms/icons/green-dot.png"
        : "https://maps.google.com/mapfiles/ms/icons/red-dot.png";
      markerRef.current.setIcon(L.icon({ iconUrl, iconSize: [32, 32] }));
    }
  }, [anyLampOn]);

  const streamUrl = `${window.location.protocol}//${window.location.hostname}:5050/stream.mjpg`;

  return (
    <div style={{ display: "flex", flexDirection: "column", gap: "2rem" }}>
      {/* 상태 카드 */}
      <div>
        <h2>Lamp 상태</h2>
        <div style={{ display: "flex", flexWrap: "wrap", gap: "1rem" }}>
          {DEV_KEYS.map((key) => {
            const dev = ledStates[key] || { status: "off", brightness: 0 };
            return (
              <div
                key={key}
                style={{
                  border: "1px solid #ccc",
                  borderRadius: "8px",
                  padding: "1rem",
                  width: "100px",
                  backgroundColor: dev.status === "on" ? "#d1fae5" : "#f3f4f6",
                }}
              >
                <strong>{key}</strong>
                <p>전원: {dev.status}</p>
                <p>밝기: {dev.brightness}</p>
              </div>
            );
          })}
        </div>
      </div>

      {/* 지도 & 카메라 */}
      <div style={{ display: "flex", justifyContent: "space-between", gap: "1rem" }}>
        <div style={{ flex: 1 }}>
          <h3>디바이스 지도</h3>
          <div
            ref={mapRef}
            id="map"
            style={{
              width: "100%",
              height: "480px",
              borderRadius: "8px",
              border: "1px solid #ccc",
            }}
          ></div>
        </div>

        <div style={{ flex: 1 }}>
          <h3>카메라 스트리밍</h3>
          <img
            src={streamUrl}
            alt="카메라 스트리밍"
            style={{
              width: "100%",
              height: "480px",
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
