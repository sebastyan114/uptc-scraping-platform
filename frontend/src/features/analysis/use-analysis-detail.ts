import { useQuery } from '@tanstack/react-query'
import { fetchAnalysisDetail } from '@/features/analysis/api'

export function useAnalysisDetail(analysisId: string | undefined) {
    return useQuery({
        queryKey: ['analyses', analysisId],
        queryFn: () => fetchAnalysisDetail(analysisId as string),
        enabled: !!analysisId,
        refetchInterval: 1000,
    })
}