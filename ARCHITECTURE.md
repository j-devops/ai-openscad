# AI-OpenSCAD Architecture

## System Overview

AI-OpenSCAD is a microservices-based application that transforms natural language into 3D models through AI code generation and OpenSCAD rendering.

## Architecture Diagram

```
┌─────────────────────────────────────────────────────────────────┐
│                         User Browser                            │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────────────┐  │
│  │ Monaco Editor│  │  Three.js    │  │  Chat Interface      │  │
│  │  (Code)      │  │  (3D View)   │  │  (Modifications)     │  │
│  └──────────────┘  └──────────────┘  └──────────────────────┘  │
└────────────────────────┬────────────────────────────────────────┘
                         │ HTTP/WebSocket
                ┌────────▼────────┐
                │  Nginx Gateway  │ Port 4100 (Reverse Proxy)
                └────────┬────────┘
                         │
        ┌────────────────┼────────────────┐
        │                │                │
   ┌────▼─────┐    ┌────▼────────┐  ┌───▼──────┐
   │ Frontend │    │   Backend   │  │  Redis   │
   │  (React) │    │  (FastAPI)  │◄─┤  Queue   │
   │  Static  │    │   Port 8100 │  └──────────┘
   └──────────┘    └────┬────────┘
                        │ Job Queue
                   ┌────▼──────────────┐
                   │  Render Service   │
                   │    (OpenSCAD)     │
                   │    Port 8200      │
                   └───────────────────┘
```

## Services

### 1. Frontend (React + Vite)

**Technology Stack:**
- React 18 with TypeScript
- Vite for bundling and dev server
- Monaco Editor for code editing
- Three.js + React-Three-Fiber for 3D rendering
- Zustand for state management

**Responsibilities:**
- User interface and interaction
- Code editing with syntax highlighting
- 3D model visualization (STL rendering)
- Chat interface for conversational editing
- Real-time console logging
- WebSocket connection for live updates

**Key Components:**
- `PromptInput` - Natural language generation input
- `CodeEditor` - Monaco-based OpenSCAD editor
- `Preview3D` - Three.js STL viewer with orbit controls
- `ChatInterface` - Conversational modification UI
- `ConsoleLog` - Real-time rendering feedback

**Ports:**
- Development: Vite dev server on 4100
- Production: Static files served by Nginx on 4100

### 2. Backend (FastAPI)

**Technology Stack:**
- Python 3.11+
- FastAPI for REST API
- OpenAI Python SDK for GPT-4 integration
- Redis for job queue
- WebSockets for real-time updates

**Responsibilities:**
- AI code generation via OpenAI API
- Conversational code editing
- Job queue management (rendering tasks)
- File management (.scad, .stl, .png)
- WebSocket server for real-time status
- Input validation and security

**Key Modules:**
- `api/v1/generate.py` - AI generation endpoint
- `api/v1/chat.py` - Conversational editing
- `api/v1/render.py` - Rendering job management
- `api/v1/export.py` - STL/PNG downloads
- `core/ai_generator.py` - OpenAI integration
- `websocket/manager.py` - WebSocket connections

**Endpoints:**
```
POST   /api/v1/generate              # Generate code from prompt
POST   /api/v1/chat                  # Modify code via conversation
POST   /api/v1/render                # Submit render job
GET    /api/v1/render/{job_id}       # Check job status
GET    /api/v1/render/{job_id}/stl   # Download STL
GET    /api/v1/render/{job_id}/png   # Get preview image
WS     /ws/render                    # Real-time updates
```

**Port:** 8100

### 3. Render Service (OpenSCAD Worker)

**Technology Stack:**
- Python 3.11+
- OpenSCAD CLI (headless rendering)
- Xvfb for virtual display
- Redis for job queue processing

**Responsibilities:**
- OpenSCAD code compilation
- STL file generation
- PNG preview rendering
- Job queue processing (consumer)
- Error logging and validation

**Installed Libraries:**
- threads-scad (ISO metric threads)
- BOSL2 (comprehensive utilities)
- MCAD (mechanical parts)
- dotSCAD (path modeling)
- Round-Anything (edge rounding)

**Rendering Process:**
1. Poll Redis queue for jobs
2. Validate .scad file syntax
3. Run OpenSCAD CLI: `openscad -o output.stl input.scad`
4. Generate PNG preview: `openscad -o output.png --imgsize=800,600`
5. Update job status in Redis
6. Notify backend via WebSocket

