import '@mantine/core/styles.css';
import { LoadingOverlay, MantineProvider, Text } from '@mantine/core';
import { Router } from '@src/Router';
import { theme } from '@src/theme';

import Boundary, { PYWEBVIEWREADY } from '@src/lib/boundary'
import { Switchboard } from '@src/lib/switchboard';
import { useEffect, useMemo, useState } from 'react';
import APIBridge from '@src/lib/api';
import { AppContext, type AppContextValue } from '@src/contexts/App.context';

const boundary = new Boundary()
const switchboard = new Switchboard()

export default function App() {
    const [isReady, setIsReady] = useState(false)

    const api = useMemo(() => new APIBridge(boundary), [])

    useEffect(() => {
        console.log('Connected')
        if (window.pywebview !== undefined && window.pywebview.api !== undefined) {
            setIsReady(true)
        } else {
            window.addEventListener(PYWEBVIEWREADY, () => setIsReady(true), { once: true })
        }
    }, [isReady, setIsReady])

    const appContext = useMemo<AppContextValue>(() => ({
        api
    }), [api])

    api.logger.debug('UI is ready').then()

    if (!isReady) {
        return (
            <MantineProvider forceColorScheme='dark' theme={theme}>
              <LoadingOverlay visible />
                <Text>Waiting on API</Text>
            </MantineProvider>
        )
    }

  return (
    <MantineProvider forceColorScheme='dark' theme={theme}>
        <AppContext.Provider value={appContext}>
            <Router />
        </AppContext.Provider>
    </MantineProvider>
  );
}
