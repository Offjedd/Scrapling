/*
  # Add Vector Similarity Search Function

  ## Overview
  Creates a PostgreSQL function to search for similar law articles using vector embeddings.
  This enables semantic search capabilities for the AI query system.

  ## Function: search_similar_articles
  - Takes a query embedding vector as input
  - Searches for similar articles using cosine similarity
  - Returns articles with their law information
  - Includes similarity score threshold filtering
  - Ordered by similarity (most similar first)

  ## Parameters
  - query_embedding: vector(1536) - The embedding vector of the user's question
  - match_threshold: float - Minimum similarity score (0-1)
  - match_count: integer - Maximum number of results to return
*/

-- Create function for vector similarity search
CREATE OR REPLACE FUNCTION search_similar_articles(
  query_embedding vector(1536),
  match_threshold float DEFAULT 0.5,
  match_count integer DEFAULT 5
)
RETURNS TABLE (
  article_id uuid,
  law_id uuid,
  law_name_ar text,
  law_name_en text,
  law_number text,
  law_url text,
  publication_date date,
  article_number text,
  article_title_ar text,
  article_text_ar text,
  similarity float
)
LANGUAGE plpgsql
AS $$
BEGIN
  RETURN QUERY
  SELECT
    la.id as article_id,
    la.law_id,
    l.name_ar as law_name_ar,
    l.name_en as law_name_en,
    l.law_number,
    l.url as law_url,
    l.publication_date,
    la.article_number,
    la.article_title_ar,
    la.article_text_ar,
    1 - (le.embedding <=> query_embedding) as similarity
  FROM law_embeddings le
  JOIN law_articles la ON le.article_id = la.id
  JOIN laws l ON la.law_id = l.id
  WHERE 1 - (le.embedding <=> query_embedding) > match_threshold
  ORDER BY le.embedding <=> query_embedding
  LIMIT match_count;
END;
$$;
