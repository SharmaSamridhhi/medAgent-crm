import { createBrowserRouter } from 'react-router-dom'
import LogInteractionScreen from '../features/logInteraction/LogInteractionScreen'
import NotFoundPage from '../routes/NotFoundPage'

export const router = createBrowserRouter([
  {
    path: '/',
    element: <LogInteractionScreen />,
  },
  {
    path: '*',
    element: <NotFoundPage />,
  },
])
