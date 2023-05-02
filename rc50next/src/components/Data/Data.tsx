import React, { useContext } from "react";
import DataContext from "../../context/DataContext";
import { Equipment } from "../Equipment";
import { Graph } from "../Graph";
import { Tile } from "../Tile";
import styles from "./Data.module.scss";

function Data(props: any) {
    const { currentPoint } = useContext(DataContext);
    return (
        <div className={styles.content}>
            <Equipment />
            {currentPoint ? (
                <div className={styles.data}>
                    <Graph />
                    <div className={styles.tiles}>
                        <Tile
                            label={"systemPressure"}
                            title="Pressure"
                            value={
                                Math.round(10 * currentPoint.systemPressure) /
                                10
                            }
                            unit={currentPoint.pressureUnit}
                            bounds={[
                                currentPoint.targetPressure -
                                    currentPoint.pressureRange,
                                currentPoint.targetPressure +
                                    currentPoint.pressureRange,
                            ]}
                        />
                        <Tile
                            label={"dispenseCount"}
                            title="Dispense Count"
                            value={currentPoint.dispenseCount}
                            unit=" "
                            bounds={[0, 10000]}
                        />
                        <Tile
                            label={"lowLevelCount"}
                            title="Low Level Count"
                            value={currentPoint.lowLevelCount}
                            unit=""
                            bounds={[15, 100]}
                        />
                        <Tile
                            label={"ch1Dispensing"}
                            title="Dispensing Status"
                            value={
                                currentPoint.ch1Dispensing
                                    ? "Dispensing"
                                    : "Stopped"
                            }
                        />
                        <Tile
                            label={"temperature"}
                            title="Temperature"
                            value={
                                Math.round(10 * currentPoint.temperature) / 10
                            }
                            unit="°C"
                        />
                        <Tile
                            label={"humidity"}
                            title="Humidity"
                            value={Math.round(10 * currentPoint.humidity) / 10}
                            unit="%RH"
                        />
                    </div>
                </div>
            ) : (
                ""
            )}
        </div>
    );
}

export default Data;
