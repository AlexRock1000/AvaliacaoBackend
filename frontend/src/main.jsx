import React from "react";
import { createRoot } from "react-dom/client";

import Aplicativo from "./Aplicativo.jsx";
import "./estilos.css";


// Monta a interface React dentro do elemento principal da página.
createRoot(document.getElementById("raiz")).render(
  <React.StrictMode>
    <Aplicativo />
  </React.StrictMode>,
);
