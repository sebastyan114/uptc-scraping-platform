export function ErrorState({ detail, onRetry }: { detail: string; onRetry: () => void }) {
    return (
        <div className="rounded border border-red-200 bg-red-50 p-4" role="alert">
            <p className="text-sm text-red-800">{detail}</p>
            <button
                type="button"
                onClick={onRetry}
                className="mt-2 text-sm font-medium text-red-800 underline underline-offset-2"
            >
                Reintentar
            </button>
        </div>
    )
}