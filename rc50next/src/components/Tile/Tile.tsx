import dynamic from "next/dynamic";
import { Datum } from "plotly.js";
import React, { useContext, useState } from "react";
import { InfoCircle } from "tabler-icons-react";
import DataContext from "../../context/DataContext";
import { Error } from "../../graphics";
import { RC50Data } from "../../types";
import { Modal } from "../Modal";
import styles from "./Tile.module.scss";

const Plot = dynamic(() => import("react-plotly.js"), { ssr: false });

function TileGraph({ data }: { data: string }) {
    const dataMap = (
        point: RC50Data,
        value: string
    ): number | string | Date | boolean => {
        switch (value) {
            case "timestamp":
                return point.timestamp;
            case "systemPressure":
                return point.systemPressure;
            case "systemStatus":
                return point.systemStatus;
            case "temperature":
                return point.temperature;
            case "humidity":
                return point.humidity;
            case "pressureUnit":
                return point.pressureUnit;
            case "ch1Mode":
                return point.ch1Mode;
            case "ch2Mode":
                return point.ch2Mode;
            case "targetPressure":
                return point.targetPressure;
            case "pressureRange":
                return point.pressureRange;
            case "lowLevelCount":
                return point.lowLevelCount;
            case "lowLevelStatus":
                return point.lowLevelStatus;
            case "dispenseCount":
                return point.dispenseCount;
            default:
                return 0;
        }
    };

    const { history, currentPoint } = useContext(DataContext);
    const [timeFrame, setTimeFrame] = useState<number>(300000);

    return (
        <div>
            <div>
                <ul className={styles.timeSelect}>
                    <li
                        className={`${
                            timeFrame === 300000 ? styles.active : ""
                        }`}
                        onClick={() => setTimeFrame(300000)}
                    >
                        5m
                    </li>
                    <li
                        className={`${
                            timeFrame === 600000 ? styles.active : ""
                        }`}
                        onClick={() => setTimeFrame(600000)}
                    >
                        10m
                    </li>
                    <li
                        className={`${
                            timeFrame === 1800000 ? styles.active : ""
                        }`}
                        onClick={() => setTimeFrame(1800000)}
                    >
                        30m
                    </li>
                    <li
                        className={`${
                            timeFrame === 3600000 ? styles.active : ""
                        }`}
                        onClick={() => setTimeFrame(3600000)}
                    >
                        1hr
                    </li>
                    <li
                        className={`${
                            timeFrame === 28800000 ? styles.active : ""
                        }`}
                        onClick={() => setTimeFrame(28800000)}
                    >
                        8hr
                    </li>
                    <li
                        className={`${
                            timeFrame === 86400000 ? styles.active : ""
                        }`}
                        onClick={() => setTimeFrame(86400000)}
                    >
                        1d
                    </li>
                </ul>
                {history ? (
                    <Plot
                        layout={{
                            xaxis: {
                                title: {
                                    text: "Time",
                                    font: {
                                        family: "-apple-system, BlinkMacSystemFont, Segoe UI, Roboto, Oxygen, Ubuntu, Cantarell, Fira Sans, Droid Sans, Helvetica Neue, sans-serif;",
                                        // family: 'Courier New, monospace',
                                        size: 18,
                                        color: "#7f7f7f",
                                    },
                                },
                                range: [
                                    new Date(currentPoint.timestamp).getTime() -
                                        timeFrame,
                                    new Date(currentPoint.timestamp),
                                ],
                            },
                            autosize: true,
                            datarevision: history.length,
                        }}
                        useResizeHandler={true}
                        className={styles.plot}
                        revision={history.length}
                        data={[
                            {
                                x: history.map(
                                    (point) => new Date(point.timestamp)
                                ),
                                y: history.map((point) =>
                                    dataMap(point, data)
                                ) as Datum[],
                                mode: "lines",
                                type: "scatter",
                                marker: {
                                    size: 5,
                                    opacity: 0.8,
                                },
                            },
                        ]}
                    />
                ) : (
                    ""
                )}
            </div>
        </div>
    );
}

const Tile = ({
    title,
    value,
    unit,
    label,
    bounds,
}: {
    title: string;
    value: number | string;
    unit?: string;
    label: string;
    bounds?: Array<number>;
}) => {
    const [opened, setOpened] = useState(false);

    return (
        <div className={styles.outer}>
            <Modal title={title} shown={opened} close={() => setOpened(false)}>
                <TileGraph data={label} />
            </Modal>
            <div className={styles.infoButton} onClick={() => setOpened(true)}>
                <InfoCircle />
                {bounds &&
                typeof value == "number" &&
                (bounds[0] > value || bounds[1] < value) ? (
                    <div className={styles.error}>
                        <Error />
                    </div>
                ) : (
                    ""
                )}
            </div>
            <div className={styles.inner}>
                <div className={styles.title}>
                    <h2>{title}</h2>
                </div>
                <div className={styles.values}>
                    {typeof value == "string" && (
                        <p className={styles.text}>{value}</p>
                    )}
                    {typeof value == "number" && (
                        <p className={styles.value}>{value}</p>
                    )}
                    {unit && <p className={styles.unit}>{unit}</p>}
                </div>
            </div>
        </div>
    );
};

export default Tile;
