import "jsr:@supabase/functions-js/edge-runtime.d.ts";
import { createClient } from "npm:@supabase/supabase-js@2";

const corsHeaders = {
  "Access-Control-Allow-Origin": "*",
  "Access-Control-Allow-Methods": "GET, POST, PUT, DELETE, OPTIONS",
  "Access-Control-Allow-Headers": "Content-Type, Authorization, X-Client-Info, Apikey",
};

interface QueryRequest {
  question: string;
  language?: string;
  max_results?: number;
}

interface LawArticleResult {
  article_id: string;
  law_id: string;
  law_name_ar: string;
  law_name_en: string;
  law_number: string;
  law_url: string;
  publication_date: string;
  article_number: string;
  article_title_ar: string;
  article_text_ar: string;
  similarity: number;
}

Deno.serve(async (req: Request) => {
  if (req.method === "OPTIONS") {
    return new Response(null, {
      status: 200,
      headers: corsHeaders,
    });
  }

  const startTime = Date.now();

  try {
    const supabaseUrl = Deno.env.get("SUPABASE_URL")!;
    const supabaseServiceKey = Deno.env.get("SUPABASE_SERVICE_ROLE_KEY")!;
    const openaiApiKey = Deno.env.get("OPENAI_API_KEY");

    if (!openaiApiKey) {
      throw new Error("OPENAI_API_KEY environment variable is required");
    }

    const supabase = createClient(supabaseUrl, supabaseServiceKey);

    // Parse request body
    const { question, language = "ar", max_results = 5 }: QueryRequest =
      await req.json();

    if (!question || question.trim().length === 0) {
      return new Response(
        JSON.stringify({ error: "Question is required" }),
        {
          status: 400,
          headers: {
            ...corsHeaders,
            "Content-Type": "application/json",
          },
        }
      );
    }

    console.log(`Processing question: ${question}`);

    // Step 1: Generate embedding for the question
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
          input: question,
        }),
      }
    );

    if (!embeddingResponse.ok) {
      throw new Error(`OpenAI API error: ${embeddingResponse.statusText}`);
    }

    const embeddingData = await embeddingResponse.json();
    const questionEmbedding = embeddingData.data[0].embedding;

    // Step 2: Find similar articles using vector similarity search
    const { data: similarArticles, error: searchError } = await supabase.rpc(
      "search_similar_articles",
      {
        query_embedding: questionEmbedding,
        match_threshold: 0.5,
        match_count: max_results,
      }
    );

    if (searchError) {
      // If RPC function doesn't exist, fall back to direct query
      console.error("RPC function error:", searchError);

      // Use alternative approach with raw SQL
      const { data: articles, error: altError } = await supabase
        .from("law_embeddings")
        .select(
          `
          id,
          article_id,
          law_id,
          text_chunk,
          law_articles!inner(
            article_number,
            article_title_ar,
            article_text_ar,
            laws!inner(
              name_ar,
              name_en,
              law_number,
              url,
              publication_date
            )
          )
        `
        )
        .limit(max_results);

      if (altError) throw altError;

      // Format results
      const formattedResults = articles?.map((item: any) => ({
        article_id: item.article_id,
        law_id: item.law_id,
        law_name_ar: item.law_articles.laws.name_ar,
        law_name_en: item.law_articles.laws.name_en,
        law_number: item.law_articles.laws.law_number,
        law_url: item.law_articles.laws.url,
        publication_date: item.law_articles.laws.publication_date,
        article_number: item.law_articles.article_number,
        article_title_ar: item.law_articles.article_title_ar,
        article_text_ar: item.law_articles.article_text_ar,
        similarity: 0.7,
      })) || [];

      return await generateResponse(
        question,
        formattedResults,
        language,
        openaiApiKey,
        supabase,
        startTime,
        corsHeaders
      );
    }

    // Step 3: Generate AI response with context
    return await generateResponse(
      question,
      similarArticles || [],
      language,
      openaiApiKey,
      supabase,
      startTime,
      corsHeaders
    );
  } catch (error) {
    console.error("Error in query-law function:", error);

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

async function generateResponse(
  question: string,
  articles: LawArticleResult[],
  language: string,
  openaiApiKey: string,
  supabase: any,
  startTime: number,
  corsHeaders: Record<string, string>
): Promise<Response> {
  if (!articles || articles.length === 0) {
    const noResultsMessage =
      language === "ar"
        ? "عذراً، لم أتمكن من العثور على معلومات قانونية ذات صلة بسؤالك. يرجى إعادة صياغة السؤال أو تقديم المزيد من التفاصيل."
        : "Sorry, I couldn't find relevant legal information for your question. Please rephrase or provide more details.";

    return new Response(
      JSON.stringify({
        answer: noResultsMessage,
        citations: [],
        response_time_ms: Date.now() - startTime,
      }),
      {
        headers: {
          ...corsHeaders,
          "Content-Type": "application/json",
        },
      }
    );
  }

  // Build context from articles
  const context = articles
    .map(
      (article, idx) =>
        `[${idx + 1}] اسم النظام: ${article.law_name_ar}
رقم النظام: ${article.law_number}
رقم المادة: ${article.article_number}
${article.article_title_ar ? `عنوان المادة: ${article.article_title_ar}` : ""}
نص المادة: ${article.article_text_ar}
تاريخ النشر: ${article.publication_date || "غير متوفر"}
رابط النظام: ${article.law_url}
---`
    )
    .join("\n\n");

  // Build prompt for Arabic-optimized model
  const systemPrompt = `أنت مساعد قانوني متخصص في الأنظمة السعودية. مهمتك الإجابة على أسئلة المستخدمين بدقة واحترافية بناءً على المواد القانونية المتوفرة.

تعليمات مهمة:
1. يجب أن تكون الإجابة باللغة العربية في المقام الأول
2. في كل إجابة، يجب ذكر:
   - اسم النظام
   - رقم المادة
   - تاريخ النشر
   - رابط النظام
3. إذا كان هناك أكثر من مادة ذات صلة، اذكرها جميعاً
4. كن دقيقاً ومباشراً في إجابتك
5. لا تختلق معلومات غير موجودة في السياق المقدم
6. إذا لم تكن المعلومات كافية، اذكر ذلك بوضوح

السياق القانوني:
${context}`;

  const userPrompt = `السؤال: ${question}

يرجى تقديم إجابة شاملة ودقيقة مع ذكر جميع المراجع القانونية المطلوبة (اسم النظام، رقم المادة، تاريخ النشر، رابط النظام).`;

  try {
    // Use OpenAI GPT-4 for Arabic-optimized response
    const chatResponse = await fetch(
      "https://api.openai.com/v1/chat/completions",
      {
        method: "POST",
        headers: {
          "Authorization": `Bearer ${openaiApiKey}`,
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          model: "gpt-4-turbo-preview",
          messages: [
            { role: "system", content: systemPrompt },
            { role: "user", content: userPrompt },
          ],
          temperature: 0.3,
          max_tokens: 2000,
        }),
      }
    );

    if (!chatResponse.ok) {
      throw new Error(`OpenAI Chat API error: ${chatResponse.statusText}`);
    }

    const chatData = await chatResponse.json();
    const answer = chatData.choices[0].message.content;

    // Prepare citations
    const citations = articles.map((article) => ({
      law_name_ar: article.law_name_ar,
      law_name_en: article.law_name_en,
      law_number: article.law_number,
      article_number: article.article_number,
      article_title_ar: article.article_title_ar,
      publication_date: article.publication_date,
      law_url: article.law_url,
      similarity: article.similarity,
    }));

    const responseTimeMs = Date.now() - startTime;

    // Log the query
    await supabase.from("query_logs").insert({
      query_text: question,
      query_language: language,
      response_text: answer,
      cited_articles: citations.map((c) => c.article_number),
      response_time_ms: responseTimeMs,
    });

    return new Response(
      JSON.stringify({
        answer,
        citations,
        response_time_ms: responseTimeMs,
      }),
      {
        headers: {
          ...corsHeaders,
          "Content-Type": "application/json",
        },
      }
    );
  } catch (error) {
    console.error("Error generating AI response:", error);
    throw error;
  }
}
