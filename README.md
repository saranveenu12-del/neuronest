# NeuroNest 🧠

> An evolving cognitive AI companion that develops, reasons, and grows alongside the user with deep customization and emotional awareness.

---

## 📁 Repository Structure

This monorepo contains both the core Python AI engine and the modern full-stack web interface:

```
neuronest/
├── neuronest/              # Core Python AI Engine & Backend
│   ├── config/             # System configuration and personality settings
│   ├── core/               # Reasoning engine, self-evolution & cognitive models
│   ├── data/               # Knowledge base, facts, and embeddings
│   ├── emotional/          # Emotional state machine and adaptive resonance
│   ├── interface/          # Terminal CLI & interactive input handlers
│   ├── learning/           # Continuous learning & memory consolidation
│   ├── memory/             # Short-term, long-term, and episodic memory systems
│   ├── web/                # Lightweight Flask web interface & templates
│   ├── main.py             # CLI entry point for NeuroNest
│   ├── web_app.py          # Python web service entry point
│   └── requirements.txt    # Python dependencies
│
├── neuronest-web/          # Modern Full-Stack Web Application
│   ├── client/             # React + Vite frontend with TailwindCSS & Radix UI
│   ├── server/             # Express.js backend with tRPC & LLM integrations
│   ├── shared/             # Shared TypeScript types, constants & schemas
│   ├── drizzle/            # Database schema & migrations
│   └── package.json        # Node.js dependencies and scripts
│
├── .gitignore              # Unified ignore rules (Python, Node, OS, Binaries)
└── README.md               # Monorepo documentation
```

---

## 🚀 Quick Start

### 1. Python Core AI (`neuronest/`)

#### Prerequisites
- Python 3.10+
- (Optional) Local LLM via Ollama

#### Setup & Run
```bash
cd neuronest

# Create virtual environment
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Run CLI Companion
python main.py

# Or launch the Python Web Interface
python web_app.py
```

---

### 2. Full-Stack Web Application (`neuronest-web/`)

#### Prerequisites
- Node.js 18+
- pnpm (recommended) or npm

#### Setup & Run
```bash
cd neuronest-web

# Install dependencies
pnpm install

# Start development server
pnpm run dev
```

---

## 🌟 Key Features

- **Self-Evolving Cognitive Architecture**: Progresses through developmental stages from foundational cognition to maturity.
- **Dynamic Emotional Intelligence**: Contextual emotional adaptation reflecting ongoing user interactions and resonance.
- **Hybrid Memory Systems**: Combines episodic memories, learned facts, and persistent preferences.
- **Modern Interactive UI**: Contemplative, sleek interface with real-time showcases, cognitive telemetry, and chat.

---

## 📜 License

MIT License. Designed with ❤️ for lifelong learning and human-AI collaboration.
