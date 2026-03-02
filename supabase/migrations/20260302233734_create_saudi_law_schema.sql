/*
  # Saudi Arabian Law Database Schema

  ## Overview
  This migration creates the complete database structure for storing and querying Saudi Arabian laws
  from the official government website (laws.boe.gov.sa).

  ## 1. New Tables

  ### law_folders (مجلدات الأنظمة)
  - `id` (uuid, primary key) - Unique identifier for each folder
  - `folder_id` (text) - Original folder ID from the website
  - `name_ar` (text) - Folder name in Arabic
  - `name_en` (text) - Folder name in English
  - `url` (text) - Full URL to the folder on the website
  - `created_at` (timestamptz) - When this record was created
  - `updated_at` (timestamptz) - Last update timestamp

  ### laws (الأنظمة)
  - `id` (uuid, primary key) - Unique identifier for each law
  - `law_number` (text) - Official law number/identifier
  - `name_ar` (text) - Law name in Arabic
  - `name_en` (text) - Law name in English
  - `folder_id` (uuid, foreign key) - Reference to parent folder
  - `publication_date` (date) - Official publication date
  - `url` (text) - Full URL to the law document
  - `full_text_ar` (text) - Complete law text in Arabic
  - `full_text_en` (text) - Complete law text in English if available
  - `metadata` (jsonb) - Additional metadata (version, amendments, etc.)
  - `created_at` (timestamptz) - When this record was created
  - `updated_at` (timestamptz) - Last update timestamp
  - `last_checked_at` (timestamptz) - Last time we checked for updates

  ### law_articles (المواد)
  - `id` (uuid, primary key) - Unique identifier for each article
  - `law_id` (uuid, foreign key) - Reference to parent law
  - `article_number` (text) - Article number (e.g., "1", "2", "3/أ")
  - `article_title_ar` (text) - Article title in Arabic if exists
  - `article_text_ar` (text) - Full article text in Arabic
  - `article_text_en` (text) - Article text in English if available
  - `created_at` (timestamptz) - When this record was created
  - `updated_at` (timestamptz) - Last update timestamp

  ### law_embeddings (التضمينات المتجهة)
  - `id` (uuid, primary key) - Unique identifier
  - `article_id` (uuid, foreign key) - Reference to law article
  - `law_id` (uuid, foreign key) - Reference to parent law
  - `embedding` (vector(1536)) - Vector embedding for semantic search
  - `text_chunk` (text) - The text chunk that was embedded
  - `chunk_index` (integer) - Index of chunk within the article
  - `created_at` (timestamptz) - When this record was created

  ### query_logs (سجلات الاستعلامات)
  - `id` (uuid, primary key) - Unique identifier
  - `query_text` (text) - User's question
  - `query_language` (text) - Language of the query (ar/en)
  - `response_text` (text) - AI generated response
  - `cited_articles` (jsonb) - Array of article IDs that were cited
  - `response_time_ms` (integer) - Response time in milliseconds
  - `created_at` (timestamptz) - When this query was made

  ## 2. Security
  - Enable RLS on all tables
  - Add policies for authenticated access to query the system
  - Add policies for system user to manage scraping and updates

  ## 3. Important Notes
  - Arabic text is fully supported with proper UTF-8 encoding
  - Vector embeddings use pgvector extension for semantic search
  - Full-text search indexes on Arabic text fields
  - Indexes on foreign keys and frequently queried fields for performance
*/

-- Enable necessary extensions
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "vector";

-- Create law_folders table
CREATE TABLE IF NOT EXISTS law_folders (
  id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  folder_id text UNIQUE NOT NULL,
  name_ar text NOT NULL,
  name_en text DEFAULT '',
  url text NOT NULL,
  created_at timestamptz DEFAULT now(),
  updated_at timestamptz DEFAULT now()
);

-- Create laws table
CREATE TABLE IF NOT EXISTS laws (
  id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  law_number text DEFAULT '',
  name_ar text NOT NULL,
  name_en text DEFAULT '',
  folder_id uuid REFERENCES law_folders(id) ON DELETE CASCADE,
  publication_date date,
  url text NOT NULL UNIQUE,
  full_text_ar text DEFAULT '',
  full_text_en text DEFAULT '',
  metadata jsonb DEFAULT '{}'::jsonb,
  created_at timestamptz DEFAULT now(),
  updated_at timestamptz DEFAULT now(),
  last_checked_at timestamptz DEFAULT now()
);

-- Create law_articles table
CREATE TABLE IF NOT EXISTS law_articles (
  id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  law_id uuid REFERENCES laws(id) ON DELETE CASCADE NOT NULL,
  article_number text NOT NULL,
  article_title_ar text DEFAULT '',
  article_text_ar text NOT NULL,
  article_text_en text DEFAULT '',
  created_at timestamptz DEFAULT now(),
  updated_at timestamptz DEFAULT now(),
  UNIQUE(law_id, article_number)
);

