export function LoadingState({ label = 'Cargando…' }: { label?: string }) {
    return (
        <p className="py-8 text-sm text-slate-500" role="status">
            {label}
        </p>
    )
}