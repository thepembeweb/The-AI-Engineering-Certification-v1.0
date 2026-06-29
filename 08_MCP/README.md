<p align="center" draggable="false"><img src="https://github.com/AI-Maker-Space/LLM-Dev-101/assets/37101144/d1343317-fa2f-41e1-8af1-1dbb18399719"
     width="200px"
     height="auto"/>
</p>

<h1 align="center" id="heading">Session 8: Model Context Protocol (MCP)</h1>

### [Quicklinks]()

| Session Sheet                                                                                                              | Recording                                                                                                                                                   | Slides                                                 | Repo          | Homework                                                    | Feedback                                             |
| :------------------------------------------------------------------------------------------------------------------------- | :---------------------------------------------------------------------------------------------------------------------------------------------------------- | :----------------------------------------------------- | :------------ | :---------------------------------------------------------- | :--------------------------------------------------- |
| [Session 8: MCP](https://github.com/AI-Maker-Space/The-AI-Engineering-Certification-v1.0/tree/main/00_Docs/Modules/08_MCP) | [Recording!](https://us02web.zoom.us/rec/share/rqw5I5hwbOOHy8TrGjnu0IjDJi53ykHb0k897jYfyHqZpgRhUuFP4A18d4NrcEKS.18sNk6Do9XwyaVUy) <br> passcode: `E56&^V+8` | [Session 8 Slides](https://canva.link/k8cixqgkfeghdsn) | You are here! | [Session 8 Assignment](https://forms.gle/TcjjChq38ydMjuqn8) | [Feedback 6/25](https://forms.gle/DvcWDgBXatBWCXqi7) |

## Useful Resources

**MCP (Model Context Protocol)**

- [MCP Official Docs](https://modelcontextprotocol.io/) — Spec, tutorials, and guides
- [MCP-UI](https://mcpui.dev/) — Official standard for interactive UI in MCP
- [MCP Auth Guide (Auth0)](https://auth0.com/blog/mcp-specs-update-all-about-auth/) — Deep dive into MCP auth spec updates

## Main Assignment

In this session, you will build an MCP server with OAuth authentication — a cat
shop application that exposes tools for browsing products, managing a cart, and
checking out.

The main entry point is:

```text
server.py
```

The server implementation lives in:

```text
app/
```

Available MCP tools:

- `list_products`
- `search_products`
- `get_product`
- `add_to_cart`
- `view_cart`
- `remove_from_cart`
- `checkout`

## Setup

From this folder:

```bash
uv sync
```

Copy the example env file and fill in your OpenAI API key:

```bash
cp .env.example .env
```

## Running the MCP Server

Run the server locally:

```bash
uv run server.py
```

The server starts on `http://localhost:8000`.

If port `8000` is already in use on your machine, start it on a different port:

```bash
PORT=8001 uv run server.py
```

### Expose the server with ngrok

In a separate terminal, start an ngrok tunnel:

```bash
ngrok http 8000
```

Copy the ngrok forwarding URL (e.g. `https://xxxx-xx-xx-xx-xx.ngrok-free.app`) and
restart the server with it:

```bash
ISSUER_URL=https://xxxx-xx-xx-xx-xx.ngrok-free.app uv run server.py
```

> **Note:** The `ISSUER_URL` must match the public URL clients use to reach the
> server, otherwise OAuth authentication will fail.

## Outline

### Breakout Room #1

- Set up the MCP server with OAuth and the product database
- Explore the MCP tools: `list_products`, `search_products`, `get_product`, `add_to_cart`, `view_cart`, `remove_from_cart`, `checkout`

### Breakout Room #2

- Connect an MCP client to the server
- Build an end-to-end interaction flow using the MCP tools

## Ship

The completed MCP server and client integration!

### Deliverables

- A short Loom of either:
  - the MCP server you built and a demo of the client interacting with it; or
  - the notebook you created for the Advanced Build

## Share

Make a social media post about your final application!

### Deliverables

- Make a post on any social media platform about what you built!

Here's a template to get you started:

```
🚀 Exciting News! 🚀

I am thrilled to announce that I have just built and shipped an MCP server with OAuth authentication! 🎉🤖

🔍 Three Key Takeaways:
1️⃣
2️⃣
3️⃣

Let's continue pushing the boundaries of what's possible in the world of AI and tool integration. Here's to many more innovations! 🚀
Shout out to @AIMakerspace !

#MCP #ModelContextProtocol #OAuth #Innovation #AI #TechMilestone

Feel free to reach out if you're curious or would like to collaborate on similar projects! 🤝🔥
```

## Submitting Your Homework

Follow these steps to prepare and submit your homework assignment:

1. Review the MCP server code in `server.py` and the `app/` directory
2. Run the MCP server locally using `uv run server.py`
3. Connect to the server using an MCP client (e.g., Claude Desktop, or a custom client)
4. Test all available tools: browsing products, adding to cart, viewing cart, removing items, and checkout
5. Record a Loom video reviewing what you have learned from this session

## Questions

### Question #1

Why is OAuth important for MCP servers, and what security considerations should you keep in mind when exposing tools to AI clients?

#### Answer

OAuth is important for MCP servers because it gives a standard, secure way to verify who is calling your tools and what they are allowed to do. Instead of sharing static API keys broadly, OAuth issues scoped, time-limited tokens, which reduces blast radius if a token is leaked and supports better auditing and revocation.

Key security considerations:

1. Use least-privilege scopes so clients only get the minimum permissions they need.
2. Validate tokens server-side (issuer, audience, expiry, and signature) on every request.
3. Use HTTPS everywhere, especially when exposing the server publicly.
4. Protect and rotate secrets (client credentials, signing keys) and avoid logging sensitive token data.
5. Add guardrails around high-risk tools (confirmation steps, rate limits, input validation, and clear authorization checks) to prevent misuse by compromised or over-permissioned clients.

### Question #2

What is Streamable HTTP transport in MCP, and why might you expose a server publicly with OAuth instead of using a local stdio connection?

#### Answer

Streamable HTTP transport in MCP is an HTTP-based communication mode where MCP messages are exchanged over web endpoints, enabling remote and networked clients to connect to the server (not just local processes). Compared with local `stdio`, it is better suited for web-style integrations, multi-client access, hosted deployments, and interoperability across machines.

You might expose the server publicly with OAuth when clients need to connect from outside your local machine (for example, cloud-hosted apps, external tools, teammates, or demos over ngrok). OAuth adds identity, scoped permissions, and token lifecycle controls, so remote access can be authenticated and authorized safely. In contrast, `stdio` is great for local development and single-machine trust boundaries, but it is not designed for secure internet-facing access.

## Activity 1: Extend the MCP Server

Add at least one new tool to the cat shop MCP server (e.g., `search_products`, `update_cart_quantity`, or `get_order_history`). Ensure the new tool integrates properly with the existing database and OAuth authentication. Demo the new tool through an MCP client and include it in your Loom video.

### Activity 1 Answer

I added a new MCP tool: `search_products(query: str, category: str | None = None)`.

What it does:

1. Searches the `products` catalog by keyword using partial matching on product name and description.
2. Optionally filters results by category.
3. Returns the same product response shape as `list_products` (`id`, `name`, `description`, `price`, `category`) so client usage stays consistent.

Integration details:

1. Implemented in `app/tools.py` using the existing `@mcp.tool()` pattern.
2. Reused the existing SQLite database and `oauth_provider._get_db()` access path.
3. Used parameterized SQL queries (`LIKE` with bound params) to avoid injection issues.

Demo flow used in MCP client:

1. Call `list_products` to browse the catalog.
2. Call `search_products` with a keyword (and optional category) to narrow choices.
3. Call `add_to_cart` for a selected item, then `view_cart`, then `checkout`.

Result:
The new tool integrates cleanly with the existing OAuth-enabled MCP server and improves product discovery without requiring any schema changes.

## Advanced Activity: Build a Custom MCP Client

Build a custom MCP client that connects to the cat shop server over Streamable HTTP, authenticates via OAuth, and orchestrates a multi-step shopping flow (browse → add to cart → checkout). Compare the developer experience of MCP-based tool integration vs. traditional REST API calls.

Include your findings and a demo in your Loom video.

### Advanced Activity Answer

I built a custom Streamable HTTP MCP client in `advanced_client.py` that uses OAuth and executes an explicit shopping workflow end-to-end.

What I implemented:

1. A direct MCP session client using `streamable_http_client` + `ClientSession` (no LangChain agent abstraction).
2. OAuth sign-in with a local callback server and in-memory token storage.
3. Deterministic tool orchestration: `list_products` -> `search_products` -> `get_product` -> `add_to_cart` -> `view_cart` -> `checkout` -> `view_cart`.
4. Clear terminal logging of each tool result so the flow can be demonstrated in a Loom video.

How to run:

1. Start the MCP server (use `PORT`/`ISSUER_URL` as needed for your environment).
2. Run:

```bash
uv run python advanced_client.py --server-url http://localhost:8000
```

Developer experience comparison (MCP vs REST):

1. MCP advantages: tool discovery and schema-driven invocation are built-in, so adding new capabilities requires less client-side endpoint wiring.
2. REST advantages: very familiar request model and broad ecosystem support for endpoint-based debugging.
3. Tradeoff observed: MCP adds lightweight protocol ceremony (session/messages), but simplifies multi-tool orchestration once connected.
4. OAuth complexity is comparable in both approaches; both still require proper token lifecycle and issuer alignment.

Loom demo checklist:

1. Show OAuth sign-in from the custom client.
2. Show the full browse -> search -> add -> checkout flow.
3. Show cart state before and after checkout.
4. Summarize MCP vs REST tradeoffs based on implementation experience.
