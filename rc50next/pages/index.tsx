import Head from 'next/head'
import { Data, Navbar } from '../src/components'
import styles from '../styles/Home.module.scss'

import mongoose, { ConnectOptions } from 'mongoose';

import { AppShell } from '@mantine/core';
import { RC50Data } from '../src/types';
import { useContext, useEffect } from 'react';
import DataContext from '../src/context/DataContext';

const { Schema } = mongoose;

const Home = ({ data }: { data: RC50Data[] }) => {

  const { setHistory } = useContext(DataContext);

  useEffect(() => {
    if (data.length === 0) return
    setHistory(data)
  }, [data])

  return (
    <div className={styles.container}>
      <Head>
        <title>RC50 Monitoring Application</title>
        <meta name="description" content="Live Dashboard for RC50 Integrated Dispenser" />
        <link rel="icon" href="/favicon.ico" />


        <meta property="og:url" content="https://rc50.vercel.app/" />
        <meta property="og:type" content="website" />
        <meta property="og:title" content="RC50 Monitoring Application" />
        <meta property="og:description" content="Live Dashboard for RC50 Integrated Dispenser." />
        <meta property="og:image" content="https://dm.henkel-dam.com/is/image/henkel/1_Header_Loctite_Pulse_Hero_background_steelworker_with_pulse?wid=3440&fit=crop%2C1&qlt=90&align=0.01%2C-0.37&hei=1200" />

      </Head>
      <AppShell
        padding="md"
        header={<Navbar />}
        styles={(theme) => ({
          main: { backgroundColor: theme.colorScheme === 'dark' ? theme.colors.dark[8] : theme.colors.gray[0] },
        })}
      >
        <main className={styles.main}>
          <Data />
        </main>
      </AppShell>

    </div>
  )
}

export default Home

export async function getServerSideProps() {

  mongoose.connect(`mongodb://root:rootpassword@rc50db:27017/?authSource=admin&readPreference=primary&appname=MongoDB%20Compass&directConnection=true&ssl=false`, {
    useNewUrlParser: true,
    useUnifiedTopology: true,
    dbName: 'rc50data'
  } as ConnectOptions);

  let RC50 = mongoose.models.RC50 || mongoose.model('RC50', new Schema({}, { strict: false }), 'rc50data');

  const find = async (): Promise<any> => {
    try {
      const data = await RC50.find().sort({ timestamp: -1 }).limit(30)
      return [data, null]
    } catch (err) {
      return [null, err]
    }
  };

  const [data, err]: [RC50Data[], any] = await find()

  return {
    props: {
      data: JSON.parse(JSON.stringify(data))
    }
  }
}