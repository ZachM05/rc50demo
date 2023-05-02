import styles from './Equipment.module.scss'
import { useState } from 'react';
import { Modal } from '../Modal';

function ServiceHistory() {
    const serviceHistory = [
        {
            title: 'Pressure regulator calibration',
            date: new Date(2021, 12, 2, 13, 10, 45),
            status: 'good'
        },
        {
            title: 'Software update',
            date: new Date(2021, 11, 23, 9, 6, 23),
            status: 'good'
        },
        {
            title: 'Pressure regulator replacement',
            date: new Date(2021, 11, 20, 10, 13, 43),
            status: 'good'
        },
        {
            title: 'Pressure regulator failure',
            date: new Date(2021, 11, 18, 14, 43, 23),
            status: 'bad'
        },
        {
            title: 'Equipment installation',
            date: new Date(2021, 9, 1, 16, 58, 55),
            status: 'good'
        }
    ]

    return (
        <ul className={styles.history}>
        {serviceHistory.map((item, index) => {
            return (
                <li className={`${item.status === 'good' ? styles.good : styles.bad}`} key={index}>
                    <h3>{item.title}</h3>
                    <p>{item.date.toLocaleString()}</p>
                </li>
            )
        })}
    </ul>
    )
}

export default function Equipment() {
    const [opened, setOpened] = useState(false);
    return (
        <div className={styles.card}>
            <Modal title={'Equipment History'} shown = {opened} close={() => setOpened(false)}>
               <ServiceHistory/>
            </Modal>

            <img src='https://dm.henkel-dam.com/is/image/henkel/EQ-RC50-Integrated-Dispenser-I4.0-IDH-2814024?wid=4096&fit=fit%2C1&qlt=90&align=0%2C0&hei=4096' alt='Loctite RC50' />
            <div className={styles.info}>
                <ul>
                    <li>
                        <h3>Equipment</h3>
                        <p>Loctite EQ RC50 Integrated Dispenser</p>
                    </li>
                    <li>
                        <h3>IDH</h3>
                        <p>2814024</p>
                    </li>
                    <li>
                        <h3>Serial Number</h3>
                        <p>22APACA-012</p>
                    </li>
                    <li>
                        <h3>Country</h3>
                        <p>Germany</p>
                    </li>
                    <li>
                        <h3>Facility</h3>
                        <p>Inspiration Center, Dusseldorf</p>
                    </li>
                    <li>
                        <h3>Room</h3>
                        <p>AAS Lab</p>
                    </li>
                    <li style={{alignSelf: 'center'}}>
                        <button onClick={() => setOpened(true)} className={styles.button}>
                            <h3>Eqp. History</h3>
                        </button>
                    </li>
                </ul>
            </div>
        </div>
    )
}