-- Create law_embeddings table
CREATE TABLE IF NOT EXISTS law_embeddings (
  id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  article_id uuid REFERENCES law_articles(id) ON DELETE CASCADE,
  law_id uuid REFERENCES laws(id) ON DELETE CASCADE NOT NULL,
  embedding vector(1536),
  text_chunk text NOT NULL,
  chunk_index integer DEFAULT 0,
  created_at timestamptz DEFAULT now()
);

-- Create query_logs table
CREATE TABLE IF NOT EXISTS query_logs (
  id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  query_text text NOT NULL,
  query_language text DEFAULT 'ar',
  response_text text,
  cited_articles jsonb DEFAULT '[]'::jsonb,
  response_time_ms integer DEFAULT 0,
  created_at timestamptz DEFAULT now()
);

-- Create indexes for performance
CREATE INDEX IF NOT EXISTS idx_laws_folder_id ON laws(folder_id);
CREATE INDEX IF NOT EXISTS idx_laws_publication_date ON laws(publication_date);
CREATE INDEX IF NOT EXISTS idx_laws_updated_at ON laws(updated_at);
CREATE INDEX IF NOT EXISTS idx_law_articles_law_id ON law_articles(law_id);
CREATE INDEX IF NOT EXISTS idx_law_articles_article_number ON law_articles(article_number);
CREATE INDEX IF NOT EXISTS idx_law_embeddings_article_id ON law_embeddings(article_id);
CREATE INDEX IF NOT EXISTS idx_law_embeddings_law_id ON law_embeddings(law_id);
CREATE INDEX IF NOT EXISTS idx_query_logs_created_at ON query_logs(created_at);

-- Create vector similarity search index
CREATE INDEX IF NOT EXISTS idx_law_embeddings_vector ON law_embeddings USING ivfflat (embedding vector_cosine_ops) WITH (lists = 100);

-- Create full-text search indexes for Arabic content
CREATE INDEX IF NOT EXISTS idx_laws_name_ar_fts ON laws USING gin(to_tsvector('arabic', name_ar));
CREATE INDEX IF NOT EXISTS idx_law_articles_text_ar_fts ON law_articles USING gin(to_tsvector('arabic', article_text_ar));

-- Enable Row Level Security
ALTER TABLE law_folders ENABLE ROW LEVEL SECURITY;
ALTER TABLE laws ENABLE ROW LEVEL SECURITY;
ALTER TABLE law_articles ENABLE ROW LEVEL SECURITY;
ALTER TABLE law_embeddings ENABLE ROW LEVEL SECURITY;
ALTER TABLE query_logs ENABLE ROW LEVEL SECURITY;

-- RLS Policies for public read access (anyone can query laws)
CREATE POLICY "Anyone can view law folders"
  ON law_folders FOR SELECT
  TO public
  USING (true);

CREATE POLICY "Anyone can view laws"
  ON laws FOR SELECT
  TO public
  USING (true);

CREATE POLICY "Anyone can view law articles"
  ON law_articles FOR SELECT
  TO public
  USING (true);

CREATE POLICY "Anyone can view law embeddings"
  ON law_embeddings FOR SELECT
  TO public
  USING (true);

-- RLS Policies for service role to manage data (scraping and updates)
CREATE POLICY "Service role can insert law folders"
  ON law_folders FOR INSERT
  TO service_role
  WITH CHECK (true);

CREATE POLICY "Service role can update law folders"
  ON law_folders FOR UPDATE
  TO service_role
  USING (true)
  WITH CHECK (true);

CREATE POLICY "Service role can insert laws"
  ON laws FOR INSERT
  TO service_role
  WITH CHECK (true);

CREATE POLICY "Service role can update laws"
  ON laws FOR UPDATE
  TO service_role
  USING (true)
  WITH CHECK (true);

CREATE POLICY "Service role can insert law articles"
  ON law_articles FOR INSERT
  TO service_role
  WITH CHECK (true);

CREATE POLICY "Service role can update law articles"
  ON law_articles FOR UPDATE
  TO service_role
  USING (true)
  WITH CHECK (true);

CREATE POLICY "Service role can delete law articles"
  ON law_articles FOR DELETE
  TO service_role
  USING (true);

CREATE POLICY "Service role can insert law embeddings"
  ON law_embeddings FOR INSERT
  TO service_role
  WITH CHECK (true);

CREATE POLICY "Service role can delete law embeddings"
  ON law_embeddings FOR DELETE
  TO service_role
  USING (true);

CREATE POLICY "Service role can insert query logs"
  ON query_logs FOR INSERT
  TO service_role
  WITH CHECK (true);

-- Create a function to update the updated_at timestamp
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
  NEW.updated_at = now();
  RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Create triggers to automatically update updated_at
CREATE TRIGGER update_law_folders_updated_at
  BEFORE UPDATE ON law_folders
  FOR EACH ROW
  EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_laws_updated_at
  BEFORE UPDATE ON laws
  FOR EACH ROW
  EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_law_articles_updated_at
  BEFORE UPDATE ON law_articles
  FOR EACH ROW
  EXECUTE FUNCTION update_updated_at_column();
