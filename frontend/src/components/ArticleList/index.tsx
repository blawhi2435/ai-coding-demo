/**
 * ArticleList component
 *
 * Displays a paginated list of articles with loading and error states
 */

import { useState } from 'react';
import { Link } from 'react-router-dom';
import { useArticles } from '../../hooks/useArticles';
import { useFilterStore } from '../../stores/filterStore';
import type { ArticleListItem } from '../../types';

const SENTIMENT_COLORS = {
  low: 'bg-red-100 text-red-800',
  medium: 'bg-yellow-100 text-yellow-800',
  high: 'bg-green-100 text-green-800',
};

const getSentimentColor = (score: number): string => {
  if (score <= 4) return SENTIMENT_COLORS.low;
  if (score <= 7) return SENTIMENT_COLORS.medium;
  return SENTIMENT_COLORS.high;
};

const formatClassification = (classification: string): string => {
  return classification
    .split('_')
    .map((word) => word.charAt(0).toUpperCase() + word.slice(1))
    .join(' ');
};

const ArticleCard = ({ article }: { article: ArticleListItem }) => {
  return (
    <Link
      to={`/articles/${encodeURIComponent(article.id)}`}
      className="block bg-white rounded-lg shadow hover:shadow-md transition-shadow p-6"
    >
      <div className="flex items-start justify-between mb-3">
        <h3 className="text-lg font-semibold text-gray-900 flex-1 mr-4 hover:text-primary-600">
          {article.title}
        </h3>
        <span className={`px-3 py-1 rounded-full text-xs font-medium whitespace-nowrap ${getSentimentColor(article.sentimentScore)}`}>
          Sentiment: {article.sentimentScore}/10
        </span>
      </div>

      <p className="text-gray-600 text-sm mb-4 line-clamp-2">{article.summary}</p>

      <div className="flex flex-wrap items-center gap-3 text-sm text-gray-500">
        <span className="px-2 py-1 bg-primary-100 text-primary-700 rounded">
          {formatClassification(article.classification)}
        </span>

        <span>{article.source}</span>

        <span>{new Date(article.publishDate).toLocaleDateString()}</span>

        {article.topEntities.length > 0 && (
          <div className="flex items-center gap-2">
            <span className="text-gray-400">•</span>
            <div className="flex flex-wrap gap-1">
              {article.topEntities.map((entity, idx) => (
                <span key={idx} className="px-2 py-0.5 bg-gray-100 text-gray-700 rounded text-xs">
                  {entity}
                </span>
              ))}
            </div>
          </div>
        )}
      </div>
    </Link>
  );
};

export const ArticleList = () => {
  const [page, setPage] = useState(1);
  const pageSize = 20;
  const { filters } = useFilterStore();

  const { data, isLoading, error } = useArticles({ page, pageSize, filters });

  if (error) {
    return (
      <div className="bg-red-50 border border-red-200 rounded-lg p-6 text-center">
        <p className="text-red-800 font-medium">Failed to load articles</p>
        <p className="text-red-600 text-sm mt-2">
          {error instanceof Error ? error.message : 'An error occurred'}
        </p>
      </div>
    );
  }

  if (isLoading) {
    return (
      <div className="space-y-4">
        {[...Array(5)].map((_, i) => (
          <div key={i} className="bg-white rounded-lg shadow p-6 animate-pulse">
            <div className="h-6 bg-gray-200 rounded w-3/4 mb-4"></div>
            <div className="h-4 bg-gray-200 rounded w-full mb-2"></div>
            <div className="h-4 bg-gray-200 rounded w-2/3"></div>
          </div>
        ))}
      </div>
    );
  }

  if (!data || data.data.length === 0) {
    return (
      <div className="bg-gray-50 border border-gray-200 rounded-lg p-12 text-center">
        <p className="text-gray-600 text-lg">No articles found</p>
        <p className="text-gray-500 text-sm mt-2">
          Try adjusting your filters or check back later for new articles
        </p>
      </div>
    );
  }

  const totalPages = Math.ceil(data.total / pageSize);

  return (
    <div className="space-y-6">
      {/* Results summary */}
      <div className="flex items-center justify-between">
        <p className="text-sm text-gray-600">
          Showing {((page - 1) * pageSize) + 1} - {Math.min(page * pageSize, data.total)} of {data.total} articles
        </p>
      </div>

      {/* Article cards */}
      <div className="space-y-4">
        {data.data.map((article) => (
          <ArticleCard key={article.id} article={article} />
        ))}
      </div>

      {/* Pagination */}
      {totalPages > 1 && (
        <div className="flex items-center justify-center gap-2">
          <button
            onClick={() => setPage((p) => Math.max(1, p - 1))}
            disabled={page === 1}
            className="px-4 py-2 rounded-md bg-white border border-gray-300 text-gray-700 hover:bg-gray-50 disabled:opacity-50 disabled:cursor-not-allowed"
          >
            Previous
          </button>

          <div className="flex items-center gap-1">
            {[...Array(Math.min(5, totalPages))].map((_, i) => {
              const pageNum = i + 1;
              return (
                <button
                  key={pageNum}
                  onClick={() => setPage(pageNum)}
                  className={`px-3 py-2 rounded-md ${
                    page === pageNum
                      ? 'bg-primary-600 text-white'
                      : 'bg-white border border-gray-300 text-gray-700 hover:bg-gray-50'
                  }`}
                >
                  {pageNum}
                </button>
              );
            })}
            {totalPages > 5 && (
              <>
                <span className="px-2 text-gray-500">...</span>
                <button
                  onClick={() => setPage(totalPages)}
                  className={`px-3 py-2 rounded-md ${
                    page === totalPages
                      ? 'bg-primary-600 text-white'
                      : 'bg-white border border-gray-300 text-gray-700 hover:bg-gray-50'
                  }`}
                >
                  {totalPages}
                </button>
              </>
            )}
          </div>

          <button
            onClick={() => setPage((p) => Math.min(totalPages, p + 1))}
            disabled={page === totalPages}
            className="px-4 py-2 rounded-md bg-white border border-gray-300 text-gray-700 hover:bg-gray-50 disabled:opacity-50 disabled:cursor-not-allowed"
          >
            Next
          </button>
        </div>
      )}
    </div>
  );
};
