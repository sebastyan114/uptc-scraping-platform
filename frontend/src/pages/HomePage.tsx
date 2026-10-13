import { useState, type FormEvent } from 'react'
import { useNavigate } from 'react-router'
import { useCreateAnalysis } from '@/features/analysis/use-create-analysis'

export function HomePage() {
  const [targetUrl, setTargetUrl] = useState('')
  const navigate = useNavigate()
  const { mutate, isPending, error } = useCreateAnalysis()

  function handleSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault()
    mutate(targetUrl.trim(), {
      onSuccess: (analysis) => navigate(`/analisis/${analysis.id}`),
    })
  }

  return (
    <div className="p-8">
      <h1 className="text-4xl font-bold text-gray-900">Nuevo análisis</h1>
      <p className="mt-2 text-gray-600">Ingresa la URL del sitio que quieres analizar.</p>

      <form onSubmit={handleSubmit} className="mt-6 max-w-md">
        <input
          type="text"
          value={targetUrl}
          onChange={(event) => setTargetUrl(event.target.value)}
          placeholder="https://ejemplo.com"
          disabled={isPending}
          className="w-full rounded border border-gray-300 px-3 py-2 text-sm"
        />

        {error && (
          <p className="mt-2 text-sm text-red-700">
            {error instanceof Error ? error.message : 'No se pudo crear el análisis.'}
          </p>
        )}

        <button
          type="submit"
          disabled={isPending}
          className="mt-4 rounded bg-gray-900 px-4 py-2 text-sm font-medium text-white disabled:opacity-60"
        >
          {isPending ? 'Iniciando…' : 'Iniciar análisis'}
        </button>
      </form>
    </div>
  )
}