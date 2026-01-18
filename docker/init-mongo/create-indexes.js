// MongoDB initialization script - creates indexes for the articles collection

db = db.getSiblingDB('intelligence');

// Create articles collection if it doesn't exist
db.createCollection('articles');

// Create indexes
db.articles.createIndex({ "url": 1 }, { unique: true, name: "url_unique" });
db.articles.createIndex({ "publishDate": -1 }, { name: "publishDate_desc" });
db.articles.createIndex({ "classification": 1 }, { name: "classification_idx" });
db.articles.createIndex({ "sentimentScore": 1 }, { name: "sentimentScore_idx" });
db.articles.createIndex({ "source": 1 }, { name: "source_idx" });
db.articles.createIndex({ "status": 1 }, { name: "status_idx" });

// Compound index for common filter queries
db.articles.createIndex(
    { "publishDate": -1, "classification": 1, "sentimentScore": 1 },
    { name: "filter_compound" }
);

// Full-text search index
db.articles.createIndex(
    { "title": "text", "content": "text" },
    { name: "fulltext_search", weights: { title: 10, content: 1 } }
);

print("✓ MongoDB indexes created successfully");
