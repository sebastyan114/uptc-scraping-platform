import { api } from "@/lib/api-client";

export async function fetchAnalysisDetail(analysisId: string) {
    const { data, error } = await api.GET('/api/analyses/{analysisId}', {
        params: { path: { analysisId } },
    });
    if (error) throw error;
    return data;
}

export async function fetchAnalyses() {
    const { data, error } = await api.GET('/api/analyses')
    if (error) throw error
    return data
}

export async function createAnalysis(targetUrl: string) {
    const { data, error } = await api.POST('/api/analyses', {
        body: { targetUrl },
    })
    if (error) throw error
    return data
}