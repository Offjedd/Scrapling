import "jsr:@supabase/functions-js/edge-runtime.d.ts";
import { createClient } from "npm:@supabase/supabase-js@2";

const corsHeaders = {
  "Access-Control-Allow-Origin": "*",
  "Access-Control-Allow-Methods": "GET, POST, OPTIONS",
  "Access-Control-Allow-Headers": "Content-Type, Authorization, X-Client-Info, Apikey",
};

Deno.serve(async (req: Request) => {
  if (req.method === "OPTIONS") {
    return new Response(null, { status: 200, headers: corsHeaders });
  }

  try {
    const supabaseUrl = Deno.env.get("SUPABASE_URL")!;
    const supabaseServiceKey = Deno.env.get("SUPABASE_SERVICE_ROLE_KEY")!;
    const openaiApiKey = Deno.env.get("OPENAI_API_KEY")!;

    const supabase = createClient(supabaseUrl, supabaseServiceKey);

    console.log("Starting embedding generation...");

    // Get all laws
    const lawsResp = await supabase.from("laws").select("id, name_ar, full_text_ar");
    if (lawsResp.error) throw lawsResp.error;
    const allLaws = lawsResp.data || [];

    // Get existing embeddings
    const embsResp = await supabase.from("law_embeddings").select("law_id");
    if (embsResp.error) throw embsResp.error;
    const withEmbs = new Set((embsResp.data || []).map(e => e.law_id));

    // Filter laws needing embeddings
    const needEmbs = allLaws.filter(law => !withEmbs.has(law.id));

    console.log(`Total: ${allLaws.length}, With embs: ${withEmbs.size}, Need: ${needEmbs.length}`);

    let added = 0;

    for (const law of needEmbs) {
      console.log(`Processing: ${law.name_ar}`);

      const text = `${law.name_ar}\n\n${law.full_text_ar || ""}`;

      // Generate embedding
      const embResp = await fetch("https://api.openai.com/v1/embeddings", {
        method: "POST",
        headers: {
          "Authorization": `Bearer ${openaiApiKey}`,
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          model: "text-embedding-3-small",
          input: text.substring(0, 8000),
        }),
      });

      if (!embResp.ok) {
        console.error(`OpenAI error: ${embResp.statusText}`);
        continue;
      }

      const embData = await embResp.json();
      const embedding = embData.data[0].embedding;

      // Insert
      const insertResp = await supabase.from("law_embeddings").insert({
        law_id: law.id,
        text_chunk: law.name_ar,
        embedding: embedding,
        chunk_index: 0,
      });

      if (insertResp.error) {
        console.error(`Insert error:`, insertResp.error);
      } else {
        console.log(`  Added!`);
        added++;
      }

      await new Promise(resolve => setTimeout(resolve, 600));
    }

    return new Response(JSON.stringify({
      success: true,
      message: `Generated ${added} embeddings`,
      total: allLaws.length,
      added: added,
    }), {
      headers: { ...corsHeaders, "Content-Type": "application/json" },
    });
  } catch (error) {
    console.error("Error:", error);
    return new Response(JSON.stringify({
      success: false,
      error: error.message,
    }), {
      status: 500,
      headers: { ...corsHeaders, "Content-Type": "application/json" },
    });
  }
});
