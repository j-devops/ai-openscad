# Contributing to AI-OpenSCAD

Thank you for your interest in contributing! 🎉

## Getting Started

1. Fork the repository
2. Clone your fork: `git clone https://github.com/yourusername/ai-openscad.git`
3. Create a branch: `git checkout -b feature/your-feature-name`
4. Make your changes
5. Test thoroughly
6. Commit: `git commit -m "Add: your feature description"`
7. Push: `git push origin feature/your-feature-name`
8. Open a Pull Request

## Development Setup

See [README.md](README.md) for setup instructions.

## Code Style

### Python (Backend)
- Follow PEP 8
- Use type hints
- Add docstrings to functions
- Run: `black` and `flake8` before committing

### TypeScript (Frontend)
- Follow existing code style
- Use functional components with hooks
- Add type definitions
- Run: `npm run lint` before committing

## Areas for Contribution

### High Priority
- [ ] Additional OpenSCAD libraries integration
- [ ] Better error messages and validation
- [ ] Performance optimizations for rendering
- [ ] Mobile-responsive UI improvements

### Features
- [ ] User authentication system
- [ ] Save/load projects
- [ ] Model gallery/sharing
- [ ] More example prompts
- [ ] Keyboard shortcuts

### Documentation
- [ ] Video tutorials
- [ ] More code examples
- [ ] API documentation
- [ ] Deployment guides (AWS, GCP, Azure)

### Testing
- [ ] Unit tests for AI prompt generation
- [ ] Integration tests for rendering pipeline
- [ ] Frontend component tests
- [ ] E2E tests with Playwright

## Adding OpenSCAD Libraries

To add a new library:

1. Edit `render-service/Dockerfile`:
```dockerfile
RUN cd /usr/share/openscad/libraries && \
    git clone --depth 1 https://github.com/author/library.git library-name && \
    echo "Library installed: library-name"
```

2. Update AI prompt in `backend/app/core/ai_generator.py`:
```python
AVAILABLE LIBRARIES:
...
X. **library-name** - Description (use <library-name/file.scad>)
   - function_name(params) - what it does
   - Example: usage example
```

3. Test thoroughly with examples
4. Update README.md with library info
5. Submit PR with examples

## Improving AI Prompts

The AI code generation quality depends on the system prompt in `backend/app/core/ai_generator.py`.

When improving prompts:
- Add specific examples of correct code patterns
- Include common pitfalls to avoid
- Test with various inputs
- Document what changed and why

## Submitting PRs

- Keep PRs focused on a single feature/fix
- Write clear commit messages
- Update documentation if needed
- Add tests if applicable
- Reference any related issues

## Questions?

Open a [GitHub Discussion](https://github.com/yourusername/ai-openscad/discussions) or issue.
