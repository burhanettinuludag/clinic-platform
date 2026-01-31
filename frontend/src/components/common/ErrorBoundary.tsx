'use client';

import React from 'react';

interface ErrorBoundaryProps {
  children: React.ReactNode;
  fallback?: React.ReactNode;
}

interface ErrorBoundaryState {
  hasError: boolean;
  error: Error | null;
}

class ErrorBoundary extends React.Component<ErrorBoundaryProps, ErrorBoundaryState> {
  constructor(props: ErrorBoundaryProps) {
    super(props);
    this.state = { hasError: false, error: null };
  }

  static getDerivedStateFromError(error: Error): ErrorBoundaryState {
    return { hasError: true, error };
  }

  componentDidCatch(error: Error, errorInfo: React.ErrorInfo): void {
    console.error('ErrorBoundary caught an error:', error, errorInfo);
  }

  render() {
    if (this.state.hasError) {
      if (this.props.fallback) {
        return this.props.fallback;
      }

      return (
        <div className="min-h-screen flex items-center justify-center bg-gray-50 p-4">
          <div className="bg-white rounded-lg shadow-lg p-8 max-w-md w-full text-center">
            <div className="flex justify-center mb-4">
              <svg
                className="h-16 w-16 text-red-500"
                viewBox="0 0 48 48"
                fill="none"
                xmlns="http://www.w3.org/2000/svg"
              >
                <circle cx="24" cy="24" r="22" stroke="currentColor" strokeWidth="3" fill="none" />
                <text
                  x="24"
                  y="32"
                  textAnchor="middle"
                  fontSize="28"
                  fontWeight="bold"
                  fill="currentColor"
                >
                  !
                </text>
              </svg>
            </div>

            <h2 className="text-xl font-semibold text-gray-900 mb-2">Bir hata olustu</h2>

            {this.state.error && (
              <p className="text-sm text-gray-500 mb-6">{this.state.error.message}</p>
            )}

            <div className="flex flex-col gap-3">
              <button
                onClick={() => window.location.reload()}
                className="w-full px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 transition-colors"
              >
                Sayfayi Yenile
              </button>

              <a
                href="/"
                className="text-sm text-blue-600 hover:text-blue-800 transition-colors"
              >
                Ana Sayfaya Don
              </a>
            </div>
          </div>
        </div>
      );
    }

    return this.props.children;
  }
}

export default ErrorBoundary;
