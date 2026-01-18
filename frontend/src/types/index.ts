/**
 * TypeScript type definitions for the application
 */

export interface Entity {
  text: string;
  type: 'company' | 'person' | 'product' | 'technology';
  mentions: number;
}

export interface Article {
  id: string;
  url: string;
  title: string;
  content: string;
  publishDate: string; // ISO 8601
  source: string;
  summary: string;
  entities: Entity[];
  classification: 'competitive_news' | 'personnel_change' | 'product_launch' | 'market_trend';
  sentimentScore: number; // 1-10
  scrapedAt: string; // ISO 8601
  analyzedAt: string | null; // ISO 8601
  status: 'complete' | 'pending' | 'failed';
  metadata: {
    scraperMethod?: string;
    contentTruncated?: boolean;
    processingTime?: number;
  };
}

export interface ArticleListItem {
  id: string;
  url: string;
  title: string;
  summary: string;
  classification: Article['classification'];
  sentimentScore: number;
  publishDate: string;
  source: string;
  topEntities: string[];
}

export interface PaginatedResponse<T> {
  total: number;
  page: number;
  pageSize: number;
  data: T[];
}

export interface StatsResponse {
  totalArticles: number;
  classificationBreakdown: Record<string, number>;
  avgSentiment: number;
  lastUpdated: string;
}

export interface EntitySummary {
  text: string;
  type: Entity['type'];
  totalMentions: number;
  articleCount: number;
  articleIds: string[];
}

export interface ArticleFilters {
  classification: string | null;
  sentimentRange: [number, number];
  dateRange: {
    start: Date | null;
    end: Date | null;
  };
  searchQuery: string;
}

export interface HealthResponse {
  status: string;
  services: Record<string, string>;
  timestamp: string;
}
