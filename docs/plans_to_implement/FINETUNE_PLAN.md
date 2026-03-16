# Fine-Tuning Phi-4-mini for SwiftSites YAML Generation

## Context

SwiftSites uses a YAML DSL with 31 component types, 180+ properties, and 13 design token categories. The existing Ollama integration (`llm_service.py`) uses a generic model + a 1,160-line system prompt (`LLM_COMPONENT_GUIDE.md`) to generate YAML. A purpose-built fine-tuned model would produce higher-quality YAML with faster inference and no need for the massive system prompt.

**Goal:** Build a complete pipeline — from dataset generation through training to deployment — for fine-tuning `microsoft/Phi-4-mini-instruct` (3.8B) on SwiftSites YAML generation using HuggingFace TRL on Google Colab.

---

## Directory Structure

```
ssr_python/finetune/
├── config.py                        # Central configuration (paths, hyperparams, constants)
├── requirements.txt                 # Python dependencies
├── data/
│   ├── pairs/                       # Step 1-2 output: raw prompt-completion pairs
│   ├── augmented/                   # Step 3 output: augmented pairs
│   ├── validated/                   # Step 4 output: validated + rejected pairs
│   └── final/                       # Step 5 output: train.jsonl, eval.jsonl
├── scripts/
│   ├── 01_extract_pairs.py          # Extract pairs from existing 37 YAML templates
│   ├── 02_generate_synthetic.py     # Generate ~500 pairs via Claude API
│   ├── 03_augment_data.py           # Color swaps, prompt rephrasing, token variation (3x)
│   ├── 04_validate_dataset.py       # 4-level validation pipeline
│   ├── 05_prepare_jsonl.py          # Format for TRL SFTTrainer + train/eval split
│   └── 06_analyze_dataset.py        # Dataset statistics and coverage analysis
├── validation/
│   └── validator.py                 # Reuses renderer.py validation functions
└── notebooks/
    └── phi4_mini_finetune.ipynb     # Colab training notebook
```

---

## Existing Training Data Inventory

### Source Files (37 YAML files, ~22,000 lines)

| Category | Files | Lines | Description |
|----------|-------|-------|-------------|
| Full-page templates | 10 | ~10,050 | bakery, restaurant, bookstore, freshchoice, conference, car_dealer, logistics, hero, all_components_showcase, media_components_test |
| Hero section variants | 15 | ~5,800 | Fullscreen, split-screen, dark mode, gradient, bold typography, storytelling, minimal product, magazine, card-based, asymmetric, video, SaaS, zen, food delivery, portfolio |
| Component test files | 8 | ~4,100 | interactive, blockquote, layout, layout_full, width_mode, text, media, other |
| Metadata files | 4 | ~3,500 | component_defaults.yaml, component_schemas.yaml, schema_tokens.yaml, tokens.yaml |

### Component System Vocabulary

- **31 component types** across 7 categories (layout, text, media, interactive, form, navigation, utility)
- **180+ unique properties** in groups: typography, spacing, appearance, layout, behavior
- **13 token categories** with 70+ valid values (spacing, typography sizes, font weights, border radius, shadow, etc.)
- **Theme system:** YAML anchors (`&color-primary`) and aliases (`*color-primary`)

---

## Implementation Steps

### Step 1: Create `config.py` — Central Configuration

Single source of truth for all paths, model IDs, hyperparameters, and constants.

Key values:
- `BASE_MODEL_ID = "microsoft/Phi-4-mini-instruct"`
- `MAX_SEQ_LENGTH = 4096`
- `LORA_R = 16, LORA_ALPHA = 32, LORA_DROPOUT = 0.05`
- `LEARNING_RATE = 5e-6, NUM_EPOCHS = 3`
- `SYNTHETIC_SAMPLES_TARGET = 500`
- `INDUSTRIES` list (25 industries for prompt diversity)
- `SECTION_TYPES` list (16 section types: hero, pricing, FAQ, etc.)
- All path constants pointing to existing files

### Step 2: Create `scripts/01_extract_pairs.py` — Extract from Existing Templates

Reads all 37 existing YAML files and generates prompt-completion pairs at 3 granularities:

