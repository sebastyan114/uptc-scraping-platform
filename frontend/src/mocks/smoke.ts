import { setupServer } from 'msw/node'
import { handlers } from './handlers'

function assert(condition: unknown, message: string): asserts condition {
    if (!condition) throw new Error(message)
}

const server = setupServer(...handlers)

server.listen({ onUnhandledRequest: 'error' })

try {
    const listResponse = await fetch('http://localhost/api/analyses')
    assert(listResponse.status === 200, 'Expected the analyses list to return 200')
    assert(JSON.stringify(await listResponse.json()) === '[]', 'Expected an empty analyses list')

    const createResponse = await fetch('http://localhost/api/analyses', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ targetUrl: 'https://example.com' }),
    })
    assert(createResponse.status === 201, 'Expected analysis creation to return 201')
    const created = await createResponse.json() as { id: string }
    assert(Boolean(created.id), 'Expected the created analysis to have an id')

    const conflictResponse = await fetch('http://localhost/api/analyses', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ targetUrl: 'https://example.org' }),
    })
    assert(conflictResponse.status === 409, 'Expected a conflict while an analysis is active')

    const detailResponse = await fetch(`http://localhost/api/analyses/${created.id}`)
    assert(detailResponse.status === 200, 'Expected the analysis detail to return 200')

    const missingResponse = await fetch('http://localhost/api/analyses/missing')
    assert(missingResponse.status === 404, 'Expected a missing analysis to return 404')

    console.log('Mock handlers smoke test passed')
} finally {
    server.close()
}