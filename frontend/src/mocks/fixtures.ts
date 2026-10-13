// src/mocks/fixtures.ts
import type { components } from '@/lib/api/schema'

type AnalysisDetail = components['schemas']['AnalysisDetail']
const store = new Map<string, AnalysisDetail>()

// Tiempos cortos a propósito: para probar la pantalla de progreso en segundos, no en minutos.
const STEP_MS = 2000

export function listAnalyses(): components['schemas']['Analysis'][] {
	return Array.from(store.values()).map(({ protections: _protections, vulnerabilities: _vulnerabilities, errorMessage: _errorMessage, ...analysis }) => analysis)
}

export function createAnalysis(targetUrl: string): components['schemas']['Analysis'] {
	const analysis: AnalysisDetail = {
		id: crypto.randomUUID(),
		targetUrl,
		status: 'pending',
		createdAt: new Date().toISOString(),
		finishedAt: null,
	}

	store.set(analysis.id, analysis)
	simulateProgress(analysis.id)
	return analysis
}

// Sin esto, un análisis creado se queda en 'pending' para siempre: nada más
// en este archivo cambia su estado una vez que ya existe.
function simulateProgress(analysisId: string): void {
	setTimeout(() => {
		const current = store.get(analysisId)
		if (!current) return // pudo eliminarse o nunca más consultarse; no hace falta seguir
		store.set(analysisId, { ...current, status: 'running' })

		setTimeout(() => {
			const running = store.get(analysisId)
			if (!running) return
			store.set(analysisId, {
				...running,
				status: 'completed',
				finishedAt: new Date().toISOString(),
				protections: [{ type: 'waf', details: 'Cloudflare WAF detectado' }],
				vulnerabilities: [
					{
						type: 'sql-injection',
						severity: 'high',
						description: 'Inyección SQL detectada en parámetro de búsqueda',
					},
				]
			})
		}, STEP_MS)
	}, STEP_MS)
}

export function getAnalysis(analysisId: string): AnalysisDetail | undefined {
	return store.get(analysisId)
}

export function hasActiveAnalysis(): boolean {
	return Array.from(store.values()).some(({ status }) => status === 'pending' || status === 'running')
}

export function isBlockedTarget(targetUrl: string): boolean {
	try {
		const url = new URL(targetUrl)
		if (!['http:', 'https:'].includes(url.protocol)) return true

		const hostname = url.hostname.toLowerCase()
		return hostname === 'localhost'
			|| hostname === '::1'
			|| hostname === '127.0.0.1'
			|| hostname.startsWith('10.')
			|| hostname.startsWith('192.168.')
			|| hostname.startsWith('172.16.')
			|| hostname.startsWith('172.17.')
			|| hostname.startsWith('172.18.')
			|| hostname.startsWith('172.19.')
			|| hostname.startsWith('172.2')
			|| hostname.startsWith('172.3')
	} catch {
		return true
	}
}