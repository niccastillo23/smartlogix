// Configuración de las pruebas E2E y de API de SmartLogix (Encargo 3).
// Requiere el stack en ejecución (docker compose up -d) o las URLs definidas por variables de entorno.
import { defineConfig } from "@playwright/test";

const FRONT_URL = process.env.FRONT_URL || "http://localhost:5173";
const API_URL = process.env.API_URL || "http://localhost:8080";

export default defineConfig({
  testDir: "./tests",
  timeout: 45_000,
  retries: 0,
  workers: 1, // las pruebas comparten la base H2 del stack: se ejecutan en serie
  reporter: [["list"], ["html", { outputFolder: "reports/html", open: "never" }], ["json", { outputFile: "reports/resultados.json" }]],
  use: {
    baseURL: FRONT_URL,
    trace: "retain-on-failure",
    screenshot: "only-on-failure",
    video: "off",
  },
  metadata: { FRONT_URL, API_URL },
  projects: [
    { name: "ui", testMatch: /ui\.spec\.js/, use: { browserName: "chromium", viewport: { width: 1280, height: 800 } } },
    { name: "api", testMatch: /api\.spec\.js/, use: { baseURL: API_URL } },
  ],
});