| Pair Type | Source | Expected Count |
|-----------|--------|----------------|
| **Full-page** | 10 templates x 2 prompt variants | ~20 |
| **Section-level** | Top-level components from each template | ~80-100 |
| **Hero variants** | 15 hero/*.yaml files | ~15 |
| **Modification** | Property changes on existing components | ~50-80 |

Each template has manually curated descriptions in a `TEMPLATE_DESCRIPTIONS` dict mapping filename to natural language description.

**Output:** `data/pairs/extracted_pairs.jsonl` (~150-200 pairs)

### Step 3: Create `scripts/02_generate_synthetic.py` — Synthetic Data via Claude API

Uses Claude Sonnet with `LLM_COMPONENT_GUIDE.md` as system context to generate diverse pairs:

| Prompt Category | Strategy | Expected Count |
|-----------------|----------|----------------|
| Full pages (25 industries x 2 variants) | Industry + feature description | ~50 |
| Full pages with theme specs (5 palettes x 5 industries) | Color theme + industry | ~25 |
| Section-level (16 types x 3 industry variants) | Section type + industry | ~48 |
| Component-level (12 specific patterns) | Detailed component request | ~12 |
| Modification tasks (8 patterns) | Change request | ~8 |
| **Remaining to target** | Random combinations | ~357 |

System prompt instructs Claude to output **raw YAML only** (no markdown, no explanations).

**Requires:** `ANTHROPIC_API_KEY` env var, ~$5-10 API cost for 500 calls.
**Output:** `data/pairs/synthetic_pairs.jsonl` (~500 pairs)

### Step 4: Create `scripts/03_augment_data.py` — Data Augmentation (3x)

Three augmentation strategies:

1. **Color swaps** (complex/advanced pairs): Replace hex colors with 8 alternative palettes
2. **Prompt rephrasing** (all pairs): Generate 2 rephrased prompts per original using templates
3. **Token variation** (medium+ complexity): Swap token values (sm->md, bold->semibold) with 50% probability

**Output:** `data/augmented/augmented_pairs.jsonl` (~1,500-2,000 pairs)

### Step 5: Create `validation/validator.py` — 4-Level Validation Engine

Reuses existing functions from `renderer.py`:

| Level | Check | Function Reused |
|-------|-------|-----------------|
| 1. YAML syntax | `yaml.safe_load()` | PyYAML |
| 2. Structure | Component names exist, array props at component level | `merge_component_with_defaults()` |
| 3. Tokens | All token values valid | `validate_token_value()`, `validate_component_properties()` |
| 4. Render | Full HTML render succeeds | `POST /render` endpoint (online mode) |

Pairs with quality_score >= 0.75 pass (allows minor token warnings).

### Step 6: Create `scripts/04_validate_dataset.py` — Run Validation

Processes all augmented pairs through the validator. Outputs:
- `data/validated/validated_pairs.jsonl` — pairs that pass
- `data/validated/rejected_pairs.jsonl` — pairs that fail (for debugging)
- `data/validated/validation_report.json` — pass rate, error breakdown

### Step 7: Create `scripts/05_prepare_jsonl.py` — Format for TRL SFTTrainer

Converts validated pairs to Phi-4-mini chat format:

```json
{"messages": [
  {"role": "system", "content": "<condensed ~200-word system prompt with key YAML rules>"},
  {"role": "user", "content": "<prompt>"},
  {"role": "assistant", "content": "<yaml completion>"}
]}
```

Creates 90/10 train/eval split. **Output:** `data/final/train.jsonl`, `data/final/eval.jsonl`

### Step 8: Create `scripts/06_analyze_dataset.py` — Quality Analysis

Reports on:
- Category distribution (target: 30% full-page, 30% section, 20% component, 20% modification)
- Complexity distribution
- YAML line count stats (min/max/avg/median)
- Component type coverage (all 31 types should appear)
- Token value frequency
- Missing components flagged

### Step 9: Create `notebooks/phi4_mini_finetune.ipynb` — Colab Training

**QLoRA configuration for Phi-4-mini:**

| Parameter | T4 (16GB) | A100 (40GB) |
|-----------|-----------|-------------|
| Quantization | 4-bit NF4, fp16 compute | 4-bit NF4, bf16 compute |
| Batch size | 1 | 4 |
| Gradient accumulation | 8 | 2 |
| Effective batch | 8 | 8 |
| Attention | eager | flash_attention_2 |
| LoRA rank/alpha | 16/32 | 16/32 |
| LoRA targets | all-linear | all-linear |
| Learning rate | 5e-6 (cosine schedule) | 5e-6 (cosine schedule) |
| Epochs | 3 | 3 |
| Optimizer | paged_adamw_8bit | paged_adamw_8bit |
| Packing | enabled | enabled |

Notebook cells:
1. Install dependencies (torch, transformers, trl, peft, bitsandbytes)
2. Auto-detect GPU (T4 vs A100) and set config accordingly
3. Load dataset from uploaded JSONL
4. Load Phi-4-mini with 4-bit quantization (`BitsAndBytesConfig`)
5. Apply LoRA adapter (`prepare_model_for_kbit_training` + `get_peft_model`)
6. Train with `SFTTrainer`
7. Merge LoRA weights into base model
8. Quick inference test with 3 held-out prompts
9. Export cells (GGUF conversion commands, Ollama Modelfile, HuggingFace upload)

### Step 10: Create `requirements.txt`

```
anthropic>=0.40.0
pyyaml>=6.0
requests>=2.31.0
```

Training deps installed in Colab: `torch, transformers==4.48.1, trl==0.14.0, peft==0.14.0, accelerate, bitsandbytes, datasets`

---

## Deployment Options

### Option A: Ollama (recommended — integrates with existing `llm_service.py`)

1. Convert merged model to GGUF via `llama.cpp/convert_hf_to_gguf.py`
2. Quantize to Q4_K_M (~2.5GB file)
3. Create Ollama Modelfile with Phi-4-mini chat template (`<|system|>...<|end|><|user|>...<|end|><|assistant|>`)
4. `ollama create swiftsites-phi4-mini -f Modelfile`
5. Set `OLLAMA_MODEL=swiftsites-phi4-mini` in `.env`

### Option B: HuggingFace Inference Endpoints

Upload merged model to HuggingFace Hub, deploy as serverless endpoint.

### Option C: vLLM Self-Hosted

`python -m vllm.entrypoints.openai.api_server --model ./swiftsites-phi4-mini-merged`
Swap Ollama client for OpenAI client in `llm_service.py`.

---

## Critical Files Referenced

| File | Role in Pipeline |
|------|------------------|
| `LLM_COMPONENT_GUIDE.md` | System context for synthetic generation + condensed training system prompt |
| `component_defaults.yaml` | Component name validation, default property trees |
| `ssr_python/renderer.py` | `validate_token_value()`, `validate_component_properties()`, `merge_component_with_defaults()` reused in validator |
| `ssr_python/tokens.yaml` | Token vocabulary for validation |
| `ssr_python/llm_service.py` | Existing Ollama integration; deployment target for fine-tuned model |
| `example_templates/*.yaml` | 10 full-page + 15 hero templates as seed training data |

---

## Execution Order

```bash
cd ssr_python/finetune

# Local dataset pipeline (runs on your machine)
python scripts/01_extract_pairs.py           # ~150-200 pairs from existing templates
python scripts/02_generate_synthetic.py      # ~500 pairs via Claude API ($5-10)
python scripts/03_augment_data.py            # ~1,500-2,000 augmented pairs
python scripts/04_validate_dataset.py        # Filter to valid pairs only
python scripts/05_prepare_jsonl.py           # train.jsonl + eval.jsonl
python scripts/06_analyze_dataset.py         # Verify coverage and distribution

# Upload data/final/ to Google Colab
# Run phi4_mini_finetune.ipynb
# Export GGUF -> Ollama (or HuggingFace/vLLM)
```

---

## Verification

1. **Dataset quality:** `06_analyze_dataset.py` confirms all 31 component types covered, balanced category distribution, no missing tokens
2. **Training:** Monitor eval loss in Colab — should decrease across 3 epochs without diverging
3. **Model quality:** Inference test in notebook Cell 9 with 3 held-out prompts
4. **End-to-end:** After Ollama import, run `ollama run swiftsites-phi4-mini "Create a bakery landing page"` and POST the output to `http://localhost:5000/render` — should return valid HTML
5. **Integration:** Set `OLLAMA_MODEL=swiftsites-phi4-mini` in `.env`, restart Flask, test via the chat widget in the SwiftSites UI

---

## Anticipated Challenges

1. **Data scarcity:** ~22,000 lines across 37 files is small. Synthetic generation (step 3) is critical to reach ~1,500-2,000 samples.
2. **YAML anchor/alias handling:** Theme system (`&color-primary` / `*color-primary`) is non-trivial. Training must prominently feature this pattern.
3. **Long sequences:** Full-page templates can exceed 4096 tokens. Pre-filter during step 7, or split into section-level pairs.
4. **Structural correctness:** The array-at-component-level rule (`items`, `tabs`, `slides`, `columns` outside `properties`) is the most common LLM mistake. Include 50-100 pairs emphasizing this.
5. **Token vocabulary:** Model must learn that `spacing.marginBlock` only accepts fixed values (none, xxs, xs, sm, md, lg, xl, xxl, xxxl, auto). System prompt + training data must reinforce this.
6. **T4 memory:** With 4-bit quantization, Phi-4-mini fits in 16GB. Uses batch_size=1 + gradient_accumulation=8 for safety.

---

## Dataset Size Recommendations

| Target | Minimum | Recommended |
|--------|---------|-------------|
| Phi-4-mini (3.8B) | 500 pairs | 1,500-2,000 pairs |
| With augmentation (3x) | 200 seed | 500-700 seed |

Expected final dataset: **~1,200-1,800 validated pairs** from ~700 seed pairs (150 extracted + 500 synthetic) after augmentation and validation filtering.