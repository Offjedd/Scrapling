import "jsr:@supabase/functions-js/edge-runtime.d.ts";

const corsHeaders = {
  "Access-Control-Allow-Origin": "*",
  "Access-Control-Allow-Methods": "GET, POST, PUT, DELETE, OPTIONS",
  "Access-Control-Allow-Headers": "Content-Type, Authorization, X-Client-Info, Apikey",
};

Deno.serve(async (req: Request) => {
  if (req.method === "OPTIONS") {
    return new Response(null, {
      status: 200,
      headers: corsHeaders,
    });
  }

  try {
    // This edge function triggers the Python scraper to check for updates
    // The actual scraping logic is in the Python script

    const pythonScraperUrl = Deno.env.get("PYTHON_SCRAPER_URL");

    if (!pythonScraperUrl) {
      return new Response(
        JSON.stringify({
          message: "Update check scheduled",
          note: "Run the Python scraper manually with 'python saudi_law_scraper.py update'",
        }),
        {
          headers: {
            ...corsHeaders,
            "Content-Type": "application/json",
          },
        }
      );
    }

    // If a Python scraper URL is configured, trigger it
    const response = await fetch(pythonScraperUrl, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({ action: "update" }),
    });

    const result = await response.json();

    return new Response(
      JSON.stringify({
        message: "Update check completed",
        result,
      }),
      {
        headers: {
          ...corsHeaders,
          "Content-Type": "application/json",
        },
      }
    );
  } catch (error) {
    console.error("Error in update-laws function:", error);

    return new Response(
      JSON.stringify({
        error: error.message || "Internal server error",
        message: "To run updates manually, use: python saudi_law_scraper.py update",
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
