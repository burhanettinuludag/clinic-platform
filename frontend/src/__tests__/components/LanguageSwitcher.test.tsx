import { render, screen, fireEvent } from '@testing-library/react';
import LanguageSwitcher from '@/components/common/LanguageSwitcher';

// Mock i18n modules
const mockReplace = jest.fn();
jest.mock('@/i18n/navigation', () => ({
  useRouter: () => ({
    replace: mockReplace,
  }),
  usePathname: () => '/test-path',
}));

jest.mock('@/i18n/routing', () => ({
  routing: {
    locales: ['tr', 'en'],
  },
}));

jest.mock('next-intl', () => ({
  useLocale: () => 'tr',
}));

describe('LanguageSwitcher', () => {
  beforeEach(() => {
    mockReplace.mockClear();
  });

  it('renders language buttons', () => {
    render(<LanguageSwitcher />);
    expect(screen.getByText('TR')).toBeInTheDocument();
    expect(screen.getByText('EN')).toBeInTheDocument();
  });

  it('highlights current locale', () => {
    render(<LanguageSwitcher />);
    const trButton = screen.getByText('TR');
    expect(trButton).toHaveClass('bg-blue-600', 'text-white');
  });

  it('calls router.replace when clicking a language button', () => {
    render(<LanguageSwitcher />);
    const enButton = screen.getByText('EN');
    fireEvent.click(enButton);
    expect(mockReplace).toHaveBeenCalledWith('/test-path', { locale: 'en' });
  });
});
