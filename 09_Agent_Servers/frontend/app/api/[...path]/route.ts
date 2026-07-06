import { initApiPassthrough } from "langgraph-nextjs-api-passthrough";

const rawApiUrl = process.env.LANGGRAPH_API_URL?.trim();
const apiUrl =
  rawApiUrl && isValidAbsoluteHttpUrl(rawApiUrl) ? rawApiUrl : null;
export const runtime = "edge";

function isValidAbsoluteHttpUrl(value: string) {
  try {
    const url = new URL(value);
    return url.protocol === "http:" || url.protocol === "https:";
  } catch {
    return false;
  }
}

function missingApiUrlResponse() {
  return new Response(
    JSON.stringify({
      error:
        "LANGGRAPH_API_URL is missing or invalid. Set it to the full backend deployment URL in your frontend environment variables.",
    }),
    {
      status: 500,
      headers: { "content-type": "application/json" },
    },
  );
}

const handlers = apiUrl
  ? initApiPassthrough({
      apiUrl,
      apiKey: process.env.LANGSMITH_API_KEY,
      disableWarningLog: true,
      runtime,
    })
  : null;

const missingHandler = async () => missingApiUrlResponse();

export const GET = handlers?.GET ?? missingHandler;
export const POST = handlers?.POST ?? missingHandler;
export const PUT = handlers?.PUT ?? missingHandler;
export const PATCH = handlers?.PATCH ?? missingHandler;
export const DELETE = handlers?.DELETE ?? missingHandler;
export const OPTIONS = handlers?.OPTIONS ?? missingHandler;
