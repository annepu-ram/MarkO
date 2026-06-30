# Fine-Tuning Qwen2.5-Coder-3B for SwiftSites YAML Generation

## Table of Contents

1. [Understanding Fine-Tuning — Concepts](#understanding-fine-tuning--concepts)
2. [Why Fine-Tune? (vs. Prompting vs. RAG)](#why-fine-tune-vs-prompting-vs-rag)
3. [QLoRA — How We Train on 6GB](#qlora--how-we-train-on-6gb)
4. [The Data Pipeline — Overview](#the-data-pipeline--overview)
5. [Script 01: Extract Pairs from Templates](#script-01-extract-pairs-from-templates)
6. [Script 02: Component Knowledge Pairs](#script-02-component-knowledge-pairs)
7. [Script 03: Augment Data](#script-03-augment-data)
8. [Script 04: Validate Dataset](#script-04-validate-dataset)
9. [Script 05: Prepare Training JSONL](#script-05-prepare-training-jsonl)
10. [Script 06: Analyze Dataset](#script-06-analyze-dataset)
11. [Training (Script 07)](#training-script-07)
12. [Export & Deploy (Scripts 08-10)](#export--deploy-scripts-08-10)
13. [Prerequisites — Software Installation](#prerequisites--software-installation)
14. [Hyperparameters Explained](#hyperparameters-explained)
15. [Troubleshooting](#troubleshooting)

---

## Understanding Fine-Tuning — Concepts

### What Is Fine-Tuning?

A Large Language Model (LLM) like Qwen2.5-Coder-3B has been **pre-trained** on trillions of tokens of code and text. It already "knows" Python, YAML, HTML, and general programming patterns. But it doesn't know *your specific* YAML format (SwiftSites components, property groups, nesting rules).

**Fine-tuning** is the process of continuing the model's training on a small, focused dataset so it learns your domain-specific patterns without forgetting its general knowledge.

```
Pre-trained Model          Fine-tuned Model
(knows YAML syntax)  →→→  (knows SwiftSites YAML specifically)
(knows programming)  →→→  (knows layout-row/column patterns)
(general knowledge)  →→→  (knows our 37 component types)
```

### The Analogy

Think of it like hiring a developer:
- **Pre-trained model** = A developer who knows YAML and web development generally
- **Fine-tuning** = Onboarding them on your specific codebase and conventions
- **Training data** = The onboarding materials (examples of correct work)

### Key Terms

| Term | Meaning |
|------|---------|
| **Base model** | The pre-trained model we start from (Qwen2.5-Coder-3B-Instruct) |
| **Training pair** | One (prompt, completion) example the model learns from |
| **Epoch** | One full pass through all training data |
| **Loss** | How "wrong" the model's predictions are (lower = better) |
| **Overfitting** | Model memorizes training data instead of learning patterns |
| **Tokens** | Sub-word pieces the model reads/writes (~3.5 chars per token for code) |
| **Inference** | Using the trained model to generate new output |

### How Training Actually Works (Simplified)

1. Model reads a prompt + completion pair
2. It tries to predict the next token at each position in the completion
3. The difference between its prediction and the actual token = **loss**
4. Loss is used to calculate **gradients** (direction to adjust weights)
5. Weights are nudged slightly in the right direction
6. Repeat thousands of times across all training pairs

Each pass through the entire dataset = 1 **epoch**. We train for 3 epochs (the model sees every example 3 times).

### What Makes Training Data Good?

1. **Correctness** — Every completion must be valid, renderable YAML
2. **Diversity** — Cover all section types, components, styles, industries
3. **Consistency** — Same format/structure across all examples
4. **Volume** — Enough examples that the model learns patterns, not memorizes (2000-5000 is good for domain-specific fine-tuning)
5. **No contradictions** — Don't teach two different ways to do the same thing

---

## Why Fine-Tune? (vs. Prompting vs. RAG)

### Three Approaches to Teaching an LLM

| Approach | How | Best For | Limitations |
|----------|-----|----------|-------------|
| **Prompting** | Put instructions in system prompt | Simple tasks, general models | Token limit, model may ignore rules |
| **RAG** | Retrieve relevant examples at runtime | Dynamic content, large knowledge bases | Depends on retrieval quality, adds latency |
| **Fine-tuning** | Train model weights on your data | Consistent format, domain expertise | Fixed knowledge, needs compute |

### Why We Use Fine-Tuning for SwiftSites

Our builder agent makes 7-12 LLM calls per website generation. Each call must produce valid YAML with:
- Correct component names (37 types)
- Correct property groups (`layout`, `spacing`, `appearance`, `typography`)
- Correct nesting (components inside layout-column, not layout-row)
- Correct token values (string tokens like `"50"` for widthMode)

With prompting alone, general models produce ~60% valid YAML. With RAG + prompting, ~80%. With fine-tuning, we target **95%+** valid on first attempt.

### The Combined Approach

We don't abandon RAG — we combine:
```
Fine-tuned model (knows format deeply)
  + RAG (retrieves relevant style examples at runtime)
  + System prompt (specific instructions per call)
  = Highly reliable YAML generation
```

The fine-tuned model doesn't need to be told "use layout-row for sections" every time — it *knows*. The system prompt and RAG then focus on the creative aspects (style, content, specific requirements).

---

## QLoRA — How We Train on 6GB

### The Memory Problem

A 3B parameter model at full precision (float32) = 12 GB. Even at half precision (float16) = 6 GB. That's our entire GPU budget just to *load* the model — no room for training.

### The Solution: QLoRA (Quantized Low-Rank Adaptation)

QLoRA combines three techniques:

#### 1. Quantization (4-bit NF4)

Instead of storing each weight as a 16-bit float, we compress to 4 bits using the NormalFloat4 format. This reduces model size from 6 GB → 1.5 GB.

```
Float16:  Each weight = 16 bits  → 3B params × 2 bytes = 6 GB
NF4:      Each weight = 4 bits   → 3B params × 0.5 bytes = 1.5 GB
```

NF4 is designed for neural network weights (which follow a normal distribution), so quality loss is minimal.

#### 2. LoRA (Low-Rank Adaptation)

Instead of updating all 3 billion parameters, we freeze the base model and attach small "adapter" matrices to key layers.

```
Original layer: Y = W × X          (W is 4096×4096 = 16M params, frozen)
LoRA layer:     Y = W × X + B × A × X  (A is 4096×16, B is 16×4096 = 131K params, trainable)
```

With rank `r=16`, each adapted layer adds only 131K trainable parameters. Total trainable: ~15M out of 3B = **0.5% of the model**.

This means:
- Gradients only flow through tiny adapter matrices
- Optimizer states (momentum, variance) only stored for 15M params, not 3B
- Base model weights are frozen and quantized (save memory)

#### 3. Double Quantization

Even the quantization parameters themselves get quantized (nested quantization), saving another ~0.4 GB.

### VRAM Budget

| Component | Size | Why |
|-----------|------|-----|
| Base model (4-bit NF4) | ~1.5 GB | 3B params at 4 bits each |
| LoRA adapters (float16) | ~0.1 GB | 15M trainable params |
| Optimizer states (8-bit) | ~0.2 GB | Momentum + variance for 15M params |
| Gradients + activations | ~3.5 GB | Forward/backward pass cache |
| **Total** | **~5.3 GB** | Fits in 6 GB with margin |

### Gradient Checkpointing

To further save memory, we don't store all intermediate activations. Instead, we recompute them during the backward pass. This trades compute time for memory (~30% slower, ~1.5 GB saved).

---

## The Data Pipeline — Overview

### Why a Pipeline?

Raw data (example templates) isn't ready for training. We need to:
1. **Extract** — Pull YAML from files, generate prompts
2. **Enrich** — Add component knowledge beyond just templates
3. **Multiply** — Create variations to prevent overfitting
4. **Filter** — Remove broken/too-long/duplicate examples
5. **Format** — Convert to the exact format the trainer expects
6. **Verify** — Confirm coverage and balance

```
example_templates/           COMPONENT_SYNTAX_REFERENCE.md
       ↓                              ↓
┌─────────────┐              ┌─────────────────┐
│ 01_extract  │              │ 02_component    │
│ _pairs.py   │              │ _knowledge.py   │
└──────┬──────┘              └────────┬────────┘
       ↓                              ↓
  extracted_pairs.jsonl    component_knowledge_pairs.jsonl
       ↓                              ↓
       └──────────┬───────────────────┘
                  ↓
         ┌───────────────┐
         │ 03_augment    │  ← Rephrases prompts, injects style/industry context
         │ _data.py      │
         └───────┬───────┘
                 ↓
         augmented_pairs.jsonl (3x more data)
                 ↓
         ┌───────────────┐
         │ 04_validate   │  ← Removes broken YAML, too-long, duplicates
         │ _dataset.py   │
         └───────┬───────┘
                 ↓
         validated_pairs.jsonl (quality-filtered)
                 ↓
         ┌───────────────┐
         │ 05_prepare    │  ← Formats as ChatML, splits train/eval
         │ _jsonl.py     │
         └───────┬───────┘
                 ↓
         train.jsonl + eval.jsonl (ready for training)
                 ↓
         ┌───────────────┐
         │ 06_analyze    │  ← Reports coverage gaps, token stats
         │ _dataset.py   │
         └───────────────┘
```

### Agent-Agnostic Design

A critical design choice: the training data is **not tied to any specific agent prompt format**.

If tomorrow we change the builder agent's prompt from `[Section] hero\n[Theme] ...` to a different format, the model should still generate valid SwiftSites YAML. The model learns the *output format* (SwiftSites YAML), not the *input format* (agent prompts).

This means training prompts are natural and varied:
- "Create a hero section for a SaaS startup"
- "Build a pricing table with glassmorphism style"
- "Section: features | Style: modern_minimalist | Industry: healthcare"

---

## Script 01: Extract Pairs from Templates

**File:** `scripts/01_extract_pairs.py`
**Input:** `example_templates/` directory (298 YAML template files)
**Output:** `data/pairs/extracted_pairs.jsonl` (~939 pairs)

### What It Does

This script reads every YAML template file in `example_templates/` and creates training pairs. Each template becomes multiple training examples with different prompts that could produce the same output.

### How Template Headers Work

Each template file starts with comment headers that describe it:
```yaml
# Glassmorphism Hero Section
# A split-screen hero with frosted glass effects
# Section type: hero
# Layout: split
# Visual style: glassmorphism
# Industries: SaaS, fintech, design agency
# Base components: layout-row, layout-column, heading, paragraph, button, image
```

The script parses these headers to extract metadata (section type, style, industries, description), then uses the metadata to generate realistic prompts.

### Two Types of Prompts Generated

**1. Natural language (50%)** — What a human would type:
```
"Create a hero section with glassmorphism style for a SaaS company"
"Build a hero, glassmorphism themed"
"I need a hero with frosted glass effects for my website"
```

These come from templates like:
```python
NATURAL_PROMPTS_SECTION = [
    "Create a {section_type} section{style_clause}{industry_clause}",
    "Build a {section_type}{style_clause}{industry_clause}",
    ...
]
```

The `{style_clause}`, `{industry_clause}`, `{desc_clause}` slots are randomly filled from the template metadata, creating variety.

**2. Structured (50%)** — Key-value format:
```
"Section: hero\nStyle: glassmorphism\nDescription: A split-screen hero with frosted glass"
"Type: hero\nVisual style: glassmorphism\nIndustry: SaaS"
```

This teaches the model to respond to both conversational and structured prompts.

### Handling Long Templates (Compression)

Some templates are very large (22,000+ characters ≈ 6,500 tokens). Since our model's context window is 4,096 tokens, these can't fit. The script uses smart compression:

```python
def _compress_section_yaml(yaml_body, max_chars=8000):
```

**How compression works:**
- Keep the top 2 levels of component nesting fully (section structure, columns)
- For deeply nested components (level 3+), keep only the component name
- This teaches the model section *structure* without overwhelming it

**Critical safeguard:** The model is never shown placeholder text like `# ... (omitted)`. It only sees component names without properties. Combined with the system prompt ("Always include full properties"), the model learns to expand component names into full property blocks.

### Component-Level Pairs

Besides section-level pairs, the script extracts individual components:
```yaml
# From a hero section, extract just the button:
- name: button
  properties:
    layout:
      widthMode: fit
    typography:
      content: "Get Started"
      size: md
      weight: semibold
    appearance:
      color: "#FFFFFF"
      backgroundColor: *color-accent
      radius: pill
```

This teaches the model to generate standalone components, not just full sections.

### Key Concept: `_strip_page_wrapper()`

Templates are stored as full page documents:
```yaml
- name: page
  slug: home
  properties: ...
  components:
    - name: layout-row    ← This is what we want
      properties: ...
```

The script strips the page wrapper to extract just the section-level YAML, since that's what the builder agent generates.

---

## Script 02: Component Knowledge Pairs

**File:** `scripts/02_component_knowledge_pairs.py`
**Input:** `config/COMPONENT_SYNTAX_REFERENCE.md` (37 component definitions)
**Output:** `data/pairs/component_knowledge_pairs.jsonl` (~254 pairs)

### Why This Script Exists

Script 01 extracts *examples* of components in context. Script 02 teaches the model *rules* — what properties each component supports, valid values, common mistakes.

Think of it as:
- Script 01 = "Here's how hero sections look" (learning by example)
- Script 02 = "Here are the rules for layout-row" (learning by reference)

### What It Parses

The `COMPONENT_SYNTAX_REFERENCE.md` file contains structured blocks like:
```markdown
## Component: layout-row

A horizontal container that arranges children in a row.

### Syntax
```yaml
- name: layout-row
  properties:
    layout:
      wrap: wrap       # wrap | nowrap
      gap: md          # Spacing token
      align: center    # flex align-items
      justify: center  # flex justify-content
    spacing:
      paddingBlock: lg
      paddingInline: lg
    appearance:
      backgroundColor: "#F5F5F5"
  components:
    - name: layout-column
      ...
```

### Key Notes
- Direct children MUST have layout.widthMode set
- wrap: nowrap for split layouts (hero, side-by-side)
- Always use string tokens for widthMode: "50", "33", "66"
```

### Four Types of Knowledge Pairs Generated

**1. Component Syntax** (148 pairs) — "Show me the syntax for X"
```
Prompt: "What properties does layout-row support in SwiftSites?"
Completion: [full syntax block from reference]
```

**2. Component Usage** (67 pairs) — Natural prompts per component
```
Prompt: "Create a section wrapper with centered content and padding."
Completion: [layout-row syntax showing centered content]
```

**3. Component Knowledge** (38 pairs) — Rules + notes
```
Prompt: "What are the key rules for using layout-row?"
Completion: [syntax block + key notes text]
```

**4. Common Mistakes** (1+ pairs) — What NOT to do
```
Prompt: "What are common mistakes when using layout-row?"
Completion: [mistakes examples from reference]
```

### Why 37 Components Get Separate Treatment

The builder model must deeply understand *every* component. Without Script 02, rare components (like `calendar`, `panorama-display`) might only appear 1-2 times in template examples. Script 02 ensures every component gets at least 5-10 dedicated training pairs covering its full API.

---

## Script 03: Augment Data

**File:** `scripts/03_augment_data.py`
**Input:** `data/pairs/*.jsonl` (all pairs from scripts 01 + 02)
**Output:** `data/augmented/augmented_pairs.jsonl` (~3,126 pairs)

### Why Augmentation?

With only ~1,193 original pairs, the model might:
- **Overfit** — memorize exact prompt wordings instead of learning patterns
- **Be brittle** — only respond correctly to prompts that look like training data

Augmentation creates *variations* of existing pairs to teach the model that many different prompts should produce the same (or similar) output.

### How It Works

For each original pair, generate 1-2 augmented variants:

#### Variant 1: Prompt Rephrasing

Change the opening verb/structure while keeping the meaning:
```
Original:  "Create a hero section with modern style"
Rephrased: "I need a hero section with modern style"
           "Can you create a hero section with modern style"
           "Please generate a hero section with modern style"
```

The completion stays the same — teaching the model that different phrasings map to the same output.

#### Variant 2: Context Injection (for section/component pairs)

Add style, industry, or detail context:
```
Original:  "Create a pricing section"
Injected:  "Create a pricing section, with glassmorphism style, for a SaaS company"
           "Create a pricing section, in a clean Scandinavian style, that converts visitors"
```

Again, the completion stays the same. This teaches the model that additional context doesn't change the core structure — it just influences styling choices.

### The Math

```
1,193 original pairs
× ~1.6 augmentation (1 rephrase + sometimes 1 context-inject)
= ~3,126 total pairs
```

### Important: Same Completion, Different Prompts

The YAML completion is never modified during augmentation. Only the prompt changes. This is crucial because:
1. The YAML is already validated (from templates)
2. We want the model to learn prompt→YAML mapping, not create new YAML patterns
3. Modified YAML might introduce errors

---

## Script 04: Validate Dataset

**File:** `scripts/04_validate_dataset.py`
**Input:** `data/augmented/augmented_pairs.jsonl`
**Output:** `data/validated/validated_pairs.jsonl` (~2,579 pairs)

### Why Validation Matters

"Garbage in, garbage out" — if we train on broken YAML, the model learns to produce broken YAML. This script is the quality gate.

### What Gets Checked

#### 1. Length Validation

```python
MAX_COMPLETION_CHARS = int(MAX_SEQ_LENGTH * 0.75 * 3.5)  # ~10,752 chars
```

Why 75%? The training sequence includes system prompt + user prompt + completion. If the completion alone exceeds 75% of the token budget, the full sequence won't fit in the model's context window (4,096 tokens). Such pairs would be truncated during training, teaching the model incomplete patterns.

#### 2. Deduplication

```python
hash(prompt + "|||" + completion)
```

Exact duplicate pairs waste training compute and can cause overfitting on specific examples. We hash on prompt+completion together (not just completion) because the same YAML legitimately appears with different prompts.

#### 3. YAML Parse Validation

Attempts to parse the YAML with PyYAML's `safe_load()`. Catches:
- Broken indentation
- Invalid characters
- Malformed mappings

**Special case:** YAML aliases (`*color-background`) are tolerated because our templates use YAML anchors defined at the site level — individual section snippets reference but don't define them.

#### 4. Structure Validation

For component/section YAML, checks that `- name:` structure exists. A completion without any component definition is useless for training.

### Rejection Statistics (Typical Run)

```
Input:    3,126 pairs
Valid:    2,579 (82.5%)
Rejected:   547
  yaml_parse: 377  (anchors, inline comments with colons)
  length:     162  (very long templates exceeding token budget)
  duplicate:    8  (exact duplicates from augmentation)
```

An 82% pass rate is healthy. The rejected pairs are genuinely problematic — either too long for the model or have syntax issues that would teach bad habits.

---

## Script 05: Prepare Training JSONL

**File:** `scripts/05_prepare_jsonl.py`
**Input:** `data/validated/validated_pairs.jsonl`
**Output:** `data/final/train.jsonl` (2,321 pairs), `data/final/eval.jsonl` (258 pairs)

### What Format Does the Trainer Expect?

The SFTTrainer (Supervised Fine-Tuning Trainer) expects a `text` field containing the full conversation in ChatML format:

```
<|im_start|>system
You are a SwiftSites YAML code generator...<|im_end|>
<|im_start|>user
Create a hero section with modern style.<|im_end|>
<|im_start|>assistant
- name: layout-row
  properties:
    layout:
      wrap: nowrap
  components:
  ...<|im_end|>
```

### Why ChatML?

Qwen2.5 models were pre-trained with ChatML format (`<|im_start|>`, `<|im_end|>` tokens). By matching this format, our fine-tuning data aligns with what the model already understands about conversation structure.

The model learns: "After seeing a user message about creating a section, I should output SwiftSites YAML as the assistant."

### The System Prompt

```python
SYSTEM_PROMPT = (
    "You are a SwiftSites YAML code generator. "
    "Generate valid, complete SwiftSites component YAML based on the user's request. "
    "Always include full properties for every component — never abbreviate or omit properties. "
    "Use correct component names, property groups (layout, spacing, appearance, typography), and nesting. "
    "Output only YAML code without explanation."
)
```

This system prompt appears in every training example. The model learns to follow these instructions as a baseline behavior. Key phrases:
- **"Always include full properties"** — Prevents compressed/abbreviated output
- **"Output only YAML code"** — No explanatory text, no markdown fences
- **"property groups (layout, spacing, appearance, typography)"** — Reinforces correct structure

### Stripping Markdown Fences

Training completions have markdown fences stripped:
```python
if completion.startswith("```yaml"):
    completion = completion[7:]  # Remove opening fence
```

We train the model to output raw YAML, not markdown-wrapped YAML. The agent layer can add fences if needed.

### Train/Eval Split

```python
TRAIN_EVAL_SPLIT = 0.9  # 90% train, 10% eval
```

- **Training set (90%):** What the model learns from
- **Eval set (10%):** Held-out examples to measure generalization

The eval set is critical for detecting **overfitting**. If training loss keeps dropping but eval loss starts rising, the model is memorizing rather than learning patterns.

```
Epoch 1:  train_loss=1.2  eval_loss=1.3  (both improving → good)
Epoch 2:  train_loss=0.6  eval_loss=0.7  (both improving → good)
Epoch 3:  train_loss=0.3  eval_loss=0.4  (both improving → good)
Epoch 5:  train_loss=0.1  eval_loss=0.8  (diverging → OVERFITTING!)
```

### Shuffling

Data is shuffled before splitting. Without shuffling, the eval set might contain only the last section types processed, giving a biased evaluation.

---

## Script 06: Analyze Dataset

**File:** `scripts/06_analyze_dataset.py`
**Input:** `data/validated/validated_pairs.jsonl` + `data/final/train.jsonl` + `data/final/eval.jsonl`
**Output:** Console report (no file output)

### What It Measures

#### 1. Token Distribution

```
Token Distribution (estimated):
  Total samples: 2579
  Avg tokens:    1273
  Min tokens:    160
  Max tokens:    3219
  Over budget:   0 (>4096)
```

**Why this matters:** If average tokens are too high (>3000), many sequences get truncated during training. If too low (<200), the model doesn't learn complex patterns. Our avg of 1,273 is ideal — complex enough to learn structure, short enough to fit many in context.

#### 2. Prompt Kind Distribution

```
natural:              55.5%   ← Natural language prompts
structured:           20.6%   ← Key-value structured prompts
component_syntax:     11.2%   ← Component syntax reference
component_usage:       7.8%   ← Component usage examples
component_knowledge:   2.8%   ← Component rules/notes
component:             2.1%   ← Standalone component pairs
```

**Why this matters:** The model will generate output proportional to what it sees in training. 55% natural prompts means it will respond well to natural language (the most common use case). The 11% component_syntax ensures deep property knowledge.

#### 3. Section Type Coverage

```
hero:           352 pairs
cta:            261 pairs
features:       225 pairs
testimonials:   124 pairs
pricing:        115 pairs
...
```

**Why this matters:** If "hero" has 352 pairs but "schedule" has only 33, the model will be much better at generating heroes than schedules. This imbalance is acceptable because hero sections are also more commonly requested.

#### 4. Component Coverage

```
Components covered: 36 of 37
Missing: media-caption
```

**Why this matters:** If a component has zero training pairs, the model won't know how to generate it. This report identifies gaps so you can add more examples.

#### 5. Augmentation Ratio

```
Original pairs:   1,005
Augmented pairs:  1,574
Augmentation ratio: 1.57x
```

**Why this matters:** Too little augmentation (<1.5x) means limited prompt variety. Too much (>3x) means the model sees the same completions too many times and overfits to them.

### What To Do With This Report

- **Missing components?** → Add templates to `example_templates/` or update Script 02
- **Over token budget?** → Reduce MAX_SEQ_LENGTH or compress more aggressively
- **Unbalanced section types?** → Add more templates for underrepresented types
- **Low augmentation ratio?** → Increase AUGMENTATION_MULTIPLIER in config

---

## Training (Script 07)

**File:** `scripts/07_train.py`

### The Training Loop Explained

```python
trainer.train()
```

Behind this one line, thousands of steps happen:

```
For each epoch (3 total):
  For each batch (2,321 samples ÷ effective_batch_8 ≈ 290 steps):
    1. Load batch of text sequences
    2. Tokenize into token IDs
    3. Forward pass: model predicts next token at each position
    4. Compute cross-entropy loss (prediction vs. actual)
    5. Backward pass: compute gradients for LoRA params only
    6. Accumulate gradients (8 steps before updating)
    7. Update LoRA weights using AdamW optimizer
    8. Log metrics every 10 steps
    9. Evaluate on eval set every 100 steps
    10. Save checkpoint every 200 steps
```

### Packing (`packing=True`)

Without packing:
```
Batch 1: [pad pad pad pad ... short_example_1 ... pad pad pad]  ← Wasted compute on padding
Batch 2: [pad pad ... short_example_2 ... pad pad pad pad pad]
```

With packing:
```
Batch 1: [example_1 ... example_2 ... example_3 ... example_4]  ← No wasted tokens!
```

Multiple short examples are concatenated into a single sequence (up to MAX_SEQ_LENGTH), separated by EOS tokens. This dramatically improves training efficiency.

### What "Eval Loss < 0.5" Means

Cross-entropy loss measures how surprised the model is by the correct next token:
- **Loss = 3.0:** Model has almost no idea what comes next (untrained)
- **Loss = 1.0:** Model has some idea but often wrong
- **Loss = 0.5:** Model predicts most tokens correctly
- **Loss = 0.1:** Model predicts almost perfectly (possibly overfitting)

For our task, loss < 0.5 means the model reliably produces the correct SwiftSites YAML structure.

---

## Export & Deploy (Scripts 08-10)

### Step 8: Merge LoRA (`08_merge_model.py`)

After training, we have:
- Base model (frozen, 4-bit quantized)
- LoRA adapter weights (small, trained)

Merging combines them into a single model:
```
merged_weight = base_weight + (B × A) × (alpha/rank)
```

This produces a standard model file that doesn't need the PEFT library at runtime.

### Step 9: Convert to GGUF

GGUF is the format Ollama uses. The conversion:
```
HuggingFace format (merged/) → GGUF float16 → GGUF Q4_K_M (quantized)
```

Q4_K_M quantization reduces the model from ~6 GB (fp16) to ~2 GB while maintaining quality. The "K_M" means it uses a k-quant method with medium precision — good balance of size vs. quality.

### Step 10: Ollama Import

The `Modelfile` tells Ollama:
- Where to find the GGUF weights
- What chat template to use (ChatML for Qwen2.5)
- Generation parameters (temperature=0.3 for deterministic YAML, max tokens=4096)

After `ollama create swiftsites-coder-3b`, the model is available locally like any other Ollama model. Zero code changes needed in the SwiftSites codebase — just update `RAG_MODEL_NAME` in `.env`.

---

## Prerequisites — Software Installation

### 1. Python Environment

```bash
# Create venv with --system-site-packages to inherit globally installed PyTorch
python -m venv C:\Users\sannepu\finetune-env --system-site-packages
C:\Users\sannepu\finetune-env\Scripts\activate
```

### 2. CUDA Toolkit

Already installed (CUDA 12.8). Verify:
```bash
nvcc --version
nvidia-smi
```

### 3. PyTorch with CUDA

```bash
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu128
```

Verify:
```bash
python -c "import torch; print(torch.cuda.is_available()); print(torch.cuda.get_device_name(0))"
```

### 4. Training Libraries

```bash
pip install transformers>=4.48.1 trl>=0.14.0 peft>=0.14.0 accelerate>=0.34.0
pip install bitsandbytes>=0.45.0 datasets>=2.20.0 sentencepiece protobuf
```

### 5. Data Libraries

```bash
pip install pyyaml tqdm
```

### 6. Model Conversion (llama.cpp)

```bash
git clone https://github.com/ggerganov/llama.cpp.git C:\Users\sannepu\llama.cpp
cd C:\Users\sannepu\llama.cpp
pip install -r requirements.txt
```

---

## Deep Dive: Gradient Accumulation & Learning Rate

### Gradient Accumulation — The "Read Multiple Essays Before Grading" Trick

Your GPU can only process 1 training sample at a time (`BATCH_SIZE=1` — that's all 6GB allows). But updating the model after just 1 sample is like changing your grading rubric after reading a single essay — too reactive, too noisy.

**Gradient accumulation** lets you "virtually" train on larger batches:

```
Without accumulation (effective batch = 1):
  Sample 1 → compute gradient → UPDATE weights
  Sample 2 → compute gradient → UPDATE weights    ← noisy, unstable
  Sample 3 → compute gradient → UPDATE weights

With accumulation = 8 (effective batch = 8):
  Sample 1 → compute gradient → store
  Sample 2 → compute gradient → add to stored
  Sample 3 → compute gradient → add to stored
  Sample 4 → compute gradient → add to stored
  Sample 5 → compute gradient → add to stored
  Sample 6 → compute gradient → add to stored
  Sample 7 → compute gradient → add to stored
  Sample 8 → compute gradient → add to stored
       → AVERAGE all 8 gradients → UPDATE weights    ← smooth, stable
```

**The key insight:** Memory usage = batch_size (1 sample). Training quality = effective batch (8 samples). You get the quality of a big batch while only paying the memory cost of a small one.

**The tradeoff with total steps:**
```
total_steps = (num_samples × epochs) / (batch_size × accumulation)

accum=8:  3196 × 1 / (1 × 8)  = ~138 steps (more updates, finer learning)
accum=16: 3196 × 1 / (1 × 16) = ~69 steps  (fewer updates, coarser learning)
accum=32: 3196 × 1 / (1 × 32) = ~35 steps  (very few updates, fast but rough)
```

Higher accumulation = faster training (fewer steps) but each step "averages out" more individual signals, potentially smoothing away useful details about rare components.

### Learning Rate — How Hard to Turn the "Knowledge Dial"

Every training step does this to each model weight:

```
new_weight = old_weight - learning_rate × gradient
```

The **gradient** tells the model *which direction* to adjust (e.g., "this weight should go down to reduce loss"). The **learning rate** controls *how far* to move in that direction.

**Analogy: Tuning a radio dial**

| LR Value | Behavior | Risk |
|----------|----------|------|
| 1e-3 (too high) | Spinning the dial wildly | Never finds the station (divergence) |
| 2e-4 (aggressive) | Big turns, finds station fast | Might overshoot past it |
| 1.5e-4 (our choice) | Moderate turns, good balance | Sweet spot for single-epoch |
| 2e-5 (conservative) | Tiny turns, very precise | Takes 10x longer to converge |
| 1e-6 (too low) | Barely moving | Training never converges |

**Why LR and epochs are linked:**
- 3 epochs + LR 2e-5 = the model sees each sample 3 times with small adjustments each time → slowly learns
- 1 epoch + LR 1.5e-4 = the model sees each sample once, so each adjustment must be bigger → learns same amount in fewer steps

**The cosine schedule:**
```
LR over time:

1.5e-4 │    ╭──╮
       │   ╱    ╲
       │  ╱      ╲
       │ ╱        ╲
1e-5   │╱          ╲___
       └─────────────────
       step 0    step 69    step 138
       (warmup)  (peak)     (end)
```

Starts low (warmup), rises to peak, then smoothly decays. This prevents:
- Early instability (warmup)
- Late-training "unlearning" (decay to near-zero)

### How They Interact

```
┌─────────────────────────────────────────────────────┐
│ Effective learning per update:                      │
│                                                     │
│   weight_change = LR × (sum of gradients / accum)   │
│                                                     │
│   accum=8, LR=1.5e-4:                              │
│     Stable gradients (8 samples averaged)           │
│     Moderate step size (1.5e-4)                     │
│     138 total updates (good for overnight run)      │
│                                                     │
│   If you halve accum → double steps, noisier grads  │
│   If you double LR → same steps, bigger changes     │
└─────────────────────────────────────────────────────┘
```

---

## Hyperparameters Explained

### Model Selection

| Parameter | Value | Why |
|-----------|-------|-----|
| `BASE_MODEL_ID` | Qwen2.5-Coder-3B-Instruct | YAML/code specialist, fits 6GB with QLoRA |
| `MAX_SEQ_LENGTH` | 2048 | Halved for speed; 90%+ sections fit in 2048 tokens. Longer samples truncated. |

### LoRA Parameters

| Parameter | Value | Explanation |
|-----------|-------|-------------|
| `LORA_R` | 16 | **Rank** — capacity of adapter. Higher = more expressive but more memory. 16 is sufficient for a 3B model learning a specific format. |
| `LORA_ALPHA` | 32 | **Scaling factor** — `alpha/rank = 32/16 = 2`. Controls how much LoRA influences output. Rule of thumb: alpha = 2×rank. |
| `LORA_DROPOUT` | 0.05 | **Regularization** — 5% of adapter neurons randomly disabled during training. Prevents overfitting. Low because we have limited data. |
| `LORA_TARGET_MODULES` | q,k,v,o,gate,up,down | **Which layers get adapters.** Attention projections (q,k,v,o) + MLP layers (gate,up,down). More modules = better quality but more memory. |

### Training Parameters

| Parameter | Value | Explanation |
|-----------|-------|-------------|
| `LEARNING_RATE` | 1.5e-4 | How much to adjust weights per step. Higher than typical (2e-5) because we only do 1 epoch — the model needs to learn faster per step. Slightly reduced from 2e-4 since we now have more steps (138 vs 69). |
| `NUM_EPOCHS` | 1 | Single pass through data. Higher LR compensates. Can resume for epoch 2 if quality is insufficient. |
| `WARMUP_RATIO` | 0.03 | First 3% of steps use a gradually increasing learning rate. Shorter than usual because fewer total steps. |
| `BATCH_SIZE` | 1 | Number of sequences processed simultaneously. Must be 1 for 6GB VRAM. |
| `GRADIENT_ACCUMULATION` | 8 | Accumulate gradients over 8 steps before updating weights. Effective batch size = 1×8 = 8. Balances step count (~138) with training speed for an overnight run. |
| `OPTIMIZER` | paged_adamw_8bit | AdamW optimizer with 8-bit states (saves memory) and paged memory (prevents OOM spikes). |
| `LR_SCHEDULER` | cosine | Learning rate follows a cosine curve: starts high, smoothly decreases to near-zero. Matches the natural "fast learning → fine-tuning" progression. |

### Speed-Tuned Configuration (6GB Laptop GPU Reality)

The original config (3 epochs, LR=2e-5, accum=8, seq_len=4096) produced ~1,198 steps at ~11 min/step = **220+ hours**. That's impractical on a laptop GPU. Here's the retuned config targeting **8-12 hours**:

| Parameter | Before | After | Why the Change |
|-----------|--------|-------|----------------|
| `NUM_EPOCHS` | 3 | 1 | Biggest time saver (3x reduction). 1 epoch with higher LR can learn the format. We can always train another epoch later with `resume_from_checkpoint`. |
| `MAX_SEQ_LENGTH` | 4096 | 2048 | Most sections fit in 2048 tokens. Halving seq len means less memory per step → faster iteration. Samples >2048 tokens get truncated, but that's rare. |
| `GRADIENT_ACCUMULATION` | 8 | 16 | Effective batch: 1x16=16 instead of 1x8=8. Fewer total steps (half as many), more stable gradients from larger effective batch. |
| `LEARNING_RATE` | 2e-5 | 2e-4 | With only 1 epoch, the model has fewer steps to learn. Higher LR compensates — each step makes a bigger adjustment. 2e-4 is aggressive but standard for single-epoch LoRA. |
| `WARMUP_RATIO` | 0.05 | 0.03 | Fewer total steps means warmup should be shorter (we don't want to spend 5% of a single epoch just ramping up). |

**New math:**
```
total_steps = (3,196 samples x 1 epoch) / (1 batch x 16 accum) = ~200 steps
time = 200 steps x ~6 min/step* = ~20 hours
```
*Shorter seq_len (2048 vs 4096) should cut per-step time from ~11min to ~5-6min.

**The tradeoffs:**
- **Less exposure:** Model sees each example once instead of 3 times. Mitigated by higher LR.
- **Truncation:** Samples >2048 tokens lose their tail. Acceptable because 90%+ of sections fit in 2048.
- **Larger LR risk:** 2e-4 can occasionally overshoot. The cosine scheduler and warmup help stabilize it.
- **Fewer gradient samples:** 16 accum steps means the model "looks at more context" before updating, which is actually a *good* thing for quality.

**If quality is poor after 1 epoch:**
You can resume training for a second epoch with a lower LR:
```python
trainer.train(resume_from_checkpoint="output/checkpoints/checkpoint-200")
```
Or re-run with `NUM_EPOCHS=2` and `LEARNING_RATE=5e-5` (lower LR for refinement pass).

### Why These Specific Values?

The hyperparameters balance training quality against a 6GB VRAM constraint:
- **Batch=1, accum=16:** Effective batch of 16 gives stable gradients with minimal memory
- **LR=2e-4:** Aggressive for single-epoch training (compensates for limited passes)
- **1 epoch × 3,196 samples / 16 effective batch = ~200 total steps:** Achievable overnight
- **Cosine scheduler:** Still prevents late-training instability
- **R=16:** Sweet spot for 3B model — R=8 underfits, R=32 is overkill

---

## Troubleshooting

### Out of Memory (OOM)

If you get CUDA OOM during training:
1. Reduce `MAX_SEQ_LENGTH` from 4096 → 2048
2. Ensure `gradient_checkpointing=True`
3. Close all other GPU apps (browser hardware acceleration, running Ollama models)
4. Set environment variable: `PYTORCH_CUDA_ALLOC_CONF=expandable_segments:True`
5. If still OOM: reduce `LORA_TARGET_MODULES` to just `["q_proj", "v_proj"]`

### bitsandbytes on Windows

```bash
pip install bitsandbytes-windows
# Or use WSL2 (recommended for training)
```

### Slow Training

Expected: ~8-20 hours for 1 epoch (6GB laptop GPU). If much slower:
- Check GPU utilization: `nvidia-smi -l 1` (should show >90% GPU usage)
- Ensure `device_map="auto"` puts model on GPU (not CPU)
- `packing=True` reduces wasted compute from padding
- Close ALL other GPU applications (Ollama, browser hardware acceleration, VS Code GPU acceleration)
- If still too slow: reduce `LORA_TARGET_MODULES` to `["q_proj", "v_proj"]` (fewer adapters = faster)

### Model Quality Issues

If the fine-tuned model produces poor YAML:

| Symptom | Likely Cause | Fix |
|---------|-------------|-----|
| Generates random text | Not enough training | More epochs (5-7) or more data |
| Always same output | Overfitting | More augmentation, higher dropout |
| Missing properties | Training data too compressed | Ensure Script 05 system prompt emphasizes full properties |
| Wrong component names | Insufficient component knowledge | Run Script 02, ensure all components covered |
| Broken indentation | YAML in training has inconsistent indentation | Fix source templates |

---

## Execution Summary

```bash
# 1. Activate environment
C:\Users\sannepu\finetune-env\Scripts\activate

# 2. Prepare data (run in order)
cd C:\Users\sannepu\finetune
python scripts/01_extract_pairs.py
python scripts/02_component_knowledge_pairs.py
python scripts/03_augment_data.py
python scripts/04_validate_dataset.py
python scripts/05_prepare_jsonl.py
python scripts/06_analyze_dataset.py

# 3. Train (~8-20 hours on 6GB laptop GPU)
$env:PYTHONUTF8 = "1"
C:\Users\sannepu\llm-finetune-env\Scripts\python.exe scripts/07_train.py

# 4. Export
python scripts/08_merge_model.py
cd C:\Users\sannepu\llama.cpp
python convert_hf_to_gguf.py "C:\Users\sannepu\finetune\output\merged" --outtype f16 --outfile swiftsites-coder-3b-f16.gguf
.\llama-quantize.exe swiftsites-coder-3b-f16.gguf swiftsites-coder-3b-Q4_K_M.gguf Q4_K_M

# 5. Deploy
cd C:\Users\sannepu\finetune
ollama create swiftsites-coder-3b -f Modelfile
# Update .env: RAG_MODEL_NAME=swiftsites-coder-3b
# Restart Flask
```

---

## Verification Checklist

1. **Dataset gate** — Script 06 shows all major components and section types covered
2. **Training gate** — Eval loss < 0.5 by epoch 3
3. **Smoke test** — `ollama run swiftsites-coder-3b "Build a glassmorphism hero for SaaS"` → valid YAML
4. **Render test** — Wrap output in site+page shell, POST /render → 200 + valid HTML
5. **Integration test** — Set env vars, restart Flask, run chat prompts covering create_section, modify, create_page

---

## Key Takeaways

1. **Fine-tuning teaches format, not knowledge.** The model already knows YAML — we teach it *our* YAML.
2. **QLoRA makes it possible on consumer GPUs.** 4-bit quantization + small adapters = 3B model training on 6GB.
3. **Data quality > data quantity.** 2,500 validated pairs beats 10,000 unvalidated ones.
4. **Agent-agnostic training = flexibility.** The model learns output format, not input format.
5. **The pipeline is reproducible.** Add new templates → re-run pipeline → retrain.

---

**Hardware:** NVIDIA RTX A1000 6GB Laptop GPU, Windows 11, CUDA 12.8
**Model:** Qwen2.5-Coder-3B-Instruct
**Method:** QLoRA (4-bit NF4 + BFloat16 compute + LoRA rank 16)
**Dataset:** ~3,196 train / 356 eval pairs
**Training time:** ~8-20 hours (1 epoch, speed-tuned for 6GB)
**Output:** ~2GB GGUF model for Ollama
