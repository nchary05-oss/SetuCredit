import React from "react";
import { createRoot } from "react-dom/client";
import App from "./App.jsx";
import "./styles.css";

const storedTheme = localStorage.getItem("sc-theme");
if (storedTheme === "light" || storedTheme === "dark") {
  document.documentElement.setAttribute("data-theme", storedTheme);
} else if (matchMedia("(prefers-color-scheme: light)").matches) {
  document.documentElement.setAttribute("data-theme", "light");
}

createRoot(document.getElementById("root")).render(
  <React.StrictMode>
    <App />
  </React.StrictMode>,
);
