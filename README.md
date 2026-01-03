# AI-OpenSCAD

> **Natural Language to 3D Models** - Generate professional OpenSCAD code and 3D models using plain English.

AI-OpenSCAD is a full-stack web application that transforms natural language descriptions into functional 3D models. Powered by GPT-4 and professional OpenSCAD libraries, it generates properly formatted, renderable code with support for complex features like ISO metric threads, gears, and mechanical parts.

![AI-OpenSCAD Demo](docs/demo.gif)

## ✨ Features

- 🤖 **AI-Powered Generation** - Describe what you want, get working OpenSCAD code
- 💬 **Conversational Editing** - Chat with AI to modify your models iteratively
- 🔩 **Professional Libraries** - Includes threads-scad, BOSL2, MCAD, dotSCAD, Round-Anything
- 🎨 **Interactive 3D Preview** - Real-time rendering with orbit controls and measurements
- 📏 **Proper Threading** - Generate ISO metric threads (M3-M12) that actually work
- 📝 **Clean Code Output** - Professionally formatted, commented OpenSCAD code
- 📦 **STL Export** - Download ready-to-print models
- 🖥️ **Console Logging** - Real-time feedback on generation and rendering

## 🚀 Quick Start

### Prerequisites

- Docker & Docker Compose
- OpenAI API key ([Get one here](https://platform.openai.com/api-keys))

### Installation

```bash
# Clone the repository
git clone https://github.com/yourusername/ai-openscad.git
cd ai-openscad

# Start with the CLI
./ai-openscad start
```

The CLI will:
1. Check for Docker and Docker Compose
2. Create `.env` from template (if needed)
3. Prompt for your OpenAI API key
4. Build and start all services
5. Open at **http://localhost:4100**

### CLI Commands

```bash
./ai-openscad start          # Start all services
./ai-openscad stop           # Stop all services
./ai-openscad restart        # Restart all services
./ai-openscad status         # Show service status
./ai-openscad logs           # View all logs
./ai-openscad logs backend   # View specific service logs
./ai-openscad clean          # Remove all data and containers
```

## 📖 Usage Examples

### Generate New Models

In the top prompt bar, try:
- `"M8 bolt with threads, 30mm long"`
- `"a gear with 24 teeth and center hole"`
- `"mounting bracket with two holes"`
- `"hexagonal nut for M10 bolt"`

### Modify Existing Code

After generating a model, use the chat (bottom-left):
- `"make it 2x bigger"`
- `"add a 5mm hole through the center"`
- `"make the threads M10 instead"`
- `"add chamfered edges"`

### Render & Export

1. Click **"Render"** button to compile and visualize
2. Rotate/zoom the 3D preview with your mouse
3. Click **"Download STL"** to export for 3D printing

## 🏗️ Architecture

```
┌─────────────────┐
│  React Frontend │ (Port 4100)
│  Vite + Monaco  │
└────────┬────────┘
         │
    ┌────▼─────┐
    │  Nginx   │ (Reverse Proxy)
    └────┬─────┘
         │
    ┌────▼──────────┐      ┌──────────┐
    │ FastAPI       │◄────►│  Redis   │
    │ Backend       │      │  Queue   │
    └────┬──────────┘      └──────────┘
         │
    ┌────▼────────────┐
    │ Render Service  │
    │ OpenSCAD + Libs │
    └─────────────────┘
```

**Services:**
- **Frontend** - React SPA with Monaco editor and Three.js viewer
- **Backend** - FastAPI REST API with OpenAI integration
- **Render Service** - OpenSCAD CLI with Xvfb for headless rendering
- **Redis** - Job queue for async rendering

## 🔧 Configuration

### Environment Variables

Create a `.env` file in the project root:

```bash
# OpenAI Configuration
OPENAI_API_KEY=sk-your-openai-api-key-here

# API URLs (defaults shown)
VITE_API_URL=http://localhost:8100
VITE_WS_URL=ws://localhost:8100

# Environment
ENVIRONMENT=development

# Redis
REDIS_URL=redis://redis:6379
```

### Port Configuration

Default ports (configurable in `docker-compose.yml`):
- **Frontend**: 4100
- **Backend**: 8100
- **Render Service**: 8200
- **Redis**: 6379

## 📚 Included Libraries

The system includes professional OpenSCAD libraries:

| Library | Purpose | Example Use |
|---------|---------|-------------|
| **threads-scad** | ISO metric threads | `ScrewThread(outer_diam=8, height=30, pitch=1.25)` |
| **BOSL2** | Advanced shapes & utilities | Rounding, attachments, transforms |
| **MCAD** | Mechanical parts | Gears, bearings, motors |
| **dotSCAD** | Path modeling | Spirals, arcs, patterns |
| **Round-Anything** | Edge rounding | Smooth corners and fillets |

## 🛠️ Development

### Running in Development Mode

```bash
# Start with hot-reload enabled
docker compose up

# View logs
docker compose logs -f backend
docker compose logs -f frontend
docker compose logs -f render-service

# Restart a service
docker compose restart backend
```

### Project Structure

```
ai-openscad/
├── frontend/               # React + TypeScript + Vite
│   ├── src/
│   │   ├── components/
│   │   │   ├── chat/      # Chat interface for modifications
│   │   │   ├── editor/    # Monaco code editor
│   │   │   ├── preview/   # Three.js 3D viewer
│   │   │   ├── prompt/    # Generation input
│   │   │   └── console/   # Real-time logging
│   │   ├── services/      # API client
│   │   └── App.tsx
│   └── package.json
├── backend/               # FastAPI Python
│   ├── app/
│   │   ├── api/v1/       # REST endpoints
│   │   │   ├── generate.py  # AI code generation
│   │   │   ├── chat.py      # Conversational edits
│   │   │   ├── render.py    # Rendering jobs
│   │   │   └── export.py    # STL downloads
│   │   ├── core/
│   │   │   └── ai_generator.py  # OpenAI integration
│   │   └── main.py
│   └── requirements.txt
├── render-service/        # OpenSCAD renderer
│   ├── app/
│   │   ├── renderer.py   # OpenSCAD CLI wrapper
│   │   └── main.py
│   └── Dockerfile        # Includes OpenSCAD + libraries
├── docker-compose.yml
└── .env.example
```

### Adding New Libraries

To add OpenSCAD libraries:

1. Edit `render-service/Dockerfile`:
```dockerfile
RUN cd /usr/share/openscad/libraries && \
    git clone --depth 1 https://github.com/user/library.git library-name
```

2. Update `backend/app/core/ai_generator.py` system prompt with library info

3. Rebuild: `docker compose build render-service`

## 🐛 Troubleshooting

### Common Issues

**"Failed to generate code"**
- Check OpenAI API key in `.env`
- Verify API key has credits
- Check backend logs: `docker compose logs backend`

**"Rendering failed"**
- Check render-service logs: `docker compose logs render-service`
- Verify OpenSCAD syntax in generated code
- Try simpler models first

**Frontend can't connect**
- Ensure all services are running: `docker compose ps`
- Check VITE_API_URL in `.env` matches backend port
- Verify no firewall blocking ports 4100, 8100

**Threads not rendering**
- Threads library takes longer to render (complex geometry)
- Check thread parameters (valid M3-M12 sizes)
- Try pre-made functions: `MetricBolt(diameter=8, length=30)`

### Logs

```bash
# All services
docker compose logs -f

# Specific service
docker compose logs -f backend
docker compose logs -f render-service

# Recent errors
docker compose logs --tail=50 render-service | grep ERROR
```

## 🚢 Production Deployment

### Using Docker Compose (Recommended)

```bash
# Create production environment file
cp .env.example .env.production

# Edit .env.production with production values
nano .env.production

# Build and start
docker compose --env-file .env.production up -d --build

# Setup reverse proxy (nginx/caddy) pointing to port 4100
```

### Environment Variables for Production

```bash
# Required
OPENAI_API_KEY=sk-prod-key-here
ENVIRONMENT=production

# Update URLs for your domain
VITE_API_URL=https://api.yourdomain.com
VITE_WS_URL=wss://api.yourdomain.com

# Security (recommended)
# - Enable HTTPS
# - Set CORS origins in backend/app/main.py
# - Use Redis password
# - Rate limiting on API endpoints
```

### Scaling Considerations

- **Backend**: Can run multiple instances behind load balancer
- **Render Service**: CPU-intensive, scale horizontally for concurrent renders
- **Redis**: Use managed Redis (AWS ElastiCache, Redis Cloud) for HA
- **Storage**: Mount persistent volume for `/app/data`

## 🤝 Contributing

Contributions welcome! Areas of interest:

- Additional OpenSCAD libraries
- UI/UX improvements
- Better error handling
- Performance optimizations
- Documentation & examples

See [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.

## 📄 License

MIT License - see [LICENSE](LICENSE) file for details

## 🙏 Acknowledgments

- [OpenSCAD](https://openscad.org/) - The foundation
- [threads-scad](https://github.com/rcolyer/threads-scad) - Professional threading library
- [BOSL2](https://github.com/BelfrySCAD/BOSL2) - Comprehensive OpenSCAD library
- [MCAD](https://github.com/openscad/MCAD) - Mechanical parts library
- OpenAI GPT-4 - Natural language understanding

## 📬 Support

- Issues: [GitHub Issues](https://github.com/yourusername/ai-openscad/issues)
- Discussions: [GitHub Discussions](https://github.com/yourusername/ai-openscad/discussions)

---

**Built with ❤️ by makers, for makers**
