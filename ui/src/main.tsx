import ReactDOM from 'react-dom/client';
import App from './App';
import {QueryClient} from "@tanstack/react-query";

const client = new QueryClient()

ReactDOM.createRoot(document.getElementById('root')!).render(<App />);
