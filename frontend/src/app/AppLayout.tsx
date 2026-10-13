import { Link, Outlet } from "react-router";

export function AppLayout() {
  return (
    <div className="min-h-screen bg-gray-50">
      <header className="border-b border-gray-200 bg-white">
        <nav className="mx-auto flex max-w-3xl gap-6 px-4 py-3 text-sm">
          <Link to="/">Inicio</Link>
          <Link to="/historial">Historial</Link>
        </nav>
      </header>
      <main>
        <Outlet />
      </main>
    </div>
  );
}