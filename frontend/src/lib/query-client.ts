import { QueryClient } from '@tanstack/react-query'

export const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      staleTime: 30_000, // 30 segundos
      retry: 1, // reintentar 1 vez en caso de error
      refetchOnWindowFocus: false, // No reintentar cuando la ventana del navegador recupere el foco
    },
  },
})
