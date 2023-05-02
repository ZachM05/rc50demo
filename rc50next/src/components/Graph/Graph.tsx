import dynamic from 'next/dynamic';
import styles from './Graph.module.scss'
import React, { useContext, useState } from 'react';
import DataContext from '../../context/DataContext';

const Plot = dynamic(() => import('react-plotly.js'), { ssr: false });

function Graph(props: any) {
    const { history, currentPoint, setCurrentPoint, setHistory } = useContext(DataContext)

    const [timeFrame, setTimeFrame] = useState<number>(300000)

    return (
        <div>
            <div>
                <ul className={styles.timeSelect}>
                    <li className={`${timeFrame === 300000 ? styles.active : ''}`} onClick={() => setTimeFrame(300000)}>5m</li>
                    <li className={`${timeFrame === 600000 ? styles.active : ''}`} onClick={() => setTimeFrame(600000)}>10m</li>
                    <li className={`${timeFrame === 1800000 ? styles.active : ''}`} onClick={() => setTimeFrame(1800000)}>30m</li>
                    <li className={`${timeFrame === 3600000 ? styles.active : ''}`} onClick={() => setTimeFrame(3600000)}>1hr</li>
                    <li className={`${timeFrame === 28800000 ? styles.active : ''}`} onClick={() => setTimeFrame(28800000)}>8hr</li>
                    <li className={`${timeFrame === 86400000 ? styles.active : ''}`} onClick={() => setTimeFrame(86400000)}>1d</li>
                </ul>
                {history ? <Plot
                    layout={{
                        title: {
                            text: 'System Pressure',
                            font: {
                                family: '-apple-system, BlinkMacSystemFont, Segoe UI, Roboto, Oxygen, Ubuntu, Cantarell, Fira Sans, Droid Sans, Helvetica Neue, sans-serif;',
                                // family: 'Courier New, monospace',
                                size: 24
                            },
                            xref: 'paper',
                            x: 0.05,
                        },
                        xaxis: {
                            title: {
                                text: 'Time',
                                font: {
                                    family: '-apple-system, BlinkMacSystemFont, Segoe UI, Roboto, Oxygen, Ubuntu, Cantarell, Fira Sans, Droid Sans, Helvetica Neue, sans-serif;',
                                    // family: 'Courier New, monospace',
                                    size: 18,
                                    color: '#7f7f7f'
                                }
                            },
                            range: [new Date(currentPoint.timestamp).getTime() - timeFrame, new Date(currentPoint.timestamp)]
                        },
                        yaxis: {
                            title: {
                                text: `System Pressure (${currentPoint.pressureUnit})`,
                                font: {
                                    family: '-apple-system, BlinkMacSystemFont, Segoe UI, Roboto, Oxygen, Ubuntu, Cantarell, Fira Sans, Droid Sans, Helvetica Neue, sans-serif;',
                                    size: 18,
                                    color: '#7f7f7f'
                                }
                            }
                        },
                        shapes: [
                            {
                                type: 'line',
                                xref: 'paper',
                                x0: 0,
                                y0: currentPoint.targetPressure,
                                x1: 1,
                                y1: currentPoint.targetPressure,
                                line: {
                                    color: 'rgb(0, 255, 0)',
                                    width: 4,
                                    dash: 'dot'
                                }
                            },
                            {
                                type: 'line',
                                xref: 'paper',
                                x0: 0,
                                y0: currentPoint.targetPressure - currentPoint.pressureRange,
                                x1: 1,
                                y1: currentPoint.targetPressure - currentPoint.pressureRange,
                                line: {
                                    color: 'rgb(255, 0, 0)',
                                    width: 4,
                                    dash: 'dot'
                                }
                            },
                            {
                                type: 'line',
                                xref: 'paper',
                                x0: 0,
                                y0: currentPoint.targetPressure + currentPoint.pressureRange,
                                x1: 1,
                                y1: currentPoint.targetPressure + currentPoint.pressureRange,
                                line: {
                                    color: 'rgb(255, 0, 0)',
                                    width: 4,
                                    dash: 'dot'
                                }
                            }
                        ],
                        autosize: true,
                        datarevision: history.length

                    }}
                    useResizeHandler={true}
                    className={styles.plot}
                    revision={history.length}
                    data={[
                        {
                            x: history
                                .map(point => new Date(point.timestamp)),
                            y: history
                                .map(point => point.systemPressure),
                            name: 'Pressure Data',
                            mode: 'lines',
                            type: 'scatter',
                            marker: {
                                size: 5,
                                opacity: 0.8,
                            }
                        }
                    ]}
                /> : ''}
            </div>
        </div>
    );
}

export default Graph;