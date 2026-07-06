# Frontend

This Next.js app is the Vercel-hosted UI for the LangSmith-hosted LangGraph agent in the parent repository.

## Runtime model

- The browser talks to the local Next.js proxy route at `/api`.
- The proxy route in `app/api/[...path]/route.ts` forwards requests to `LANGGRAPH_API_URL`.
- `LANGSMITH_API_KEY` is used server-side only and must not be exposed to the browser.
- `NEXT_PUBLIC_API_URL` should point to `/api` locally or to your deployed Vercel frontend URL with `/api` appended.
- `LANGGRAPH_API_URL` should point to the backend URL you are testing against. Use `http://localhost:2024` for `langgraph dev`, or your public backend URL in production.

## Environment variables

Create a local `.env.local` from `.env.local.example`.

```text
LANGGRAPH_API_URL=http://localhost:2024
LANGSMITH_API_KEY=
NEXT_PUBLIC_API_URL=http://localhost:3000/api
```

For production on Vercel:

```text
LANGGRAPH_API_URL=https://your-backend.example.com
LANGSMITH_API_KEY=lsv2_pt_...
NEXT_PUBLIC_API_URL=https://your-app.vercel.app/api
```

## Development

```bash
npm install
npm run dev
```

Open `http://localhost:3000` and send a message through the chat UI.

## Deployment

Deploy this folder to Vercel as a standard Next.js app. Set the environment variables above in the Vercel project settings, then redeploy.
