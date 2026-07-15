import { createBrowserRouter } from 'react-router-dom'
import HomePage from '../routes/HomePage'
import NotFoundPage from '../routes/NotFoundPage'

export const router = createBrowserRouter([
  {
    path: '/',
    element: <HomePage />,
  },
  {
    path: '*',
    element: <NotFoundPage />,
  },
])
