// import { showNotification, cleanNotifications } from '@mantine/notifications';
// import React, { useEffect, useState } from 'react';
// import DataContext from '../context/DataContext';
// import useLazyFetch from '../hooks/useLazyFetch';
// import { RC50Data } from '../types';

// interface DataContextProviderProps {
//     children: React.ReactNode
// }

// interface Alerts {
//     lowLevel: Date;
//     pressure: Date;
//     rebuild: Date;
// }

// const init = {
//     timestamp: new Date(),
//     systemPressure: 12.7,
//     systemStatus: false,
//     temperature: 20.2,
//     humidity: 56,
//     pressureUnit: "PSI",
//     ch1Mode: 'Continue',
//     ch2Mode: "Continue",
//     targetPressure: 13,
//     pressureRange: 0.3,
//     lowLevelCount: 15,
//     dispenseCount: 0,
//     lowLevelStatus: 'FULL',
//     runMode: false,
//     pressureStatus: false,
//     _id: ''
// }

// const alert = (title: string, message: string) => {
//     showNotification(
//         {
//             title: title,
//             message: message,
//             autoClose: 5000
//         }
//     )
// }

// function DataContextProvider(props: DataContextProviderProps) {

//     const [currentPoint, setCurrentPoint] = useState<RC50Data>(init);
//     const [history, setHistory] = useState<RC50Data[]>([])
//     const [live, setLive] = useState<boolean>(true)
//     const [ws, setWs] = useState<WebSocket | null>(null)
//     const [token, setToken] = useState<any | null>(null)
//     const [alerts, setAlerts] = useState<Alerts | any>({
//         lowLevel: new Date(2020, 1, 1),
//         pressure: new Date(2020, 1, 1),
//         rebuild: new Date(2020, 1, 1)
//     })

//     const updateFetched = () => {
//         makeDataFetch({ url: '/api/mongo' })
//     }

//     const updateData = (point: RC50Data) => {
//         setCurrentPoint(point)
//         setHistory((prevData: RC50Data[]) => [point, ...prevData])
//     }

//     const [makeDataFetch] = useLazyFetch({
//         onSuccess: result => {
//             setHistory(result.data)
//         }
//     });

//     const [makeTokenFetch] = useLazyFetch({
//         onSuccess: result => {
//             setToken(result)
//         },
//         onError: err => {
//             console.log(err)
//         }
//     });

//     useEffect(() => {
//         makeTokenFetch({
//             url: '/api/token'
//         })
//     }, [])

//     useEffect(() => {
//         if (!history) return;
//         const now = new Date()
//         console.log(currentPoint)
//         if (
//             currentPoint.pressureStatus &&
//             (
//                 currentPoint.systemPressure > (currentPoint.targetPressure + currentPoint.pressureRange) ||
//                 currentPoint.systemPressure < (currentPoint.targetPressure - currentPoint.pressureRange)
//             ) &&
//             ((1 / 1000) * (now.getTime() - alerts.pressure.getTime()) > 5)
//         ) {
//             alert(
//                 'System Pressure Error',
//                 'The system pressure is out of the desired range'
//             );
//             setAlerts((alerts: Alerts) => {
//                 return {
//                     ...alerts,
//                     pressure: new Date()
//                 }
//             })
//         }
//         if (currentPoint.lowLevelStatus !== "FULL" && ((1 / 1000) * (now.getTime() - alerts.lowLevel.getTime()) > 5)) {
//             alert(
//                 'Adhesive Level Error',
//                 'The bottle inside the reservoir is out of adhesive. Please place a new bottle.'
//             )
//             setAlerts((alerts: Alerts) => {
//                 return {
//                     ...alerts,
//                     lowLevel: new Date()
//                 }
//             })
//         }
//         if (currentPoint.dispenseCount > 10000 && ((1 / 1000) * (now.getTime() - alerts.rebuild.getTime()) > 5)) {
//             alert(
//                 'Valve Rebuild Notification',
//                 `Valve has reached it\'s rated lifecycle. Visit ${<a href='https://equipment.loctite.com/page/factory-repair/#exchange' rel='noreferrer' target='_blank'>Loctite Equipment website</a>} to initiate repair process.`
//             )
//             setAlerts((alerts: Alerts) => {
//                 return {
//                     ...alerts,
//                     rebuild: new Date()
//                 }
//             })
//         }
//     }, [currentPoint])

//     useEffect(() => {
//         if (history.length === 0) return;
//         setCurrentPoint(history[0])
//     }, [history])

//     useEffect(() => {
//         if (!token) return;
//         setWs(new WebSocket('ws://localhost:3002'))
//     }, [token])

//     useEffect(() => {
//         if (!ws) return;
//         ws.onopen = () => { }
//         ws.onmessage = function (msg) {
//             const msgData = JSON.parse(msg.data)
//             const newPoint = {
//                 _id: '124',
//                 ...msgData
//             }
//             updateData(newPoint)
//             // console.log(newPoint)
//         }
//     }, [ws])

//     return (
//         <DataContext.Provider
//             value={{
//                 currentPoint,
//                 setCurrentPoint,
//                 history,
//                 setHistory,
//                 live,
//                 setLive,
//                 updateFetched
//             }}>
//             {props.children}
//         </DataContext.Provider>
//     )
// }

// export default DataContextProvider;

import {
    showNotification,
    cleanNotifications,
    hideNotification,
} from "@mantine/notifications";
import React, { ReactNode, useEffect, useState } from "react";
import DataContext from "../context/DataContext";
import useLazyFetch from "../hooks/useLazyFetch";
import { RC50Data } from "../types";

interface DataContextProviderProps {
    children: React.ReactNode;
}

interface Alerts {
    lowLevel: Date;
    pressure: Date;
    rebuild: Date;
}

