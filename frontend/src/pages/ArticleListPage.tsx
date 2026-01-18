/**
 * Article List Page
 *
 * Main page displaying the list of articles with filters
 */

import { ArticleList } from '../components/ArticleList';
import { Filters } from '../components/Filters';

export const ArticleListPage = () => {
  return (
    <div className="min-h-screen bg-gray-50">
      <header className="bg-white shadow">
        <div className="max-w-7xl mx-auto py-6 px-4 sm:px-6 lg:px-8">
          <h1 className="text-3xl font-bold text-gray-900">
            Enterprise Data Intelligence
          </h1>
          <p className="mt-1 text-sm text-gray-600">
            Analyze and explore competitive intelligence from NVIDIA Newsroom
          </p>
        </div>
      </header>

      <main className="max-w-7xl mx-auto py-6 sm:px-6 lg:px-8">
        <div className="grid grid-cols-1 lg:grid-cols-4 gap-6">
          {/* Filters sidebar */}
          <aside className="lg:col-span-1">
            <Filters />
          </aside>

          {/* Article list */}
          <div className="lg:col-span-3">
            <ArticleList />
          </div>
        </div>
      </main>
    </div>
  );
};
