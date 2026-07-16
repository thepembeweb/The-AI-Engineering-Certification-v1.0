# Agent-to-Agent Communication with A2A

Session 8 gave agents a standard way to reach **tools**: MCP. This folder covers the complementary standard for reaching **other agents**: A2A (Agent2Agent), the protocol started by Google and now governed by the Linux Foundation.

```text
MCP : agent -> tool    "here is a function you may call, with this schema"
A2A : agent -> agent   "here is a colleague you may consult, in plain language"
```

The difference is who does the thinking. A tool executes; an agent *reasons* — it may call its own tools, models, and sub-agents, none of which the caller can see. A2A standardizes only the conversation between them: how an agent advertises what it can do, and how another agent sends it work. Both sides stay opaque — different teams, frameworks, even companies.

Rather than install an SDK, this folder implements a minimal, spec-faithful subset of A2A from scratch, so nothing about agent interop is magic. The official [`a2a-sdk`](https://github.com/a2aproject/a2a-python) is what you would use in production.

## The Protocol in Five Ideas

1. **The agent card.** An agent describes itself in a JSON document served at a well-known URL: `GET {agent_url}/.well-known/agent-card.json`. The card lists name, description, skills, and capabilities — the agent's résumé. A client decides *whether and what* to delegate by reading it, not by reading the agent's code.
2. **JSON-RPC transport.** Requests are JSON-RPC 2.0 over HTTP POST. The method implemented here is `message/send`.
3. **Messages and parts.** A message has a `role` (`user` or `agent`) and a list of typed `parts` (`text`, `file`, `data`), so agents can exchange more than strings. We use text parts.
4. **Tasks and artifacts.** For long-running work, a server may respond with a **Task** the client polls (`submitted -> working -> completed`), collecting **artifacts**. Our specialist answers synchronously, so it returns a plain message — the spec allows either.
5. **Opacity.** The client never sees the remote agent's model, tools, prompts, or memory. The card and the messages are the entire interface. That is what lets two organizations interoperate without sharing internals — and why your own guardrails (Notebook 1) still matter on your side of the wire.

## The Files

```text
server.py     the Cat Health Specialist agent behind a minimal A2A server (port 9999)
client.py     discovery + message/send; shares no code with the server on purpose
front_desk.py a delegating agent that consults the specialist it discovered via its card
smoke_test.py protocol checks with a stub agent; needs no API key
```

## How to Start

From the session folder, install the environment (skip if already done):

```bash
cd 12_Production_Agent_Patterns
uv sync
export OPENAI_API_KEY="your-key"
```

Then, **terminal 1** — start the specialist's A2A server from this folder:

```bash
cd a2a
uv run python server.py
```

You should see:

```text
Cat Health Specialist serving A2A at http://127.0.0.1:9999
Agent card: http://127.0.0.1:9999/.well-known/agent-card.json
```

Stop it with `Ctrl+C`. If the port is stuck from an earlier run, kill the old process or change `PORT` in `server.py`.

## How to Test

### 1. Protocol smoke test (no API key needed)

Exercises the server plumbing with a stub agent — card discovery, a `message/send` round-trip, and all three JSON-RPC error codes:

```bash
uv run python smoke_test.py
```

### 2. Discover the agent card

With the server running:

```bash
curl -s http://127.0.0.1:9999/.well-known/agent-card.json | python3 -m json.tool
```

Note what the card does **not** contain: no model name, no tool list, no framework. Those are private.

### 3. Send a message over raw JSON-RPC

```bash
curl -s http://127.0.0.1:9999/ \
  -H "Content-Type: application/json" \
  -d '{
    "jsonrpc": "2.0",
    "id": "1",
    "method": "message/send",
    "params": {
      "message": {
        "kind": "message",
        "role": "user",
        "parts": [{"kind": "text", "text": "Do indoor cats need flea prevention?"}],
        "messageId": "m1"
      }
    }
  }' | python3 -m json.tool
```

Try breaking it: change `"method"` to `"tasks/get"` and you get a structured `-32601` error object, never a stack trace — remote callers always get protocol-shaped errors.

### 4. Use the client

```bash
uv run python client.py "Do indoor cats need flea prevention?"
```

The client fetches the card, prints what it discovered, and sends the question. Everything it knows about the specialist crossed the wire as JSON — the specialist could be rewritten in another framework, moved to another machine, or run by another company, and `client.py` would not change.

### 5. Watch one agent delegate to another

```bash
uv run python front_desk.py
```

The default demo asks two questions: clinic hours (answered locally — no `[A2A]` lines in the trace) and a kitten health question (delegated — the trace shows the front desk phrasing a question, sending it across the protocol, and relaying an answer produced by tools and prompts it cannot see). Or ask your own:

```bash
uv run python front_desk.py "My kitten keeps sneezing. Should I be worried?"
```

## Where This Connects

Guardrails (Notebook 1) apply at this boundary in both directions — check what you send to a remote agent and what comes back. Caching (Notebook 2) applies too, with the same caveat: a semantic cache in front of `send_message` inherits all the risks of caching health answers, plus a new one — the remote agent can change behind an unchanged card version.

## Further Reading

- [A2A protocol specification](https://a2a-protocol.org/) — including tasks, artifacts, streaming, and push notifications, the parts deliberately skipped here
- [a2a-sdk (Python)](https://github.com/a2aproject/a2a-python) — the official implementation to use in production
- [A2A and MCP: complementary protocols](https://a2a-protocol.org/latest/topics/a2a-and-mcp/)
- [JSON-RPC 2.0 specification](https://www.jsonrpc.org/specification)

> This is an educational cat health assistant, not a veterinary care tool. That caveat travels *across the protocol boundary*: a remote agent's disclaimers are part of its contract.
