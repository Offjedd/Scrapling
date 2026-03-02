import "jsr:@supabase/functions-js/edge-runtime.d.ts";
import { createClient } from "npm:@supabase/supabase-js@2";

const corsHeaders = {
  "Access-Control-Allow-Origin": "*",
  "Access-Control-Allow-Methods": "GET, POST, PUT, DELETE, OPTIONS",
  "Access-Control-Allow-Headers": "Content-Type, Authorization, X-Client-Info, Apikey",
};

interface ArticleRecord {
  id: string;
  law_id: string;
  article_number: string;
  article_title_ar: string;
  article_text_ar: string;
}

Deno.serve(async (req: Request) => {
  if (req.method === "OPTIONS") {
    return new Response(null, {
      status: 200,
      headers: corsHeaders,
    });
  }

  try {
    const supabaseUrl = Deno.env.get("SUPABASE_URL")!;
    const supabaseServiceKey = Deno.env.get("SUPABASE_SERVICE_ROLE_KEY")!;
    const openaiApiKey = Deno.env.get("OPENAI_API_KEY");

    if (!openaiApiKey) {
      throw new Error("OPENAI_API_KEY environment variable is required");
    }

    const supabase = createClient(supabaseUrl, supabaseServiceKey);

    // Get all articles without embeddings
    const { data: articles, error: articlesError } = await supabase
      .from("law_articles")
      .select("id, law_id, article_number, article_title_ar, article_text_ar")
      .limit(100);

    if (articlesError) {
      throw articlesError;
    }

    if (!articles || articles.length === 0) {
      return new Response(
        JSON.stringify({ message: "No articles to process", processed: 0 }),
        {
          headers: {
            ...corsHeaders,
            "Content-Type": "application/json",
          },
        }
      );
    }

    let processed = 0;
    let errors = 0;

    for (const article of articles as ArticleRecord[]) {
      try {
        // Check if embedding already exists
        const { data: existingEmbedding } = await supabase
          .from("law_embeddings")
          .select("id")
          .eq("article_id", article.id)
          .maybeSingle();

        if (existingEmbedding) {
          continue; // Skip if embedding already exists
        }

        // Prepare text for embedding
        const textToEmbed = [
          article.article_title_ar,
          article.article_text_ar,
          `المادة ${article.article_number}`,
        ]
          .filter(Boolean)
          .join(" - ");

        // Generate embedding using OpenAI
        const embeddingResponse = await fetch(
          "https://api.openai.com/v1/embeddings",
          {
            method: "POST",
            headers: {
              "Authorization": `Bearer ${openaiApiKey}`,
              "Content-Type": "application/json",
            },
            body: JSON.stringify({
              model: "text-embedding-3-small",
              input: textToEmbed,
            }),
          }
        );

        if (!embeddingResponse.ok) {
          throw new Error(
            `OpenAI API error: ${embeddingResponse.statusText}`
          );
        }

        const embeddingData = await embeddingResponse.json();
        const embedding = embeddingData.data[0].embedding;

        // Store embedding in database
        const { error: insertError } = await supabase
          .from("law_embeddings")
          .insert({
            article_id: article.id,
            law_id: article.law_id,
            embedding: embedding,
            text_chunk: textToEmbed,
            chunk_index: 0,
          });

        if (insertError) {
          console.error(
            `Error inserting embedding for article ${article.id}:`,
            insertError
          );
          errors++;
        } else {
          processed++;
        }

        // Add small delay to avoid rate limiting
        await new Promise((resolve) => setTimeout(resolve, 100));
      } catch (error) {
        console.error(
          `Error processing article ${article.id}:`,
          error
        );
        errors++;
      }
    }

    return new Response(
      JSON.stringify({
        message: "Embeddings generation completed",
        processed,
        errors,
        total: articles.length,
      }),
      {
        headers: {
          ...corsHeaders,
          "Content-Type": "application/json",
        },
      }
    );
  } catch (error) {
    console.error("Error in generate-embeddings function:", error);

    return new Response(
      JSON.stringify({
        error: error.message || "Internal server error",
      }),
      {
        status: 500,
        headers: {
          ...corsHeaders,
          "Content-Type": "application/json",
        },
      }
    );
  }
});
