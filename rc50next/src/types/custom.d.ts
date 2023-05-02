export interface RC50Data {
    timestamp: Date;
    systemPressure: number;
    systemStatus: boolean;
    temperature: number;
    humidity: number;
    pressureUnit: string;
    ch1Mode: string;
    ch2Mode: string;
    targetPressure: number;
    pressureRange: number;
    lowLevelCount: number;
    lowLevelStatus: string;
    dispenseCount: number;
    ch1Dispensing: boolean;
    pressureStatus: boolean;
    runMode: boolean;
    _id: string;
}

export interface DataContextProps {
    currentPoint: RC50Data;
    setCurrentPoint: (value: RC50Data) => void;
    history: RC50Data[];
    setHistory: any;
    live: boolean;
    setLive: any;
    updateFetched: () => void;
}
