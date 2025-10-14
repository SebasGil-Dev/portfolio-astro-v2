// src/scripts/i18n.ts
// Carga el diccionario y aplica traducciones de texto + placeholders.

import lang from "../i18n/lang.json";

type Lang = "es" | "en";
type Dict = Record<string, string>;
type Root = Record<Lang, Dict>;

const ROOT = lang as Root;
const LANG_KEY = "lang";
const DEFAULT_LANG: Lang = "es";

/* ---------------- helpers ---------------- */
const getBrowserLang = (): Lang => {
  try {
    const nav = navigator?.language?.slice(0, 2).toLowerCase();
    return (nav === "en" ? "en" : "es") as Lang;
  } catch {
    return DEFAULT_LANG;
  }
};

export const getLang = (): Lang => {
  try {
    const saved = localStorage.getItem(LANG_KEY) as Lang | null;
    if (saved && ROOT[saved]) return saved;
  } catch {}
  return getBrowserLang();
};

export const setLang = (lng: Lang, persist = true) => {
  const langToUse = ROOT[lng] ? lng : DEFAULT_LANG;
  if (persist) {
    try {
      localStorage.setItem(LANG_KEY, langToUse);
    } catch {}
  }
  applyI18n(langToUse);
  // Notifica a componentes que dependen del idioma (e.g. tipeo del about)
  document.dispatchEvent(new CustomEvent("i18n:changed", { detail: { lang: langToUse } }));
};

/* ---------------- aplicación de i18n ---------------- */
function applyI18n(lng: Lang) {
  const dict = ROOT[lng] || (ROOT[DEFAULT_LANG] as Dict);

  // 1) Texto normal: <span data-i18n="key"></span>
  document.querySelectorAll<HTMLElement>("[data-i18n]").forEach((el) => {
    const key = el.getAttribute("data-i18n")!;
    const v = dict[key];
    if (typeof v === "string") el.textContent = v;
  });

  // 2) Placeholders: <input data-i18n-placeholder="key" />
  document
    .querySelectorAll<HTMLInputElement | HTMLTextAreaElement>("[data-i18n-placeholder]")
    .forEach((el) => {
      const key = el.getAttribute("data-i18n-placeholder")!;
      const v = dict[key];
      if (typeof v === "string") el.placeholder = v;
    });

  // 3) Opcional: title y aria-label si alguna vez los usas
  document.querySelectorAll<HTMLElement>("[data-i18n-title]").forEach((el) => {
    const key = el.getAttribute("data-i18n-title")!;
    const v = dict[key];
    if (typeof v === "string") el.setAttribute("title", v);
  });

  document.querySelectorAll<HTMLElement>("[data-i18n-aria-label]").forEach((el) => {
    const key = el.getAttribute("data-i18n-aria-label")!;
    const v = dict[key];
    if (typeof v === "string") el.setAttribute("aria-label", v);
  });

  // marca el idioma activo en <html>
  document.documentElement.setAttribute("lang", lng);
}

/* ---------------- inicialización ---------------- */
document.addEventListener("DOMContentLoaded", () => {
  applyI18n(getLang());

  // Si tienes un botón global para alternar idioma:
  // <button data-lang-toggle></button>
  const btn = document.querySelector("[data-lang-toggle]");
  btn?.addEventListener("click", () => {
    const next: Lang = getLang() === "es" ? "en" : "es";
    setLang(next, true);
  });
});

// Exporta en window por si lo quieres usar manualmente desde la consola
declare global {
  interface Window {
    __setLang?: (l: Lang) => void;
    __getLang?: () => Lang;
  }
}
window.__setLang = (l: Lang) => setLang(l, true);
window.__getLang = () => getLang();
