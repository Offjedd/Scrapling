/*
  # Article-Level Vector Search Function

  1. Purpose
    - Enables precise semantic search at the article level (not just law level)
    - Returns individual articles with their parent law information
    - Provides better search accuracy for specific legal questions

  2. New Function
    - `search_similar_articles` - Searches law_embeddings joined with law_articles and laws
    - Returns article details with parent law information
    - Uses cosine similarity for vector matching

  3. Performance
    - Leverages vector index on law_embeddings.embedding
    - Efficient joins with proper foreign keys
    - Configurable similarity threshold and result count

  4. Return Structure
    - article_id: UUID of the article
    - law_id: UUID of the parent law
    - law_name_ar: Arabic name of the law
    - law_number: Official law number
    - law_url: Link to the law
    - publication_date: When the law was published
    - article_number: Article number (1, 2, 3, etc.)
    - article_title_ar: Article title if available
    - article_text_ar: Full article text
    - similarity: Match score (0-1, higher is better)
*/

-- Create article-level vector search function
CREATE OR REPLACE FUNCTION search_similar_articles(
  query_embedding vector(1536),
  match_threshold float DEFAULT 0.3,
  match_count integer DEFAULT 10
)
RETURNS TABLE (
  article_id uuid,
  law_id uuid,
  law_name_ar text,
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
    l.id as law_id,
    l.name_ar as law_name_ar,
    l.law_number,
    l.url as law_url,
    l.publication_date,
    la.article_number,
    la.article_title_ar,
    la.article_text_ar,
    1 - (le.embedding <=> query_embedding) as similarity
  FROM law_embeddings le
  LEFT JOIN law_articles la ON le.article_id = la.id
  JOIN laws l ON le.law_id = l.id
  WHERE le.embedding IS NOT NULL
    AND la.id IS NOT NULL
    AND 1 - (le.embedding <=> query_embedding) > match_threshold
  ORDER BY le.embedding <=> query_embedding
  LIMIT match_count;
END;
$$;

-- Add comment to function
COMMENT ON FUNCTION search_similar_articles IS 'Searches for similar law articles using vector embeddings. Returns article-level results with parent law information for precise semantic search.';
