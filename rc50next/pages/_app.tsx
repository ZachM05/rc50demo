import '../styles/globals.scss';
import '../styles/Notifications.scss';
import type { AppProps } from 'next/app';
import DataContextProvider from '../src/providers/DataContextProvider';
import { NotificationsProvider } from '@mantine/notifications';

function MyApp({ Component, pageProps }: AppProps) {
  return (
    <DataContextProvider>
      <NotificationsProvider position="top-right" limit={1}>
        <Component {...pageProps} />
      </NotificationsProvider>
    </DataContextProvider>
  )
}

export default MyApp
