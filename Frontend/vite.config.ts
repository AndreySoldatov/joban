import { defineConfig } from "vite";
import react from "@vitejs/plugin-react-swc";

export default defineConfig({
    server: {
        proxy: {
            "/api": {
                target: "https://joban.ddns.net",
                changeOrigin: true,
                secure: false,
            },
        },
    },
    plugins: [react()],
});
