export async function enableMocking(): Promise<void> {
    const shouldMock = import.meta.env.DEV && import.meta.env.VITE_USE_MOCKS !== 'false'
    if (!shouldMock) return
    const { worker } = await import('@/mocks/browser')
    await worker.start({ onUnhandledRequest: 'bypass', quiet: true })
}