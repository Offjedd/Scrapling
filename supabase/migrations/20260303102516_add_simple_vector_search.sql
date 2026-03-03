/*
  # Simple Vector Search for Laws
  
  Creates a function to search laws using vector similarity.
  Works with the current schema (laws + law_embeddings).
*/

-- Drop old function if exists
DROP FUNCTION IF EXISTS search_similar_articles(vector, float, integer);

-- Create simplified vector search for laws
CREATE OR REPLACE FUNCTION search_similar_laws(
  query_embedding vector(1536),
  match_threshold float DEFAULT 0.3,
  match_count integer DEFAULT 5
)
RETURNS TABLE (
  law_id uuid,
  law_name_ar text,
  law_number text,
  law_url text,
  full_text_ar text,
  similarity float
)
LANGUAGE plpgsql
AS $$
BEGIN
  RETURN QUERY
  SELECT
    l.id as law_id,
    l.name_ar as law_name_ar,
    l.law_number,
    l.url as law_url,
    l.full_text_ar,
    1 - (le.embedding <=> query_embedding) as similarity
  FROM law_embeddings le
  JOIN laws l ON le.law_id = l.id
  WHERE le.embedding IS NOT NULL
    AND 1 - (le.embedding <=> query_embedding) > match_threshold
  ORDER BY le.embedding <=> query_embedding
  LIMIT match_count;
END;
$$;