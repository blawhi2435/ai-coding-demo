/**
 * React Query hook for fetching article detail
 */

import { useQuery } from '@tanstack/react-query';
import apiClient from '../services/api';
import type { Article } from '../types';

export const useArticleDetail = (articleId: string | undefined) => {
  return useQuery<Article>({
    queryKey: ['article', articleId],
    queryFn: async () => {
      if (!articleId) {
        throw new Error('Article ID is required');
      }

      const response = await apiClient.get<Article>(`/api/articles/${encodeURIComponent(articleId)}`);
      return response.data;
    },
    enabled: !!articleId, // Only run query if articleId is provided
    staleTime: 30000, // Cache for 30 seconds
  });
};
