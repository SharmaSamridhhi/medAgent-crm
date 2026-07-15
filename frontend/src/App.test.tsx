import { render, screen } from '@testing-library/react'
import { describe, expect, it } from 'vitest'
import App from './App'

describe('App', () => {
  it('mounts the app shell without error', () => {
    render(<App />)
    expect(
      screen.getByRole('heading', { name: /medAgent-CRM/i }),
    ).toBeInTheDocument()
  })
})
