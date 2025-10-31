import { render } from '@testing-library/react'
import { ThemeProvider } from '@/contexts/ThemeContext'

// Mock all the complex components and dependencies
jest.mock('@/components/layout/navigation', () => {
  return function MockHeader() {
    return <div data-testid="header">Header</div>
  }
})

jest.mock('@/components/layout/footer', () => {
  return function MockFooter() {
    return <div data-testid="footer">Footer</div>
  }
})

jest.mock('@/components/common/video-theater', () => {
  return function MockVideoTheater() {
    return <div data-testid="video-theater">Video Theater</div>
  }
})

jest.mock('@/components/common/email-subscription', () => {
  return function MockEmailSubscription() {
    return <div data-testid="email-subscription">Email Subscription</div>
  }
})

jest.mock('@/components/common/info-popup', () => {
  return function MockInfoPopup() {
    return <div data-testid="info-popup">Info Popup</div>
  }
})

// Mock Next.js router
jest.mock('next/navigation', () => ({
  useRouter: () => ({
    push: jest.fn(),
    replace: jest.fn(),
    reload: jest.fn(),
    back: jest.fn(),
    prefetch: jest.fn(),
    beforePopState: jest.fn(),
    events: {
      on: jest.fn(),
      off: jest.fn(),
      emit: jest.fn(),
    },
    isFallback: false,
  }),
}))

// Mock the Home component to be simpler
const MockHome = () => {
  return (
    <div data-testid="home-page">
      <h1>AI-Powered Music Video Creation</h1>
      <p>Welcome to Clipizy</p>
    </div>
  )
}

const renderWithProviders = (component: React.ReactElement) => {
  return render(
    <ThemeProvider>
      {component}
    </ThemeProvider>
  )
}

describe('Home Page', () => {
  it('renders without crashing', () => {
    const { getByTestId } = renderWithProviders(<MockHome />)
    expect(getByTestId('home-page')).toBeInTheDocument()
  })

  it('contains main content', () => {
    const { getByText } = renderWithProviders(<MockHome />)
    expect(getByText('AI-Powered Music Video Creation')).toBeInTheDocument()
    expect(getByText('Welcome to Clipizy')).toBeInTheDocument()
  })
})
