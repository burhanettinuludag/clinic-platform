import { render, screen, waitFor, act } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { AuthProvider, useAuth } from '@/context/AuthContext';
import Cookies from 'js-cookie';
import api from '@/lib/api';

// Mock API
jest.mock('@/lib/api', () => ({
  get: jest.fn(),
  post: jest.fn(),
}));

const mockApi = api as jest.Mocked<typeof api>;
const mockCookies = Cookies as jest.Mocked<typeof Cookies>;

// Test component that uses auth context
function TestComponent() {
  const { user, isLoading, login, logout } = useAuth();

  if (isLoading) return <div>Loading...</div>;

  return (
    <div>
      {user ? (
        <>
          <div data-testid="user-email">{user.email}</div>
          <button onClick={logout}>Logout</button>
        </>
      ) : (
        <>
          <div>Not logged in</div>
          <button onClick={() => login('test@example.com', 'password')}>
            Login
          </button>
        </>
      )}
    </div>
  );
}

describe('AuthContext', () => {
  beforeEach(() => {
    jest.clearAllMocks();
    mockCookies.get = jest.fn().mockReturnValue(undefined);
  });

  it('shows loading state initially when token exists', async () => {
    mockCookies.get = jest.fn().mockReturnValue('fake-token');
    mockApi.get.mockImplementation(
      () => new Promise((resolve) => setTimeout(() => resolve({ data: { email: 'test@example.com' } }), 100))
    );

    render(
      <AuthProvider>
        <TestComponent />
      </AuthProvider>
    );

    expect(screen.getByText('Loading...')).toBeInTheDocument();
  });

  it('shows not logged in when no token', async () => {
    mockCookies.get = jest.fn().mockReturnValue(undefined);

    render(
      <AuthProvider>
        <TestComponent />
      </AuthProvider>
    );

    await waitFor(() => {
      expect(screen.getByText('Not logged in')).toBeInTheDocument();
    });
  });

  it('fetches user data when token exists', async () => {
    mockCookies.get = jest.fn().mockReturnValue('fake-token');
    mockApi.get.mockResolvedValue({
      data: { email: 'user@example.com', role: 'patient' },
    });

    render(
      <AuthProvider>
        <TestComponent />
      </AuthProvider>
    );

    await waitFor(() => {
      expect(screen.getByTestId('user-email')).toHaveTextContent('user@example.com');
    });
  });

  it('handles login', async () => {
    const user = userEvent.setup();
    mockCookies.get = jest.fn().mockReturnValue(undefined);
    mockApi.post.mockResolvedValue({
      data: {
        user: { email: 'test@example.com', role: 'patient' },
        tokens: { access: 'access-token', refresh: 'refresh-token' },
      },
    });

    render(
      <AuthProvider>
        <TestComponent />
      </AuthProvider>
    );

    await waitFor(() => {
      expect(screen.getByText('Not logged in')).toBeInTheDocument();
    });

    await user.click(screen.getByText('Login'));

    await waitFor(() => {
      expect(screen.getByTestId('user-email')).toHaveTextContent('test@example.com');
    });

    expect(mockCookies.set).toHaveBeenCalledWith('access_token', 'access-token');
    expect(mockCookies.set).toHaveBeenCalledWith('refresh_token', 'refresh-token');
  });

  it('handles logout', async () => {
    const user = userEvent.setup();
    mockCookies.get = jest.fn()
      .mockReturnValueOnce('fake-token')  // Initial check
      .mockReturnValue('refresh-token');  // For logout
    mockApi.get.mockResolvedValue({
      data: { email: 'user@example.com', role: 'patient' },
    });
    mockApi.post.mockResolvedValue({});

    render(
      <AuthProvider>
        <TestComponent />
      </AuthProvider>
    );

    await waitFor(() => {
      expect(screen.getByTestId('user-email')).toBeInTheDocument();
    });

    await user.click(screen.getByText('Logout'));

    await waitFor(() => {
      expect(screen.getByText('Not logged in')).toBeInTheDocument();
    });

    expect(mockCookies.remove).toHaveBeenCalledWith('access_token');
    expect(mockCookies.remove).toHaveBeenCalledWith('refresh_token');
  });

  it('throws error when useAuth is used outside provider', () => {
    const consoleSpy = jest.spyOn(console, 'error').mockImplementation(() => {});

    expect(() => {
      render(<TestComponent />);
    }).toThrow('useAuth must be used within an AuthProvider');

    consoleSpy.mockRestore();
  });
});
