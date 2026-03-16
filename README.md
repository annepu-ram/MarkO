# Swift Sites - YAML-Based Website Builder (SSR)

## Overview

**Swift Sites** is a YAML-based website builder that uses Server-Side Rendering (SSR) with Python Flask and Jinja2. Users author their websites by writing structured YAML in a browser-based editor, which is then rendered in real-time within an isolated iframe preview.

The YAML structure serves as the single source of truth, ensuring that the editor, live preview, properties inspector, and history remain perfectly synchronized.

### Key Features

- 🎯 **YAML-First Authoring**: Define entire websites through structured YAML.
- ⚡ **Server-Side Rendering**: High-fidelity rendering using Python Flask and Jinja2 templates.
- 👁️ **Isolated Preview**: Real-time preview in an iframe for complete CSS isolation.
- 🎨 **Visual Inspector**: Edit component properties through an intuitive sidebar panel.
- 📦 **Rich Component Library**: 30+ pre-built components (Layouts, Interactive, Media, Marketing, Forms).
- 🤖 **AI-Powered Chat**: Generate and modify YAML using AI (Ollama or Gemini).
- 🔄 **Undo/Redo**: Full history management for all authoring actions.
- 💾 **Instant Export**: Generate a self-contained, production-ready HTML file.

---

## Architecture

### Core Rendering Flow

```
YAML Editor → POST /render → Flask Backend (renderer.py)
                              ↓
                         Jinja2 Environment
                              ↓
                         Component Macros (templates/components/)
                              ↓
                         HTML Response
                              ↓
                    SSR Bridge (postMessage) → Iframe Preview
```

### Key Principles

1.  **YAML Single Source of Truth**: All changes (visual edits, insertions, theme updates) must update the YAML structure first.
2.  **Isolated Environment**: The preview iframe prevents the app's UI styles from leaking into the user's website and vice versa.
3.  **Component-Based**: Each component is a Jinja2 macro, ensuring a modular and extensible architecture.

---

## Quick Start

### Prerequisites

- Python 3.9+
- [Ollama](https://ollama.com/) (optional, for local AI chat)

### Installation

1.  Clone the repository:
    ```bash
    git clone https://github.com/your-repo/swift-sites.git
    cd swift-sites/ssr_python
    ```

2.  Install dependencies:
    ```bash
    pip install -r requirements.txt
    ```

3.  Set up environment variables:
    ```bash
    cp .env.example .env
    # Edit .env with your API keys (Pexels, Pixabay, Ollama/Gemini)
    ```

### Running the Application

1.  Start the Flask server:
    ```bash
    python app.py
    ```

2.  Open your browser to `http://localhost:5000`.

---

## Development

### Directory Structure

```
ssr_python/
├── app.py                    # Flask application entry point
├── config.py                 # Configuration and path constants
├── renderer.py               # Core rendering engine
├── routes/                   # API and view routes
├── config/                   # Component metadata (defaults, schemas, tokens)
├── templates/                # Jinja2 templates and component macros
├── static/                   # Frontend assets (CSS, JS, Icons)
└── tests/                    # Pytest suite
```

### Running Tests

```bash
cd ssr_python
python -m pytest tests/ -v
```

---

## License

MIT License - See [LICENSE](LICENSE) for details.

---

**Swift Sites** - Build beautiful websites with the power of YAML.
