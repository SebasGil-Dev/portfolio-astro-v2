/// <reference types="astro/client" />

import lang from "../i18n/lang.json";

type Lang = "es" | "en";
type Dict = Record<string, any>;
type Root = Record<Lang, Dict>;

const ROOT = lang as Root;
const DEFAULT_LANG: Lang = "es";
const LANG_KEY = "lang";

// Bandera: resuelve URL de los SVG sin ?url
const esFlagUrl = new URL("../assets/es.svg", import.meta.url).href;
const enFlagUrl = new URL("../assets/en.svg", import.meta.url).href;

// -------- utils
const getInitialLang = (): Lang => {
  try {
    const stored = localStorage.getItem(LANG_KEY);
    if (stored === "es" || stored === "en") return stored as Lang;
  } catch {}
  const html = document.documentElement.getAttribute("lang");
  if (html === "es" || html === "en") return html as Lang;
  const nav = (navigator.language || "").toLowerCase();
  return nav.startsWith("en") ? "en" : DEFAULT_LANG;
};

const setFlagsIfAny = (langCode: Lang) => {
  document.querySelectorAll<HTMLImageElement>("[data-lang-flag]").forEach((img) => {
    img.src = langCode === "es" ? esFlagUrl : enFlagUrl;
    img.alt = langCode === "es" ? "Español" : "English";
  });
};

// -------- core
const applyI18N = (langCode: Lang) => {
  const dict = ROOT[langCode] || ROOT[DEFAULT_LANG];

  document.querySelectorAll<HTMLElement>("[data-i18n]").forEach((el) => {
    const key = el.dataset.i18n!;
    const val = (dict as any)[key];

    if (Array.isArray(val)) {
      const sep = el.getAttribute("data-i18n-sep") ?? " ";
      el.textContent = val.join(sep);
    } else if (typeof val === "string" || typeof val === "number") {
      el.textContent = String(val);
    }
    // si no existe la clave, deja el fallback del HTML
  });

  document.documentElement.setAttribute("lang", langCode);
  try { localStorage.setItem(LANG_KEY, langCode); } catch {}
  setFlagsIfAny(langCode);

  document.dispatchEvent(new CustomEvent("i18n:changed", { detail: { lang: langCode } }));
};

const toggleLang = () => {
  const cur = (localStorage.getItem(LANG_KEY) as Lang) || getInitialLang();
  applyI18N(cur === "es" ? "en" : "es");
};

// -------- boot
document.addEventListener("DOMContentLoaded", () => {
  applyI18N(getInitialLang());
  document.addEventListener("click", (ev) => {
    const t = ev.target as Element | null;
    if (t?.closest("[data-lang-toggle]")) toggleLang();
  });
});

export {};
