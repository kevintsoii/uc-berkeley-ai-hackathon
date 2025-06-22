"use client";

import { useEffect } from "react";

export function useTheme() {
  // Force dark mode always
  const isDarkMode = true;

  // Apply dark theme to document on mount
  useEffect(() => {
    document.documentElement.setAttribute("data-theme", "dark");
    localStorage.setItem("theme", "dark");
  }, []);

  // No-op toggle function (theme can't be changed)
  const toggleTheme = () => {
    // Do nothing - dark mode is forced
  };

  return { isDarkMode, toggleTheme };
}
