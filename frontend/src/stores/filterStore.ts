/**
 * Zustand store for article filter state
 */

import { create } from 'zustand';
import { ArticleFilters } from '../types';

interface FilterStore {
  filters: ArticleFilters;
  setFilters: (filters: Partial<ArticleFilters>) => void;
  resetFilters: () => void;
}

const defaultFilters: ArticleFilters = {
  classification: null,
  sentimentRange: [1, 10],
  dateRange: {
    start: null,
    end: null,
  },
  searchQuery: '',
};

export const useFilterStore = create<FilterStore>((set) => ({
  filters: defaultFilters,
  setFilters: (newFilters) =>
    set((state) => ({
      filters: { ...state.filters, ...newFilters },
    })),
  resetFilters: () => set({ filters: defaultFilters }),
}));
