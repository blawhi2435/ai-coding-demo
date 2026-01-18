/**
 * React Query hook for fetching articles with filters and pagination
 */

import { useQuery } from '@tanstack/react-query';
import apiClient from '../services/api';
import type { PaginatedResponse, ArticleListItem, ArticleFilters } from '../types';

interface UseArticlesOptions {
  page?: number;
  pageSize?: number;
  filters?: ArticleFilters;
}

export const useArticles = ({ page = 1, pageSize = 20, filters }: UseArticlesOptions = {}) => {
  return useQuery<PaginatedResponse<ArticleListItem>>({
    queryKey: ['articles', page, pageSize, filters],
    queryFn: async () => {
      const params = new URLSearchParams();

      params.append('page', page.toString());
      params.append('pageSize', pageSize.toString());

      // Add filters
      if (filters?.classification) {
        params.append('classification', filters.classification);
      }

      if (filters?.sentimentRange) {
        params.append('minSentiment', filters.sentimentRange[0].toString());
        params.append('maxSentiment', filters.sentimentRange[1].toString());
      }

      if (filters?.dateRange?.start) {
        params.append('startDate', filters.dateRange.start.toISOString());
      }

      if (filters?.dateRange?.end) {
        params.append('endDate', filters.dateRange.end.toISOString());
      }

      if (filters?.searchQuery) {
        params.append('search', filters.searchQuery);
      }

      const response = await apiClient.get<PaginatedResponse<ArticleListItem>>(
        `/api/articles?${params.toString()}`
      );

      return response.data;
    },
    refetchInterval: 5000, // Poll every 5 seconds for new articles
    staleTime: 3000,
  });
};
