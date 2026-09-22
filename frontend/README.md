# Web Scanner - Frontend

Este es el repositorio del frontend para el proyecto Web Scanner, construido con herramientas modernas para garantizar rendimiento, escalabilidad y una excelente experiencia de desarrollo.

##  Tecnologías Usadas

El proyecto utiliza el siguiente stack tecnológico:

- **[React](https://react.dev/)**: Biblioteca principal para construir la interfaz de usuario.
- **[Vite](https://vite.dev/)**: Herramienta de construcción (build tool) y servidor de desarrollo ultrarrápido.
- **[TypeScript](https://www.typescriptlang.org/)**: Tipado estático para JavaScript, previniendo errores y mejorando la experiencia del desarrollador.
- **[React Router](https://reactrouter.com/)**: Enrutamiento de la aplicación (Single Page Application).
- **[Tailwind CSS](https://tailwindcss.com/) v4**: Framework de CSS basado en utilidades para un diseño ágil.
- **[React Query](https://tanstack.com/query/latest)**: Gestión de estado del servidor, caché y sincronización de datos.
- **Oxlint**: Linter ultrarrápido para mantener la calidad del código.
- **Docker & Nginx**: Contenedorización y servidor web ligero para el despliegue a producción.

##  Arquitectura del Frontend

La aplicación sigue una arquitectura modular y escalable. A continuación un diagrama simplificado del flujo principal:

```mermaid
graph TD
    %% Nodos principales
    Main[main.tsx]
    QueryProv(QueryClientProvider)
    RouterProv(RouterProvider)
    RouterDef[app/router.tsx]
    Layout[app/AppLayout.tsx]
    Outlet((Outlet))
    
    %% Páginas
    Home[pages/HomePage.tsx]
    NotFound[pages/NotFoundPage.tsx]
    
    %% Librerías base
    LibQuery[lib/query-client.ts]
    
    %% Relaciones
    Main --> QueryProv
    Main --> RouterProv
    
    QueryProv -. "Inyecta" .-> LibQuery
    RouterProv --> RouterDef
    
    RouterDef --> Layout
    Layout --> Outlet
    
    Outlet -. "Renderiza según ruta" .-> Home
    Outlet -. "Renderiza según ruta" .-> NotFound
```

### Estructura de Carpetas

- `docker/`: Archivos de configuración para el despliegue (Dockerfile, nginx.conf, etc).
- `src/app/`: Configuración global de la aplicación (Enrutador, Layouts principales).
- `src/pages/`: Vistas de nivel superior asociadas a una ruta (e.g., HomePage).
- `src/components/ui/`: Componentes reutilizables e independientes de la interfaz (preparado para shadcn/ui).
- `src/features/`: Módulos o dominios específicos de la aplicación.
- `src/lib/`: Utilidades, clientes globales (ej. cliente de React Query) y configuración de entorno (`env.ts`).

## 🧪 Pruebas y Comprobaciones (Para Testers)

Si necesitas verificar que el entorno y el proyecto están funcionando correctamente, ejecuta los siguientes comandos en orden desde la raíz del proyecto:

### 1. Verificación de Código (Linting)
```bash
npm run lint
```
> **Resultado esperado:** Debe mostrar `Found 0 warnings and 0 errors`.

### 2. Compilación para Producción (Build)
```bash
npm run build
```
> **Resultado esperado:** Compila usando `tsc -b` y `vite build` y debe terminar exitosamente sin arrojar errores de TypeScript ni de empaquetado.

### 3. Servidor de Desarrollo Local
```bash
npm run dev
```
> **Resultado esperado:** Inicia el servidor de desarrollo en `http://localhost:5173/`. Al abrir esta URL en el navegador, debes ver la página inicial que dice "Web Scanner" o "Bienvenido a la página principal".

### 4. Construcción de Imagen Docker
```bash
docker build -f docker/Dockerfile -t web-scanner-frontend .
```
> **Resultado esperado:** Construye la imagen de Docker utilizando las dos etapas (Node.js y Nginx). Debe finalizar exitosamente.

### 5. Ejecución del Contenedor Docker
```bash
docker run --rm -p 127.0.0.1:8081:8080 web-scanner-frontend
```
> **Resultado esperado:** Levanta el contenedor exponiendo el puerto 8081 en tu máquina local. Si abres `http://127.0.0.1:8081/` en el navegador, deberías ver la aplicación servida por Nginx. (Usa `Ctrl+C` en la terminal para detener y eliminar el contenedor temporal).