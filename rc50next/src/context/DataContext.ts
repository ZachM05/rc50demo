import { createContext } from "react";
import { DataContextProps } from "../types";

const init = {
    timestamp: new Date(),
    systemPressure: 12.7,
    systemStatus: false,
    temperature: 20.2,
    humidity: 56,
    pressureUnit: "PSI",
    ch1Mode: "Continue",
    ch2Mode: "Continue",
    targetPressure: 13,
    pressureRange: 0.3,
    lowLevelCount: 15,
    dispenseCount: 0,
    lowLevelStatus: "Enabled",
    pressureStatus: false,
    runMode: false,
    _id: "",
    ch1Dispensing: false,
};

const DataContext = createContext<DataContextProps>({
    currentPoint: init,
    setCurrentPoint: () => {},
    history: [],
    setHistory: () => {},
    updateFetched: () => {},
    live: false,
    setLive: () => {},
});

export default DataContext;
