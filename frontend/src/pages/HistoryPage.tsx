import { Link } from 'react-router'
import { useAnalyses } from '@/features/analysis/use-analyses'
import { LoadingState } from '@/components/LoadingState'
import { ErrorState } from '@/components/ErrorState'
import { EmptyState } from '@/components/EmptyState'

export function HistoryPage() {
    const { data: analyses, isPending, isError, error, refetch } = useAnalyses()

    if (isPending) return <LoadingState label="Cargando historial…" />

    if (isError) {
        return (
            <ErrorState
                detail={error instanceof Error ? error.message : 'No se pudo cargar el historial.'}
                onRetry={() => refetch()}
            />
        )
    }

    if (analyses.length === 0) {
        return (
            <EmptyState
                title="Sin análisis todavía"
                description="Crea tu primer análisis desde la página principal."
            />
        )
    }

    return (
        <section>
            <h1 className="text-2xl font-semibold">Historial</h1>
            <ul className="mt-4 divide-y divide-slate-200">
                {analyses.map((analysis) => (
                    <li key={analysis.id} className="py-3">
                        <Link to={`/analisis/${analysis.id}`} className="text-sm underline underline-offset-2">
                            {analysis.targetUrl}
                        </Link>
                        <span className="ml-2 text-sm text-slate-500">({analysis.status})</span>
                    </li>
                ))}
            </ul>
        </section>
    )
}