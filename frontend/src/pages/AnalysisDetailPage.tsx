import { Link, useParams } from 'react-router'
import { useAnalysisDetail } from '@/features/analysis/use-analysis-detail'
import { LoadingState } from '@/components/LoadingState'
import { ErrorState } from '@/components/ErrorState'

const STATUS_LABEL: Record<string, string> = {
  pending: 'En cola',
  running: 'Analizando…',
  completed: 'Completado',
  failed: 'Falló',
}

export function AnalysisDetailPage() {
  const { analysisId } = useParams<{ analysisId: string }>()
  const { data: analysis, isPending, isError, error, refetch } = useAnalysisDetail(analysisId)

  if (isPending) return <LoadingState label="Cargando análisis…" />

  if (isError) {
    return (
      <ErrorState
        detail={error instanceof Error ? error.message : 'No se pudo cargar el análisis.'}
        onRetry={() => refetch()}
      />
    )
  }

  return (
    <section>
      <Link to="/historial" className="text-sm underline underline-offset-2">
        ← Volver al historial
      </Link>

      <h1 className="mt-2 text-2xl font-semibold">{analysis.targetUrl}</h1>
      <p className="mt-1 text-sm text-slate-600">
        Estado: {STATUS_LABEL[analysis.status] ?? analysis.status}
      </p>

      {analysis.status === 'failed' && analysis.errorMessage && (
        <p role="alert" className="mt-4 text-sm text-red-700">
          {analysis.errorMessage}
        </p>
      )}

      <div className="mt-6">
        <h2 className="text-sm font-semibold text-slate-900">Protecciones detectadas</h2>
        <p className="mt-1 text-sm text-slate-500">
          {analysis.protections?.length ?? 0} mecanismo(s) encontrado(s).
        </p>
      </div>

      <div className="mt-6">
        <h2 className="text-sm font-semibold text-slate-900">Vulnerabilidades</h2>
        <p className="mt-1 text-sm text-slate-500">
          {analysis.vulnerabilities?.length ?? 0} hallazgo(s) encontrado(s).
        </p>
      </div>
    </section>
  )
}