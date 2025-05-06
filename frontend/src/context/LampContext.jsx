// 📁 src/context/LampContext.jsx
import { createContext, useContext, useState, useEffect } from 'react';
import io from 'socket.io-client';

const socket = io('http://localhost:5050', {
  transports: ['websocket'],
  withCredentials: false,
});

const LampContext = createContext();

export function LampProvider({ children }) {
  const [ledStates, setLedStates] = useState({});

  useEffect(() => {
    socket.on('connect', () => {
      console.log('✅ Socket 연결됨');
    });

    socket.on('disconnect', () => {
      console.warn('⚠️ Socket 연결 끊김');
    });

    socket.on('device_status_update', (data) => {
      console.log('📥 수신됨 (device_status_update):', data);
      setLedStates((prev) => ({
        ...prev,
        [data.device]: {
          status: data.status,
          brightness: data.brightness,
        },
      }));
    });

    return () => {
      socket.off('device_status_update');
      socket.off('connect');
      socket.off('disconnect');
    };
  }, []);

  return (
    <LampContext.Provider value={{ ledStates, socket }}>
      {children}
    </LampContext.Provider>
  );
}

export function useLamp() {
  return useContext(LampContext);
}
