import { createContext, useContext } from 'react'
import APIBridge from '@src/lib/api';

export interface AppContextValue {
    api: APIBridge
}

export const AppContext = createContext<AppContextValue>({} as AppContextValue)

export const useAppContext = () => useContext(AppContext)
