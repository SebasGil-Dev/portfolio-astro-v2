import { defineConfig } from "astro-i18next/config";

export default defineConfig({
  defaultLocale: "es",
  locales: ["es", "en"],
  namespaces: ["common"],
  fallbackLng: "es",
  routing: "prefix", // genera /es/... y /en/...
});


//configurar el i18n