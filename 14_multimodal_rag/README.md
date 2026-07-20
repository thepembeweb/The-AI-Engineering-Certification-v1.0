<p align = "center" draggable="false" ><img src="https://github.com/AI-Maker-Space/LLM-Dev-101/assets/37101144/d1343317-fa2f-41e1-8af1-1dbb18399719" width="200px" height="auto"/></p>

## <h1 align="center" id="heading">Session 14: Multi-Modal RAG with Vision-Language Models</h1>

| 📰 Session Sheet | ⏺️ Recording | 🖼️ Slides | 👨‍💻 Repo | 📝 Homework | 📁 Feedback |
|:----------------|:------------|:----------|:---------|:-----------|:-----------|
| [Session 14: Multimodal RAG](https://github.com/AI-Maker-Space/The-AI-Engineering-Certification-v1.0/tree/main/00_Docs/Modules/14_Multimodal_RAG) |[Recording!](https://us02web.zoom.us/rec/share/NgVURG6fXmnx1yaD_v59EwLOXGkSsqDVbfZ0-1PLajEFKYAWvSx910wXw14TybrY.tIE0_dv0mi-zZZBF) <br> passcode: `f8Vf*kFB`| [Session 14 Slides](https://canva.link/7v6gl0p4htce5ib) | You are here! | [Session 14 Assignment](https://forms.gle/2p6KYF56ejSF1dyQ9) | [Feedback 7/16](https://forms.gle/6GCcwo1nF4oi8epp9) |

**⚠️!!! This session makes real API calls and the first CLIP run downloads a ~600 MB model. Your `OPENAI_API_KEY` lives in `.env` — never commit it !!!⚠️**

# Build 🏗️

This week we extend text RAG to **images + text in one pipeline** using **Vision-Language Models**. You'll use a VLM two different ways — as an *ingestion parser* that turns charts into searchable chunks, and as a *query-time reader* that reads exact numbers straight off the pixels. In between, you'll build and compare **three cross-modal retrieval strategies** on **Qdrant**, then extend the whole pipeline to **video with timestamp citations**. Everything runs against a tiny CC0 synthetic dataset (ACME Robotics FY2024) that ships in `./data` — the key numbers exist *only in the chart pixels*, so you can prove your pipeline really reads images.

The notebook is `multimodal_rag_vlm.ipynb`, split into two breakout rooms of ~25 minutes each. Everything you need to answer the questions is written in the notebook's explanations — read as you run.

- 🤝 Breakout Room #1: Parsing & Cross-Modal Retrieval (Sections 0–5)
  - Get set up: run `uv sync` in this folder, copy `.env.example` to `.env` and add your `OPENAI_API_KEY`, then open the notebook with this folder's environment (`uv run jupyter lab`, or select the `.venv` kernel in Cursor/VS Code)
  - Run Sections 0–3: load the model provider-agnostically and explore the ACME corpus
  - Run Section 4: use the VLM to parse all six charts into searchable chunks
  - Run Section 5: build and compare retrieval Strategies A (caption→text), B (unified CLIP), and C (separate stores + RRF) on Qdrant
  - Answer ❓ Questions #1–2 and complete 🏗️ Activity #1 in the notebook

- 🤝 Breakout Room #2: Generation, Evaluation & Video (Sections 6–10)
  - Run Sections 6–7: wrap the strategies behind one retriever and generate answers grounded in the real pixels
  - Run Section 8: measure recall@3 per strategy and review the gotchas
  - Run Section 9: extend the pipeline to video — transcripts, keyframes, and timestamped answers
  - Answer ❓ Questions #3–4, complete 🏗️ Activity #2, and read the "what we built vs. production" recap in Section 10

# Ship 🚢

A fully-run multi-modal RAG notebook that retrieves chart images from text questions and reads the answers off the pixels.

### Deliverables

- Your completed `multimodal_rag_vlm.ipynb` — every cell executed, all four ❓ questions answered, and both 🏗️ activities done with your observations filled in
- A five-minute-or-less Loom video walking through your pipeline, including one answer the model read from chart pixels and one video answer with a timestamp citation

# Share 🚀

Take a screenshot of your favorite "the model read that number off the chart" moment and share what you built with the community!

```
🚀 Exciting News! 🚀

I just built a multi-modal RAG pipeline that answers questions by reading charts straight off the pixels, powered by Vision-Language Models and Qdrant! 🎉🤖

🔍 Three Key Takeaways:
1️⃣
2️⃣
3️⃣

Let's continue pushing the boundaries of what's possible in multi-modal AI. Here's to many more innovations! 🚀
Shout out to @AIMakerspace !

#AIEngineering #MultimodalRAG #VLM #Qdrant #RAG

Feel free to reach out if you're curious or would like to collaborate on similar projects! 🤝🔥
```

# Submitting Your Homework

## Main Homework Assignment

Follow these steps to prepare and submit your homework:

1. Complete both breakout rooms in `multimodal_rag_vlm.ipynb`, running every cell top to bottom
2. Respond to the four questions in the notebook (There are two at the end of each Breakout Room section)
3. Complete the activities in the notebook (There is one at the end of each Breakout Room section)
4. Record a Loom video walking through your completed notebook

##
# Continued Learning 🌱

Focus on your certification requirements during the cohort. These builds are here for when the cohort wraps and you want to come back to reinforce and extend what you learned.

## Advanced Activity: Push the pipeline toward production

Pick one (or more) of the extensions from Section 10 of the notebook and build it out:

- Swap `VLM_MODEL`/`EMBED_MODEL` to another provider and compare the recall@3 table
- Add hybrid retrieval (BM25 + dense) on the text side and fuse three lists with RRF
- Enrich the parse prompt to extract Markdown tables from figures and re-test Strategy A on numeric questions
- Add a cross-encoder reranker after fusion and check top-1 accuracy
- Replace interval keyframe sampling with scene-change detection and perceptual-hash dedupe
- Ask something the data can't answer and confirm the model declines instead of hallucinating
