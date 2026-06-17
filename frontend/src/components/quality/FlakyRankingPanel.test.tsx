import { fireEvent, render, screen, waitFor, within } from '@testing-library/react';
import { MemoryRouter } from 'react-router-dom';

import { qualityMetricsApi, type FlakyRankingResponse } from '../../api/qualityMetrics';
import { FlakyRankingPanel } from './FlakyRankingPanel';

vi.mock('../../api/qualityMetrics', async () => {
  const actual = await vi.importActual<typeof import('../../api/qualityMetrics')>('../../api/qualityMetrics');
  return {
    ...actual,
    qualityMetricsApi: {
      ...actual.qualityMetricsApi,
      getFlakyRanking: vi.fn(),
    },
  };
});

const responseWithRows: FlakyRankingResponse = {
  entries: [
    {
      test_case_id: '11111111-1111-1111-1111-111111111111',
      external_id: 'TC-1',
      display_name: 'Checkout flow',
      runs: 4,
      flaky_outcomes: 1,
      transitions: 3,
      flip_rate: 1,
      last_outcome: 'failed',
      last_seen_at: '2026-06-17T10:00:00.000Z',
    },
    {
      test_case_id: '22222222-2222-2222-2222-222222222222',
      external_id: 'TC-2',
      display_name: 'Search filters',
      runs: 2,
      flaky_outcomes: 0,
      transitions: 1,
      flip_rate: 0.5,
      last_outcome: 'passed',
      last_seen_at: '2026-06-17T09:00:00.000Z',
    },
  ],
  is_synthetic: false,
  reason: null,
};

describe('FlakyRankingPanel', () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  it('renders ranking rows from API response', async () => {
    vi.mocked(qualityMetricsApi.getFlakyRanking).mockResolvedValue(responseWithRows);

    render(
      <MemoryRouter>
        <FlakyRankingPanel window={30} />
      </MemoryRouter>
    );

    expect(await screen.findByText('Checkout flow')).toBeInTheDocument();
    expect(screen.getByText('Search filters')).toBeInTheDocument();
    expect(screen.getByText('100.0%')).toBeInTheDocument();
  });

  it('shows synthetic empty reason when no entries are returned', async () => {
    vi.mocked(qualityMetricsApi.getFlakyRanking).mockResolvedValue({
      entries: [],
      is_synthetic: true,
      reason: 'requires external case-result outcomes; no execution results are available yet',
    });

    render(
      <MemoryRouter>
        <FlakyRankingPanel window={30} />
      </MemoryRouter>
    );

    expect(await screen.findByText('Flaky Test Ranking')).toBeInTheDocument();
    expect(screen.getByText('requires external case-result outcomes; no execution results are available yet')).toBeInTheDocument();
  });

  it('re-fetches when the selected window changes', async () => {
    vi.mocked(qualityMetricsApi.getFlakyRanking).mockResolvedValue(responseWithRows);

    const { rerender } = render(
      <MemoryRouter>
        <FlakyRankingPanel window={30} />
      </MemoryRouter>
    );

    await waitFor(() => expect(qualityMetricsApi.getFlakyRanking).toHaveBeenCalledWith(30, 10, expect.any(Object)));

    rerender(
      <MemoryRouter>
        <FlakyRankingPanel window={7} />
      </MemoryRouter>
    );

    await waitFor(() => expect(qualityMetricsApi.getFlakyRanking).toHaveBeenCalledWith(7, 10, expect.any(Object)));
  });

  it('sorts rows when a sortable column header is clicked', async () => {
    vi.mocked(qualityMetricsApi.getFlakyRanking).mockResolvedValue(responseWithRows);

    render(
      <MemoryRouter>
        <FlakyRankingPanel window={30} />
      </MemoryRouter>
    );

    await screen.findByText('Checkout flow');
    const bodyRows = () => within(screen.getAllByRole('rowgroup')[1]).getAllByRole('row');

    expect(within(bodyRows()[0]).getByText('Checkout flow')).toBeInTheDocument();
    fireEvent.click(screen.getByRole('button', { name: 'Runs' }));
    fireEvent.click(screen.getByRole('button', { name: 'Runs' }));
    expect(within(bodyRows()[0]).getByText('Search filters')).toBeInTheDocument();
  });
});
