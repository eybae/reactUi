import { createContext, useContext, useState, useEffect } from 'react';

const LampSettingsContext = createContext();

export function LampSettingsProvider({ children }) {
  const [state, setState] = useState(localStorage.getItem('state') || 'off');
  const [brightness, setBrightness] = useState(parseInt(localStorage.getItem('brightness')) || 1);
  const [onTime, setOnTime] = useState(localStorage.getItem('onTime') || '19:00');
  const [offTime, setOffTime] = useState(localStorage.getItem('offTime') || '05:00');

  useEffect(() => {
    localStorage.setItem('state', state);
    localStorage.setItem('brightness', brightness);
    localStorage.setItem('onTime', onTime);
    localStorage.setItem('offTime', offTime);
  }, [state, brightness, onTime, offTime]);

  return (
    <LampSettingsContext.Provider value={{
      state, setState,
      brightness, setBrightness,
      onTime, setOnTime,
      offTime, setOffTime
    }}>
      {children}
    </LampSettingsContext.Provider>
  );
}

export function useLampSettings() {
  return useContext(LampSettingsContext);
}
