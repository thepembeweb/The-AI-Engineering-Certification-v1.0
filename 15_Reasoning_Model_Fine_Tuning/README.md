<p align = "center" draggable="false" ><img src="https://github.com/AI-Maker-Space/LLM-Dev-101/assets/37101144/d1343317-fa2f-41e1-8af1-1dbb18399719"
     width="200px"
     height="auto"/>
</p>

<h1 align="center" id="heading">Session 15: Reasoning Model Fine-Tuning with GRPO</h1>

### [Quicklinks](https://github.com/AI-Maker-Space/The-AI-Engineering-Certification-v1.0/tree/main/00_Docs/Modules)

| 📰 Session Sheet | ⏺️ Recording | 🖼️ Slides | 👨‍💻 Repo | 📝 Homework | 📁 Feedback |
|:-----------------|:-------------|:----------|:----------|:------------|:------------|
| [Session 15: 📉 Fine-Tuning](https://github.com/AI-Maker-Space/The-AI-Engineering-Certification-v1.0/tree/main/00_Docs/Modules/15_Fine-Tuning) |[Recording!](https://us02web.zoom.us/rec/share/OR_pUjCUR5Io0_aaozk6Kb7tEVrrKRfuEqDFNa0Nk77BcmuquOEkWnmgy9-WODZ3.xNci5XI4OuhLqAcT) <br> passcode: `ImT6*C?D`| [Session 15 Slides](https://canva.link/0a2b2huva9cgkt2) | You are here! | [Session 15 Assignment](https://forms.gle/UPv7tonVdjQDfzGG9) | [Feedback 7/21](https://forms.gle/RbA9anGSgHCkNowNA) |

## Main Assignment

In this assignment, you will fine-tune `meta-llama/Llama-3.2-3B-Instruct` into a small reasoning model using Unsloth and GRPO (Group Relative Policy Optimization) — the reinforcement learning algorithm popularized by DeepSeek-R1.

Instead of showing the model examples of good reasoning (supervised fine-tuning), you will reward it for producing verifiably correct, well-structured answers to GSM8K math problems and let it discover the reasoning itself:

```text
prompt -> sample a group of 8 completions -> score each with reward functions
       -> compute group-relative advantage -> policy update (with KL penalty) -> repeat
```

The main notebook is:

```text
01_Reasoning_Fine_Tuning_Unsloth_GRPO.ipynb
```

Complete all questions directly in the notebook.

## Outline

### Breakout Room #1: Model Loading and LoRA

- Task 1: Environment Setup
- Task 2: Load the Base Model
- Task 3: Attach LoRA Adapters
- Question #1, Question #2, and Question #3

### Breakout Room #2: GRPO Training on GSM8K

- Task 4: Prepare the GSM8K Dataset
- Task 5: Define Reward Functions
- Task 6: Configure GRPO
- Question #4
- Task 7: Train with GRPOTrainer
- Task 8: Compare Before and After
- Task 9: Save and Load the LoRA

## Setup

### Prerequisites

Unlike other sessions, this one trains a model on your own machine, so it needs real GPU hardware:

- **NVIDIA GPU, Ampere or newer (compute capability >= 8.0)** — e.g. RTX 30/40/50-series, A10, A100. Recent vLLM releases dropped pre-Ampere (T4/Turing) support.
- **16 GB+ VRAM** (24 GB is comfortable). If you hit out-of-memory errors: lower `gpu_memory_utilization` from `0.7` to `0.6`, or drop `num_generations` from `8` to `4` (and `gradient_accumulation_steps` from `8` to `4` to keep the batch geometry valid).
- **Linux or WSL2 only.** The training stack (vLLM, Triton, xformers) does not ship macOS wheels — `uv sync` will refuse to resolve on macOS by design.
- **~10 GB of free disk** for model weights and training checkpoints.
- **A Hugging Face account** with the [Llama 3.2 license accepted](https://huggingface.co/meta-llama/Llama-3.2-3B-Instruct) (then `hf auth login`), or swap in the ungated `unsloth/Llama-3.2-3B-Instruct` mirror inside the notebook.

### Install

From this folder, install the environment with uv:

```bash
uv sync
```

Then open the notebook in Cursor or VS Code and select the Python/Jupyter environment created by uv.

Optional Weights & Biases experiment tracking:

```bash
uv sync --extra wandb
wandb login
```

Then set `report_to = "wandb"` in the notebook's `GRPOConfig`.

## Submitting Your Homework

Follow these steps to prepare and submit your homework:

1. Pull the latest updates from upstream into the main branch of your AIE9 repo:

```bash
git checkout main
git pull upstream main
git push origin main
```

2. Start Cursor from the `15_Reasoning_Model_Fine_Tuning` folder.
3. Complete the notebook questions.
4. Keep useful notebook outputs that help explain your work, especially the training reward logs and the before/after generation comparison. Remove secrets and excessively noisy outputs.
5. Add, commit, and push your modified work to your origin repository.

When submitting your homework, provide the GitHub URL to your AIE9 repo.
