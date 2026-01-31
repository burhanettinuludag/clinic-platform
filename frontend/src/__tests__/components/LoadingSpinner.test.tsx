import { render, screen } from '@testing-library/react';
import LoadingSpinner from '@/components/common/LoadingSpinner';

describe('LoadingSpinner', () => {
  it('renders spinner without text', () => {
    render(<LoadingSpinner />);
    const spinner = document.querySelector('.animate-spin');
    expect(spinner).toBeInTheDocument();
  });

  it('renders spinner with text', () => {
    render(<LoadingSpinner text="Loading..." />);
    expect(screen.getByText('Loading...')).toBeInTheDocument();
  });

  it('renders small size spinner', () => {
    render(<LoadingSpinner size="sm" />);
    const spinner = document.querySelector('.animate-spin');
    expect(spinner).toHaveClass('h-6', 'w-6');
  });

  it('renders medium size spinner by default', () => {
    render(<LoadingSpinner />);
    const spinner = document.querySelector('.animate-spin');
    expect(spinner).toHaveClass('h-10', 'w-10');
  });

  it('renders large size spinner', () => {
    render(<LoadingSpinner size="lg" />);
    const spinner = document.querySelector('.animate-spin');
    expect(spinner).toHaveClass('h-16', 'w-16');
  });
});