**Port:** 8200 (internal, health checks)

### 4. Redis

**Responsibilities:**
- Job queue (rendering tasks)
- Session storage
- Caching AI responses (future)

**Data Structures:**
- `render_queue` - List of pending jobs
- `job:{id}:status` - Job metadata and status
- `job:{id}:result` - Rendering results

**Port:** 6379 (internal)

### 5. Nginx (Gateway)

**Responsibilities:**
- Reverse proxy to frontend/backend
- Static file serving (production)
- WebSocket proxy
- CORS headers

**Configuration:**
```nginx
location / {
    proxy_pass http://frontend:3000;
}
location /api {
    proxy_pass http://backend:8000;
}
location /ws {
    proxy_pass http://backend:8000;
    proxy_http_version 1.1;
    proxy_set_header Upgrade $http_upgrade;
    proxy_set_header Connection "upgrade";
}
```

**Port:** 4100 (public)

## Data Flow

### 1. AI Code Generation Flow

```
User enters prompt
    ↓
Frontend → POST /api/v1/generate
    ↓
Backend → OpenAI API (GPT-4)
    ↓
System prompt + user request
    ↓
GPT-4 returns OpenSCAD code
    ↓
Backend validates and returns code
    ↓
Frontend displays in Monaco editor
```

### 2. Conversational Editing Flow

```
User enters chat message
    ↓
Frontend → POST /api/v1/chat
    (sends: current code + modification request)
    ↓
Backend → OpenAI API
    (context: existing code + libraries available)
    ↓
GPT-4 returns modified code
    ↓
Backend returns updated code
    ↓
Frontend updates editor
```

### 3. Rendering Flow

```
User clicks "Render"
    ↓
Frontend → POST /api/v1/render
    (sends: OpenSCAD code)
    ↓
Backend saves .scad file with UUID
    ↓
Backend enqueues job to Redis
    ↓
Backend returns job_id
    ↓
Frontend opens WebSocket connection
    ↓
Render Service polls Redis queue
    ↓
Render Service runs OpenSCAD CLI
    (generates .stl and .png)
    ↓
Updates job status in Redis
    ↓
Backend sends WebSocket notification
    ↓
Frontend fetches STL and displays 3D preview
```

### 4. Export Flow

```
User clicks "Download STL"
    ↓
Frontend → GET /api/v1/render/{job_id}/stl
    ↓
Backend serves file with Content-Disposition header
    ↓
Browser downloads .stl file
```

## File Storage

**Directory Structure:**
```
/app/data/
├── scad_files/
│   └── {job_id}.scad      # Source code
├── renders/
│   ├── {job_id}.stl       # 3D models
│   └── {job_id}.png       # Previews
└── logs/
    └── render_{job_id}.log # Error logs
```

**File Naming:**
- UUID v4 for all files (prevents path traversal)
- Files auto-deleted after 24 hours (cleanup job)

## Security Considerations

### Input Validation
- Code size limits (max 100KB)
- Pattern matching for path traversal attempts
- No user-controlled file paths
- Sanitize all inputs before OpenAI API calls

### API Key Management
- Environment variables only
- Never logged or exposed in responses
- Separate keys for dev/production

### Container Security
- Non-root users in all containers
- Resource limits (CPU/memory)
- Read-only filesystems where possible
- Network isolation (internal Docker network)

### Rate Limiting
- API endpoint throttling (10 req/min per IP)
- OpenAI API usage monitoring
- Job queue size limits

### CORS
- Restricted to frontend domain only
- No wildcard origins in production

## OpenAI Integration

### System Prompt Strategy

The AI generator uses a carefully crafted system prompt that includes:

1. **Role Definition**: "Expert OpenSCAD developer"
2. **Library Documentation**: Functions from installed libraries
3. **Code Examples**: Common patterns (threads, gears, etc.)
4. **Constraints**: Output only valid code, proper formatting
5. **Best Practices**: Use library functions, add comments

### Context Management

- **Generation**: Full library docs + user prompt
- **Editing**: Existing code + modification request + library context
- **Token Management**: Truncate library docs if needed (~4000 tokens max)

### Model Selection
- Primary: `gpt-4-turbo-preview` (better code quality)
- Fallback: `gpt-3.5-turbo` (faster, cheaper)
- Temperature: 0.3 (balance creativity and correctness)

