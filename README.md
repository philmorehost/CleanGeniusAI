# CleanGenius AI

> AI-Powered Windows Disk Cleanup Utility with DeepSeek Integration

CleanGenius AI is a modern Windows disk cleanup application designed for developers and power users. Powered by AI models (DeepSeek, OpenAI, Claude, Gemini, Ollama), it automatically scans, analyzes, and provides conservative cleanup recommendations for temporary files, build caches (`node_modules`, `__pycache__`), logs, installers, and registry entries.

---

## 🌟 Key Features

- ⚡ **Multi-Engine Scanning**: Fast scan, Deep scan, Custom folder scan, and Registry analysis.
- 🤖 **Multi-Provider AI Analysis**: DeepSeek (default, cost-effective), OpenAI, Claude, Gemini, and Ollama local models.
- 🛡️ **3-Layer Safety Verification**: Protected path verification, active process lock checking, and system attribute detection.
- 🔄 **Instant Rollback Point**: Backs up deleted files to a recovery location before deletion so you can restore anytime.
- 📊 **Cost & Usage Dashboard**: Real-time monthly AI API cost tracking with budget limits.
- 💼 **IObitASC-Inspired Dark UI**: Custom frameless titlebar with dark aesthetic.

---

## 🚀 Quick Start

### Prerequisites
- Node.js (v18+)
- Python (3.10+)

### Installation & Execution

1. **Clone the Repository**:
   ```bash
   git clone https://github.com/yourusername/cleangenius-ai.git
   cd cleangenius-ai
   ```

2. **Install Node.js Dependencies**:
   ```bash
   npm install
   ```

3. **Install Python Dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

4. **Environment Setup**:
   ```bash
   cp .env.example .env
   # Edit .env and add your DeepSeek/OpenAI/Gemini API keys
   ```

5. **Run Development Server**:
   ```bash
   npm run dev
   ```

---

## 🛠️ Build Executable Installer

To compile the production `.exe` installer (NSIS & Portable) for Windows:

```bash
npm run build
```

The output setup binaries will be generated under the `dist/` folder.

---

## 📖 Documentation

- [ARCHITECTURE.md](ARCHITECTURE.md) - System design & internal flow.
- [API.md](API.md) - REST API specification for Python Flask backend.
- [CONTRIBUTING.md](CONTRIBUTING.md) - Developer guidelines & environment setup.
- [CHANGELOG.md](CHANGELOG.md) - Version history.

---

## 📄 License

Distributed under the MIT License. See `LICENSE` for details.
