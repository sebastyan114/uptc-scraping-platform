import { http, HttpResponse } from 'msw'
import type { components, operations } from '@/lib/api/schema'
import {
    createAnalysis,
    getAnalysis,
    hasActiveAnalysis,
    isBlockedTarget,
    listAnalyses,
} from './fixtures'

function problem(status: number, title: string, detail: string) {
    const body: components['schemas']['ProblemDetail'] = {
        type: 'about:blank',
        title,
        status,
        detail,
    }

    return HttpResponse.json(body, {
        status,
        headers: { 'Content-Type': 'application/problem+json' },
    })
}

export const handlers = [
    http.get('*/api/analyses', () => {
        const body: components['schemas']['Analysis'][] = listAnalyses()
        return HttpResponse.json(body)
    }),

    http.post('*/api/analyses', async ({ request }) => {
        const body = await request.json() as operations['createAnalysis']['requestBody']['content']['application/json']

        if (!body?.targetUrl || isBlockedTarget(body.targetUrl)) {
            return problem(422, 'URL inválida', 'La URL ingresada no es válida o no es accesible.')
        }
        if (hasActiveAnalysis()) {
            return problem(409, 'Análisis en curso', 'Ya hay un análisis en ejecución. Espera a que termine.')
        }
        return HttpResponse.json(createAnalysis(body.targetUrl), { status: 201 })
    }),

    http.get('*/api/analyses/:analysisId', ({ params }) => {
        const found = getAnalysis(params.analysisId as string)
        if (!found) return problem(404, 'Análisis no encontrado', `No existe un análisis con id ${params.analysisId}.`)
        return HttpResponse.json(found)
    }),
]