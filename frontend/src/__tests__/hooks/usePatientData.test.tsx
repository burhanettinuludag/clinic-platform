import { renderHook, waitFor } from '@testing-library/react';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { ReactNode } from 'react';
import {
  useDiseaseModules,
  useMigraineStats,
  useMedications,
} from '@/hooks/usePatientData';
import api from '@/lib/api';

// Mock API
jest.mock('@/lib/api', () => ({
  get: jest.fn(),
  post: jest.fn(),
  patch: jest.fn(),
  delete: jest.fn(),
}));

const mockApi = api as jest.Mocked<typeof api>;

// Create a wrapper with QueryClient
function createWrapper() {
  const queryClient = new QueryClient({
    defaultOptions: {
      queries: {
        retry: false,
      },
    },
  });
  return function Wrapper({ children }: { children: ReactNode }) {
    return (
      <QueryClientProvider client={queryClient}>
        {children}
      </QueryClientProvider>
    );
  };
}

describe('usePatientData hooks', () => {
  beforeEach(() => {
    jest.clearAllMocks();
  });

  describe('useDiseaseModules', () => {
    it('fetches disease modules successfully', async () => {
      const mockModules = [
        { id: '1', name_tr: 'Migren', name_en: 'Migraine', slug: 'migraine' },
        { id: '2', name_tr: 'Epilepsi', name_en: 'Epilepsy', slug: 'epilepsy' },
      ];
      mockApi.get.mockResolvedValue({ data: mockModules });

      const { result } = renderHook(() => useDiseaseModules(), {
        wrapper: createWrapper(),
      });

      await waitFor(() => {
        expect(result.current.isSuccess).toBe(true);
      });

      expect(result.current.data).toEqual(mockModules);
      expect(mockApi.get).toHaveBeenCalledWith('/modules/');
    });

    it('handles error when fetching modules fails', async () => {
      mockApi.get.mockRejectedValue(new Error('Network error'));

      const { result } = renderHook(() => useDiseaseModules(), {
        wrapper: createWrapper(),
      });

      await waitFor(() => {
        expect(result.current.isError).toBe(true);
      });
    });
  });

  describe('useMigraineStats', () => {
    it('fetches migraine stats successfully', async () => {
      const mockStats = {
        total_attacks: 15,
        avg_intensity: 6.5,
        avg_duration: 240,
        attacks_this_month: 3,
        attacks_last_month: 5,
        most_common_triggers: [{ name: 'Stress', count: 8 }],
        most_common_location: 'left',
        aura_percentage: 40,
      };
      mockApi.get.mockResolvedValue({ data: mockStats });

      const { result } = renderHook(() => useMigraineStats(), {
        wrapper: createWrapper(),
      });

      await waitFor(() => {
        expect(result.current.isSuccess).toBe(true);
      });

      expect(result.current.data).toEqual(mockStats);
      expect(mockApi.get).toHaveBeenCalledWith('/migraine/attacks/stats/');
    });
  });

  describe('useMedications', () => {
    it('fetches medications successfully', async () => {
      const mockMedications = [
        { id: '1', name: 'Sumatriptan', dosage: '50mg', is_active: true },
        { id: '2', name: 'Topiramate', dosage: '25mg', is_active: true },
      ];
      mockApi.get.mockResolvedValue({ data: mockMedications });

      const { result } = renderHook(() => useMedications(), {
        wrapper: createWrapper(),
      });

      await waitFor(() => {
        expect(result.current.isSuccess).toBe(true);
      });

      expect(result.current.data).toEqual(mockMedications);
      expect(mockApi.get).toHaveBeenCalledWith('/tracking/medications/');
    });
  });
});