## Performance Considerations

### Rendering Performance
- OpenSCAD rendering is CPU-intensive
- Complex threads can take 30-60 seconds
- Scale render-service horizontally for concurrent jobs
- Consider preview resolution (800x600 is sufficient)

### Frontend Performance
- Three.js can handle models up to ~500K triangles
- STL file size limit: 10MB
- Lazy load 3D viewer (only when rendering)
- Debounce editor changes (don't re-render on every keystroke)

### Backend Performance
- Redis queue prevents backend blocking
- Async FastAPI endpoints (non-blocking I/O)
- File cleanup background task (every 1 hour)

## Monitoring and Logging

### Logs
- **Backend**: Request/response logs, OpenAI API calls, errors
- **Render Service**: OpenSCAD stdout/stderr, job timing
- **Frontend**: Console errors, WebSocket connection status

### Metrics (Future)
- API request count
- Render job success/failure rate
- Average render time
- OpenAI API costs
- Active WebSocket connections

## Development Guidelines

### Code Style
- **Python**: PEP 8, type hints, docstrings
- **TypeScript**: Functional components, explicit types
- **OpenSCAD**: 2-space indent, descriptive variable names

### Testing Strategy
- Unit tests: AI prompt generation logic
- Integration tests: Full render pipeline
- E2E tests: User workflows (Playwright)

### Contribution Policy

**IMPORTANT: No Promotional Content**

This is a professional open-source project. When contributing:

- ✅ DO include proper attribution for libraries and tools
- ✅ DO credit authors in acknowledgments
- ✅ DO use descriptive commit messages
- ❌ DO NOT add promotional text to commits (no "Generated with X")
- ❌ DO NOT add co-author tags for AI assistants
- ❌ DO NOT include advertisements or self-promotion
- ❌ DO NOT add "Built with [Tool Name]" badges unless essential

**Examples:**

Good commit message:
```
feat: Add ISO metric thread generation with threads-scad library
```

Bad commit message:
```
feat: Add threading support

Generated with Claude Code
Co-Authored-By: AI Assistant
```

Good acknowledgment:
```
## Acknowledgments
- OpenSCAD - The foundation
- threads-scad - Threading library
```

Bad acknowledgment:
```
## Built With
- Claude Code - AI Pair Programming
- ChatGPT - Code generation
```

**Rationale**: Keep the project professional and focused on technical merit, not promotional content.

## Deployment Architecture

### Development
```
docker-compose.yml
    ↓
Local Docker containers
    ↓
Hot reload enabled
    ↓
Port 4100 (local access)
```

### Production Options

**Option 1: Single Server (Docker Compose)**
```
VPS/EC2 Instance
    ↓
Docker Compose
    ↓
Caddy/Nginx reverse proxy (HTTPS)
    ↓
Public domain
```

**Option 2: Kubernetes (Scalable)**
```
Kubernetes Cluster
    ├── Frontend Deployment (replicas: 2)
    ├── Backend Deployment (replicas: 3)
    ├── Render Service Deployment (replicas: 5)
    ├── Redis StatefulSet
    └── Ingress (HTTPS)
```

**Option 3: Serverless (Future)**
```
Frontend → CDN (Vercel/Netlify)
Backend → Cloud Functions (AWS Lambda)
Render → Fargate/Cloud Run (containerized)
Queue → Managed Redis
```

## Scaling Strategy

### Horizontal Scaling
- **Backend**: Stateless, scale to 10+ instances
- **Render Service**: CPU-bound, scale based on queue depth
- **Frontend**: CDN distribution

### Vertical Scaling
- **Render Service**: More CPU cores = faster rendering
- **Redis**: More memory = larger queue capacity

### Cost Optimization
- Use spot instances for render service
- Cache AI responses for common prompts
- Implement request deduplication

## Future Enhancements

### Short-term
- [ ] User authentication (JWT)
- [ ] Save/load projects (PostgreSQL)
- [ ] Model gallery/sharing
- [ ] Better error messages

### Long-term
- [ ] Collaborative editing (CRDT)
- [ ] Custom library uploads
- [ ] Real-time multi-user preview
- [ ] Mobile app (React Native)

## References

- [OpenSCAD Documentation](https://openscad.org/documentation.html)
- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [Three.js Documentation](https://threejs.org/docs/)
- [Redis Documentation](https://redis.io/documentation)
