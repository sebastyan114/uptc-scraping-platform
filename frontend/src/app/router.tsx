import { createBrowserRouter } from 'react-router'
import { AppLayout } from '@/app/AppLayout'
import { HomePage } from '@/pages/HomePage'
import { HistoryPage } from '@/pages/HistoryPage'
import { AnalysisDetailPage } from '@/pages/AnalysisDetailPage'
import { NotFoundPage } from '@/pages/NotFoundPage'

export const router = createBrowserRouter([
  {
    path: '/',
    element: <AppLayout />,
    children: [
      { index: true, element: <HomePage /> },
      { path: 'historial', element: <HistoryPage /> },
      { path: 'analisis/:analysisId', element: <AnalysisDetailPage /> },
      { path: '*', element: <NotFoundPage /> },
    ],
  },
])