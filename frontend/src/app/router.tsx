import { createBrowserRouter } from 'react-router-dom'
import HcpAdminPage from '../features/hcpAdmin/HcpAdminPage'
import LogInteractionScreen from '../features/logInteraction/LogInteractionScreen'
import NotFoundPage from '../routes/NotFoundPage'

export const router = createBrowserRouter([
  {
    path: '/',
    element: <LogInteractionScreen />,
  },
  {
    path: '/hcps',
    element: <HcpAdminPage />,
  },
  {
    path: '*',
    element: <NotFoundPage />,
  },
])
