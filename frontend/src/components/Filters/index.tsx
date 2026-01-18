/**
 * Filters component for article filtering
 *
 * Provides controls for filtering articles by classification, sentiment, and date range
 */

import { useFilterStore } from '../../stores/filterStore';

const CLASSIFICATIONS = [
  { value: 'competitive_news', label: 'Competitive News' },
  { value: 'personnel_change', label: 'Personnel Change' },
  { value: 'product_launch', label: 'Product Launch' },
  { value: 'market_trend', label: 'Market Trend' },
];

export const Filters = () => {
  const { filters, setFilters, resetFilters } = useFilterStore();

  return (
    <div className="bg-white rounded-lg shadow p-6 space-y-6">
      <div className="flex items-center justify-between">
        <h2 className="text-lg font-semibold text-gray-900">Filters</h2>
        <button
          onClick={resetFilters}
          className="text-sm text-primary-600 hover:text-primary-700 font-medium"
        >
          Reset All
        </button>
      </div>

      {/* Classification Filter */}
      <div>
        <label className="block text-sm font-medium text-gray-700 mb-2">
          Classification
        </label>
        <select
          value={filters.classification || ''}
          onChange={(e) => setFilters({ classification: e.target.value || null })}
          className="w-full rounded-md border-gray-300 shadow-sm focus:border-primary-500 focus:ring-primary-500"
        >
          <option value="">All Classifications</option>
          {CLASSIFICATIONS.map((cls) => (
            <option key={cls.value} value={cls.value}>
              {cls.label}
            </option>
          ))}
        </select>
      </div>

      {/* Sentiment Range Filter */}
      <div>
        <label className="block text-sm font-medium text-gray-700 mb-2">
          Sentiment Score: {filters.sentimentRange[0]} - {filters.sentimentRange[1]}
        </label>
        <div className="space-y-2">
          <div>
            <label className="text-xs text-gray-600">Min: {filters.sentimentRange[0]}</label>
            <input
              type="range"
              min="1"
              max="10"
              value={filters.sentimentRange[0]}
              onChange={(e) =>
                setFilters({
                  sentimentRange: [parseInt(e.target.value), filters.sentimentRange[1]],
                })
              }
              className="w-full h-2 bg-gray-200 rounded-lg appearance-none cursor-pointer"
            />
          </div>
          <div>
            <label className="text-xs text-gray-600">Max: {filters.sentimentRange[1]}</label>
            <input
              type="range"
              min="1"
              max="10"
              value={filters.sentimentRange[1]}
              onChange={(e) =>
                setFilters({
                  sentimentRange: [filters.sentimentRange[0], parseInt(e.target.value)],
                })
              }
              className="w-full h-2 bg-gray-200 rounded-lg appearance-none cursor-pointer"
            />
          </div>
        </div>
      </div>

      {/* Date Range Filter */}
      <div>
        <label className="block text-sm font-medium text-gray-700 mb-2">Date Range</label>
        <div className="space-y-2">
          <div>
            <label className="text-xs text-gray-600">From</label>
            <input
              type="date"
              value={filters.dateRange.start?.toISOString().split('T')[0] || ''}
              onChange={(e) =>
                setFilters({
                  dateRange: {
                    ...filters.dateRange,
                    start: e.target.value ? new Date(e.target.value) : null,
                  },
                })
              }
              className="w-full rounded-md border-gray-300 shadow-sm focus:border-primary-500 focus:ring-primary-500"
            />
          </div>
          <div>
            <label className="text-xs text-gray-600">To</label>
            <input
              type="date"
              value={filters.dateRange.end?.toISOString().split('T')[0] || ''}
              onChange={(e) =>
                setFilters({
                  dateRange: {
                    ...filters.dateRange,
                    end: e.target.value ? new Date(e.target.value) : null,
                  },
                })
              }
              className="w-full rounded-md border-gray-300 shadow-sm focus:border-primary-500 focus:ring-primary-500"
            />
          </div>
        </div>
      </div>

      {/* Search Filter */}
      <div>
        <label className="block text-sm font-medium text-gray-700 mb-2">Search</label>
        <input
          type="text"
          placeholder="Search articles..."
          value={filters.searchQuery}
          onChange={(e) => setFilters({ searchQuery: e.target.value })}
          className="w-full rounded-md border-gray-300 shadow-sm focus:border-primary-500 focus:ring-primary-500"
        />
      </div>
    </div>
  );
};
