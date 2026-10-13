import { useQuery } from '@tanstack/react-query'
import { fetchAnalyses } from '@/features/analysis/api'

export function useAnalyses() {
    return useQuery({
        queryKey: ['analyses'],
        queryFn: fetchAnalyses,
    })
}