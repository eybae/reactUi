import React, { useState, useEffect } from "react";
import Papa from "papaparse";

const API_BASE = "http://223.171.34.182:5050"; // Jetson IP 주소로 설정

export default function Logs() {
  const [logFiles, setLogFiles] = useState([]);
  const [selectedFile, setSelectedFile] = useState(null);
  const [csvData, setCsvData] = useState([]);
  const [headers, setHeaders] = useState([]);
  const [error, setError] = useState("");

  useEffect(() => {
    fetch(`${API_BASE}/api/logs/list`)
      .then((res) => res.json())
      .then((files) => setLogFiles(files))
      .catch((err) => {
        console.error("로그 파일 목록 불러오기 실패", err);
        setError("🚫 로그 파일 목록을 가져오는 데 실패했습니다.");
      });
  }, []);

  const handleSelectFile = (e) => {
    const relativePath = e.target.value;
    setSelectedFile(relativePath);
    loadCsvFile(relativePath);
  };

  const loadCsvFile = (relativePath) => {
    setCsvData([]);
    setHeaders([]);
    setError("");

    fetch(`${API_BASE}/api/logs/file?path=${encodeURIComponent(relativePath)}`)
      .then((res) => res.text())
      .then((text) => {
        const result = Papa.parse(text, {
          header: true,
          skipEmptyLines: true,
        });

        if (result.errors.length > 0) {
          console.error("CSV 파싱 오류:", result.errors);
          setError("⚠️ CSV 파일을 읽는 중 오류가 발생했습니다.");
          return;
        }

        if (result.data.length === 0) {
          setError("📭 CSV 파일에 데이터가 없습니다.");
        }

        setCsvData(result.data);
        setHeaders(Object.keys(result.data[0]));
      })
      .catch(() => {
        setError("🚫 CSV 파일을 가져오는 데 실패했습니다.");
      });
  };

  return (
    <div style={{ padding: 20 }}>
      <h2>📊 로그 파일 보기</h2>

      {/* 로그 파일 선택 */}
      <select onChange={handleSelectFile} defaultValue="">
        <option value="" disabled>
          🔽 로그 파일을 선택하세요
        </option>
        {logFiles.map((file, index) => (
          <option key={index} value={file.relative_path}>
            [{file.relative_path.split("/")[0]}] {file.name}
          </option>
        ))}
      </select>

      {/* 다운로드 링크 */}
      {selectedFile && (
        <div style={{ marginTop: 10 }}>
          <a
            href={`${API_BASE}/api/logs/download?path=${encodeURIComponent(selectedFile)}`}
            download
            target="_blank"
            rel="noopener noreferrer"
          >
            📥 이 로그 파일 다운로드
          </a>
        </div>
      )}

      {/* 오류 메시지 */}
      {error && <p style={{ color: "red", marginTop: 10 }}>{error}</p>}

      {/* CSV 테이블 출력 */}
      {headers.length > 0 && csvData.length > 0 && (
        <table
          border="1"
          cellPadding="6"
          style={{
            marginTop: 20,
            width: "100%",
            borderCollapse: "collapse",
            fontSize: "14px",
          }}
        >
          <thead style={{ background: "#f5f5f5" }}>
            <tr>
              {headers.map((header, i) => (
                <th key={i}>{header}</th>
              ))}
            </tr>
          </thead>
          <tbody>
            {csvData.map((row, rowIndex) => (
              <tr key={rowIndex}>
                {headers.map((header, colIndex) => (
                  <td key={colIndex}>{row[header]}</td>
                ))}
              </tr>
            ))}
          </tbody>
        </table>
      )}
    </div>
  );
}
