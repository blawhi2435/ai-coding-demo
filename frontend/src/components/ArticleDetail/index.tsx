/**
 * ArticleDetail component
 *
 * Displays full article details with entity highlighting
 */

import { Link, useParams } from 'react-router-dom';
import { useArticleDetail } from '../../hooks/useArticleDetail';
import type { Entity } from '../../types';

const ENTITY_TYPE_COLORS = {
  company: 'bg-blue-100 text-blue-800 border-blue-300',
  person: 'bg-purple-100 text-purple-800 border-purple-300',
  product: 'bg-green-100 text-green-800 border-green-300',
  technology: 'bg-orange-100 text-orange-800 border-orange-300',
};

const getSentimentLabel = (score: number): string => {
  if (score <= 3) return 'Negative';
  if (score <= 4) return 'Somewhat Negative';
  if (score <= 6) return 'Neutral';
  if (score <= 8) return 'Positive';
  return 'Very Positive';
};

const formatClassification = (classification: string): string => {
  return classification
    .split('_')
    .map((word) => word.charAt(0).toUpperCase() + word.slice(1))
    .join(' ');
};

const EntityBadge = ({ entity }: { entity: Entity }) => {
  const colorClass = ENTITY_TYPE_COLORS[entity.type as keyof typeof ENTITY_TYPE_COLORS] || 'bg-gray-100 text-gray-800 border-gray-300';

  return (
    <div className={`inline-flex items-center gap-2 px-3 py-1.5 rounded-lg border ${colorClass}`}>
      <span className="font-medium">{entity.text}</span>
      <span className="text-xs opacity-75">
        {entity.type} • {entity.mentions} mention{entity.mentions !== 1 ? 's' : ''}
      </span>
    </div>
  );
};

export const ArticleDetail = () => {
  const { id } = useParams<{ id: string }>();
  const { data: article, isLoading, error } = useArticleDetail(id);

  if (error) {
    return (
      <div className="max-w-4xl mx-auto">
        <div className="bg-red-50 border border-red-200 rounded-lg p-8 text-center">
          <p className="text-red-800 font-medium text-lg">Failed to load article</p>
          <p className="text-red-600 mt-2">
            {error instanceof Error ? error.message : 'An error occurred'}
          </p>
          <Link
            to="/"
            className="inline-block mt-4 px-4 py-2 bg-red-600 text-white rounded-md hover:bg-red-700"
          >
            Back to Articles
          </Link>
        </div>
      </div>
    );
  }

  if (isLoading) {
    return (
      <div className="max-w-4xl mx-auto">
        <div className="bg-white rounded-lg shadow p-8 animate-pulse">
          <div className="h-8 bg-gray-200 rounded w-3/4 mb-6"></div>
          <div className="h-4 bg-gray-200 rounded w-full mb-3"></div>
          <div className="h-4 bg-gray-200 rounded w-full mb-3"></div>
          <div className="h-4 bg-gray-200 rounded w-2/3 mb-8"></div>
          <div className="h-32 bg-gray-200 rounded"></div>
        </div>
      </div>
    );
  }

  if (!article) {
    return (
      <div className="max-w-4xl mx-auto">
        <div className="bg-gray-50 border border-gray-200 rounded-lg p-8 text-center">
          <p className="text-gray-600 text-lg">Article not found</p>
          <Link
            to="/"
            className="inline-block mt-4 px-4 py-2 bg-primary-600 text-white rounded-md hover:bg-primary-700"
          >
            Back to Articles
          </Link>
        </div>
      </div>
    );
  }

  return (
    <div className="max-w-4xl mx-auto space-y-6">
      {/* Back button */}
      <Link to="/" className="inline-flex items-center text-primary-600 hover:text-primary-700">
        <svg className="w-5 h-5 mr-1" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 19l-7-7 7-7" />
        </svg>
        Back to Articles
      </Link>

      {/* Article header */}
      <div className="bg-white rounded-lg shadow p-8">
        <h1 className="text-3xl font-bold text-gray-900 mb-4">{article.title}</h1>

        {/* Metadata */}
        <div className="flex flex-wrap items-center gap-4 text-sm text-gray-600 mb-6">
          <span className="flex items-center">
            <svg className="w-4 h-4 mr-1" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8 7V3m8 4V3m-9 8h10M5 21h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v12a2 2 0 002 2z" />
            </svg>
            {new Date(article.publishDate).toLocaleDateString('en-US', {
              year: 'numeric',
              month: 'long',
              day: 'numeric',
            })}
          </span>

          <span>•</span>

          <span>{article.source}</span>

          <span>•</span>

          <span className="px-2 py-1 bg-primary-100 text-primary-700 rounded">
            {formatClassification(article.classification)}
          </span>

          <span>•</span>

          <span className="font-medium">
            Sentiment: {article.sentimentScore}/10 ({getSentimentLabel(article.sentimentScore)})
          </span>
        </div>

        {/* Summary */}
        <div className="bg-gray-50 border-l-4 border-primary-500 p-4 mb-6">
          <p className="text-gray-700 italic">{article.summary}</p>
        </div>

        {/* Entities */}
        {article.entities && article.entities.length > 0 && (
          <div className="mb-6">
            <h2 className="text-lg font-semibold text-gray-900 mb-3">Entities</h2>
            <div className="flex flex-wrap gap-2">
              {article.entities
                .sort((a, b) => b.mentions - a.mentions)
                .map((entity, idx) => (
                  <EntityBadge key={idx} entity={entity} />
                ))}
            </div>
          </div>
        )}

        {/* Content */}
        <div className="prose prose-gray max-w-none">
          <h2 className="text-xl font-semibold text-gray-900 mb-4">Full Article</h2>
          <div className="text-gray-700 whitespace-pre-wrap leading-relaxed">
            {article.content}
          </div>
        </div>

        {/* Footer */}
        <div className="mt-8 pt-6 border-t border-gray-200">
          <div className="flex items-center justify-between text-sm text-gray-500">
            <div>
              <a
                href={article.url}
                target="_blank"
                rel="noopener noreferrer"
                className="text-primary-600 hover:text-primary-700 inline-flex items-center"
              >
                View original article
                <svg className="w-4 h-4 ml-1" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M10 6H6a2 2 0 00-2 2v10a2 2 0 002 2h10a2 2 0 002-2v-4M14 4h6m0 0v6m0-6L10 14" />
                </svg>
              </a>
            </div>
            <div>
              Scraped: {new Date(article.scrapedAt).toLocaleString()}
              {article.analyzedAt && (
                <> • Analyzed: {new Date(article.analyzedAt).toLocaleString()}</>
              )}
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};
