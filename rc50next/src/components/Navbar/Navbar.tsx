import { Header } from '@mantine/core';
import { useContext, useEffect } from 'react';
import DataContext from '../../context/DataContext';
import { Henkel, Refresh } from '../../graphics';
import useLazyFetch from '../../hooks/useLazyFetch';

import styles from './Navbar.module.scss'


const Navbar = () => {

    const {setHistory} = useContext(DataContext)

    const [makeFetch] = useLazyFetch({
        onSuccess: result => {
            setHistory(result.data)
        }
    })

    const decDispenseCount = () => {
        makeFetch({
            url: 'api/mongo?test=test'
        })
    }

    return (
        <Header height={70} p="xs" fixed style={{ width: '100%' }} position={{ top: 0, left: 0 }}>
            <div className={styles.navbar}>
                <div className={styles.title} onClick={() => decDispenseCount()}>
                    <Henkel />
                    <p>Loctite RC50 Monitoring Application</p>
                </div>
                {/* <div className={styles.buttons} onClick={() => updateFetched()}>
                    <div>
                        <Refresh/>
                    </div>

                    <div className={styles.live} onClick={() => handleLive()}>
                        <span className={`${live ? styles.isLive : styles.isNotLive}`}></span>
                    </div>
                </div> */}
            </div>
        </Header>
    )
}

export default Navbar