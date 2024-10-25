import { defineConfig } from 'vite';
import react from '@vitejs/plugin-react-swc';

export default defineConfig({
    server: {
        proxy: {
            '/api': {
                target: 'http://194.58.126.172:8000',
                changeOrigin: true,
                secure: false,
            },
        },
    },
    plugins: [react()],
});