const init = {
    timestamp: new Date(),
    systemPressure: 12.7,
    systemStatus: false,
    temperature: 20.2,
    humidity: 56,
    pressureUnit: "PSI",
    ch1Mode: "Continue",
    ch2Mode: "Continue",
    ch1Dispensing: false,
    targetPressure: 13,
    pressureRange: 0.3,
    lowLevelCount: 15,
    dispenseCount: 0,
    lowLevelStatus: "FULL",
    runMode: false,
    pressureStatus: false,
    _id: "",
};

const alert = (title: string, message: string | ReactNode) => {
    showNotification({
        title: title,
        message: message,
        autoClose: 5000,
    });
};

function DataContextProvider(props: DataContextProviderProps) {
    const [currentPoint, setCurrentPoint] = useState<RC50Data>(init);
    const [history, setHistory] = useState<RC50Data[]>([]);
    const [live, setLive] = useState<boolean>(true);
    const [ws, setWs] = useState<WebSocket | null>(null);
    const [token, setToken] = useState<any | null>(null);
    const [alerts, setAlerts] = useState<Alerts | any>({
        lowLevel: new Date(2020, 1, 1),
        pressure: new Date(2020, 1, 1),
        rebuild: new Date(2020, 1, 1),
    });

    const updateFetched = () => {
        makeDataFetch({ url: "/api/mongo" });
    };

    const updateData = (point: RC50Data) => {
        setCurrentPoint(point);
        setHistory((prevData: RC50Data[]) => [point, ...prevData]);
    };

    const [makeDataFetch] = useLazyFetch({
        onSuccess: (result) => {
            setHistory(result.data);
        },
    });

    const [makeTokenFetch] = useLazyFetch({
        onSuccess: (result) => {
            setToken(result);
        },
        onError: (err) => {
            console.log(err);
        },
    });

    useEffect(() => {
        makeTokenFetch({
            url: "/api/token",
        });
    }, []);

    useEffect(() => {
        if (!history) return;
        const now = new Date();
        console.log(currentPoint);
        if (
            currentPoint.pressureStatus &&
            (currentPoint.systemPressure >
                currentPoint.targetPressure + currentPoint.pressureRange ||
                currentPoint.systemPressure <
                    currentPoint.targetPressure - currentPoint.pressureRange)
            // &&
            // ((1 / 1000) * (now.getTime() - alerts.pressure.getTime()) > 5)
        ) {
            // alert(
            //     'System Pressure Error',
            //     'The system pressure is out of the desired range'
            // );
            showNotification({
                id: "pressure",
                title: "System Pressure Error",
                message: "The system pressure is out of the desired range",
                autoClose: false,
            });
            setAlerts((alerts: Alerts) => {
                return {
                    ...alerts,
                    pressure: new Date(),
                };
            });
        } else {
            hideNotification("pressure");
        }
        if (
            currentPoint.lowLevelStatus !== "FULL"
            //  && ((1 / 1000) * (now.getTime() - alerts.lowLevel.getTime()) > 5)
        ) {
            // alert(
            //     'Adhesive Level Error',
            //     'The bottle inside the reservoir is out of adhesive. Please place a new bottle.'
            // )
            showNotification({
                id: "lowLevel",
                title: "Adhesive Level Error",
                message:
                    "The bottle inside the reservoir is out of adhesive. Please place a new bottle.",
                autoClose: false,
            });
            setAlerts((alerts: Alerts) => {
                return {
                    ...alerts,
                    lowLevel: new Date(),
                };
            });
        } else {
            hideNotification("lowLevel");
        }
        if (
            currentPoint.dispenseCount > 10000
            // && ((1 / 1000) * (now.getTime() - alerts.rebuild.getTime()) > 20)
        ) {
            // alert(
            //     'Valve Rebuild Notification',
            //     <p>Valve has reached it's rated lifecycle. Visit <a href='https://equipment.loctite.com/page/factory-repair/#exchange' rel='noreferrer' target='_blank'><strong>Loctite Equipment website</strong></a> to initiate repair process.</p>
            // )
            showNotification({
                id: "rebuild",
                title: "Valve Rebuild Notification",
                message: (
                    <p style={{ margin: 0, padding: 0 }}>
                        Valve has reached it's rated lifecycle. Visit{" "}
                        <a
                            href="https://equipment.loctite.com/page/factory-repair/#exchange"
                            rel="noreferrer"
                            target="_blank"
                        >
                            <strong style={{ color: "#EC1B23" }}>
                                Loctite Equipment website
                            </strong>
                        </a>{" "}
                        to initiate repair process.
                    </p>
                ),
                autoClose: false,
            });
            setAlerts((alerts: Alerts) => {
                return {
                    ...alerts,
                    rebuild: new Date(),
                };
            });
        } else {
            hideNotification("rebuild");
        }
        // else {
        //     cleanNotifications()
        // }
    }, [currentPoint]);

    useEffect(() => {
        if (history.length === 0) return;
        setCurrentPoint(history[0]);
    }, [history]);

    useEffect(() => {
        if (!token) return;
        setWs(new WebSocket("ws://localhost:3002"));
    }, [token]);

    useEffect(() => {
        if (!ws) return;
        ws.onopen = () => {};
        ws.onmessage = function (msg) {
            const msgData = JSON.parse(msg.data);
            const newPoint = {
                _id: "124",
                ...msgData,
            };
            updateData(newPoint);
        };
    }, [ws]);

    return (
        <DataContext.Provider
            value={{
                currentPoint,
                setCurrentPoint,
                history,
                setHistory,
                live,
                setLive,
                updateFetched,
            }}
        >
            {props.children}
        </DataContext.Provider>
    );
}

export default DataContextProvider;
