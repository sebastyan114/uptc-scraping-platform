# Web Scanner — Frontend

Interfaz web del proyecto de scraping y análisis de vulnerabilidades. Permite ingresar una URL, iniciar un análisis, ver su progreso en vivo y consultar el historial.

> **Estado actual:** MVP básico y funcional, sin backend real. Todas las peticiones a `/api/*` las responde un mock en el navegador (MSW), no un servidor. Esto es intencional mientras el backend no está listo — ver la sección de arquitectura más abajo.

---

## 🛠 Tecnologías Usadas

El proyecto utiliza el siguiente stack tecnológico:

- **[React](https://react.dev/)**: Biblioteca principal para construir la interfaz de usuario.
- **[Vite](https://vite.dev/)**: Herramienta de construcción (build tool) y servidor de desarrollo ultrarrápido.
- **[TypeScript](https://www.typescriptlang.org/)**: Tipado estático para JavaScript, previniendo errores y mejorando la experiencia del desarrollador.
- **[React Router](https://reactrouter.com/)**: Enrutamiento de la aplicación (Single Page Application).
- **[Tailwind CSS](https://tailwindcss.com/) v4**: Framework de CSS basado en utilidades para un diseño ágil.
- **[React Query](https://tanstack.com/query/latest)**: Gestión de estado del servidor, caché y sincronización de datos.
- **[MSW](https://mswjs.io/)**: Interceptación de solicitudes HTTP para ejecutar el frontend con mocks durante el desarrollo y las pruebas.
- **[tsx](https://tsx.is/)**: Ejecución del smoke test escrito en TypeScript.
- **openapi-typescript**: Generación de tipos TypeScript a partir del contrato OpenAPI.
- **Oxlint**: Linter ultrarrápido para mantener la calidad del código.
- **Docker & Nginx**: Contenedorización y servidor web ligero para el despliegue a producción.

---

## 1. Cómo levantarlo

```bash
cd frontend
npm install
npm run dev
```

Abre [http://localhost:5173](http://localhost:5173). No hace falta levantar ningún backend ni base de datos: los mocks arrancan solos en modo desarrollo.

Revisa si tu proyecto tiene un archivo `.env.example` (puede estar en la raíz de `frontend/` o dentro de `docker/`, según cómo quedó organizado). Si lo tiene, cópialo a `.env` antes de correr `npm run dev`. Si existe la variable `VITE_USE_MOCKS`, déjala en `true` para seguir usando los mocks; en `false` intentaría hablar con un backend real en `VITE_PROXY_TARGET`.

### Verificar que todo está sano antes de tocar nada

```bash
npx tsc -b      # tipos
npm run lint    # oxlint
npm run build   # build de producción
```

Los 3 deben terminar sin errores. Si alguno falla apenas clonas el repo, es un problema de entorno (versión de Node, dependencias), no de tu código.

*(Opcional) Smoke test de los endpoints simulados:*
```bash
npm run verify:mocks
```

---

## 2. Arquitectura, en resumen

```text
pages/             -> una página por ruta (Inicio, Historial, Detalle, 404)
   |   usan
   v
features/analysis/ -> hooks de React Query (traer, listar, crear) + funciones que llaman a la API
   |   usan
   v
lib/api-client      -> cliente HTTP tipado, generado desde el contrato OpenAPI
   |
   v
/api/*  -----------> en desarrollo: interceptado por MSW (mocks/handlers.ts)
                      en producción: lo resuelve nginx, reenviando a un backend real
```

### Por qué está dividido así

Cada página solo sabe pedir datos a través de un hook (`useAnalyses`, `useAnalysisDetail`, `useCreateAnalysis`); no sabe nada de cómo se arma la petición HTTP. Eso vive en `features/analysis/api.ts`. Y ese archivo tampoco sabe si está hablando con un mock o con un backend real — eso lo decide `lib/api-client`, apoyado en el cliente tipado que generamos con `openapi-typescript` a partir de `docs/api/openapi.yaml`. El día que el backend esté listo, en teoría no hay que tocar ni las páginas ni los hooks: solo se apaga el mock.

### Piezas clave

| Carpeta / archivo | Qué hace |
| :--- | :--- |
| `src/app/router.tsx` | Define las rutas: `/`, `/historial`, `/analisis/:analysisId`, y `*` (404) |
| `src/app/AppLayout.tsx` | El menú de navegación (Inicio / Historial) y el contenedor de cada página |
| `src/pages/HomePage.tsx` | Formulario para crear un análisis nuevo |
| `src/pages/HistoryPage.tsx` | Lista de análisis ya creados, con enlace al detalle de cada uno |
| `src/pages/AnalysisDetailPage.tsx` | Progreso en vivo y, al terminar, el resumen del análisis |
| `src/features/analysis/` | Los hooks (`use-analyses`, `use-analysis-detail`, `use-create-analysis`) y `api.ts` |
| `src/components/` | `LoadingState`, `ErrorState`, `EmptyState` — se reutilizan en varias páginas |
| `src/mocks/` | `fixtures.ts` (los datos de prueba y su simulación de progreso) y `handlers.ts` (qué responde cada endpoint falso) |
| `docker/` | Dockerfile y nginx.conf para empaquetar y servir el build de producción |

### Cómo "avanza" un análisis sin backend

Al crear un análisis, el mock lo guarda con estado `pending` y programa, con `setTimeout`, que pase a `running` y luego a `completed` por su cuenta. La pantalla de detalle vuelve a pedir el dato cada 1 segundo mientras el análisis sigue activo, así que el cambio de estado se ve en vivo, sin recargar la página.

> **Importante:** estos datos viven solo en la memoria de la pestaña del navegador. Al recargar la página (F5), se pierden. Esto es esperado mientras no haya un backend real con base de datos — no es un error.

---

## 3. Cómo probarlo (guía para el tester)

No hace falta backend ni configuración previa: con `npm run dev` ya se puede probar todo el flujo. Casos sugeridos, de principio a fin:

### Caso 1 — Flujo feliz completo
1. Entra a `/` y escribe una URL válida, por ejemplo `https://uptc.edu.co`.
2. Debe navegar solo a la página de detalle, mostrando estado "En cola".
3. Sin tocar nada, espera unos segundos: debe pasar a "Analizando…" y luego a "Completado", con protecciones y vulnerabilidades listadas.
4. Ve a **Historial**: el análisis debe aparecer ahí, ya no debe decir "Sin análisis todavía".
5. Haz clic en ese análisis desde el historial: debe volver a mostrar el mismo detalle.

### Caso 2 — URL inválida
Escribe algo que no sea una URL (por ejemplo `hola`) y envía el formulario. Debe mostrar un mensaje de error sin navegar a ninguna otra pantalla.

### Caso 3 — URL bloqueada
Prueba con una URL que apunte a una red privada (`http://localhost`, `http://127.0.0.1`, `http://192.168.1.1`). Debe rechazarla con un mensaje de error, igual que el caso anterior.

### Caso 4 — Un análisis a la vez
Crea un análisis y, mientras siga en "En cola" o "Analizando…", intenta crear otro desde Inicio. Debe rechazarlo indicando que ya hay uno en curso.

### Caso 5 — Historial vacío
Abre la app en una pestaña nueva (o en modo incógnito, para no arrastrar análisis previos) y entra directo a Historial sin crear nada antes. Debe mostrar el mensaje de "Sin análisis todavía", no una lista vacía sin explicación ni un error.

### Caso 6 — Ruta inexistente
Navega a una URL que no exista, como `/esto-no-existe`. Debe mostrar la página de "no encontrada", no un error en blanco ni la pantalla de Inicio.

### Caso 7 — Análisis que no existe
Navega directo a `/analisis/` seguido de cualquier texto que no sea un id real (por ejemplo `/analisis/abc123`). Debe mostrar un mensaje de error controlado, no una pantalla en blanco ni que la app se rompa.

### Qué reportar si algo falla
Para cada caso que falle, lo más útil es: la URL exacta que visitaste, qué esperabas ver, qué viste en realidad, y si el error aparece también en la consola del navegador (F12 → pestaña Console) — cópialo tal cual, ayuda mucho a ubicar la causa.

---

## 4. Qué no cubre esto todavía

- **No hay backend real:** Todo lo de arriba se prueba contra datos simulados en MSW.
- **No hay autenticación:** Se removió del alcance del MVP; cualquiera que abra la app puede crear y ver análisis.
- **Tablas de hallazgos:** Las tablas de protecciones y vulnerabilidades son un conteo simple, no una tabla detallada todavía — eso es una tarea aparte.
- **Persistencia:** No persiste nada entre recargas (F5), como se explicó en la sección de arquitectura.

---

## 5. Despliegue con Docker (Opcional)

Si deseas empaquetar y probar la aplicación dentro del contenedor Nginx de producción:

```bash
cd frontend
docker build -f docker/Dockerfile -t web-scanner-frontend .
docker run --rm -p 127.0.0.1:8081:8080 web-scanner-frontend
```

Luego abre [http://127.0.0.1:8081/](http://127.0.0.1:8081/) en tu navegador.