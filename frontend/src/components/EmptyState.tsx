export function EmptyState({ title, description }: { title: string; description: string }) {
    return (
        <div className="rounded border border-dashed border-slate-300 p-8 text-center">
            <p className="font-medium text-slate-900">{title}</p>
            <p className="mt-1 text-sm text-slate-600">{description}</p>
        </div>
    )
}