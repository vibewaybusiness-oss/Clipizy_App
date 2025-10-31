# Clipizy

A comprehensive AI-powered music clip generation and content creation platform built with Next.js 14 and FastAPI. Clipizy enables users to create engaging music videos, analyze audio content, and manage multimedia projects through an intuitive web interface.

## 🏗️ Architecture

### Full-Stack Architecture
```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Frontend      │    │   Backend API   │    │   AI Services   │
│   Next.js 14    │◄──►│   FastAPI       │◄──►│   ComfyUI       │
│   React 18      │    │   SQLAlchemy    │    │   RunPod        │
│   TypeScript    │    │   PostgreSQL    │    │   ProducerAI    │
└─────────────────┘    └─────────────────┘    └─────────────────┘
```

### Frontend Structure
```
src/
├── app/                    # Next.js App Router
│   ├── dashboard/         # Protected user dashboard
│   ├── create/            # Content creation workflows
│   ├── projects/          # Project management
│   └── auth/              # Authentication
├── components/            # React components
│   ├── ui/               # shadcn/ui base components
│   ├── forms/            # Form components
│   └── layout/           # Layout components
├── hooks/                # Custom React hooks
│   ├── ai/               # AI integration hooks
│   ├── storage/          # Data persistence hooks
│   └── business/         # Business logic hooks
├── contexts/             # React Context providers
├── lib/                  # API clients and utilities
└── types/                # TypeScript definitions
```

### Backend Structure
```
api/
├── config/               # Configuration management
├── data/                 # Database and storage
├── middleware/           # Request processing
├── models/               # SQLAlchemy models
├── routers/              # API endpoints
├── services/             # Business logic
├── schemas/              # Pydantic validation
└── workflows/            # Process orchestration
```

## 🚀 Quick Start

### Prerequisites
- Node.js 18+ and npm
- Python 3.11+
- PostgreSQL 14+
- Redis (optional, for caching)

### Installation

1. **Clone and setup**
```bash
git clone <repository-url>
cd clipizy
```

2. **Backend setup**
```bash
# Install Python dependencies
pip install -r requirements.txt

# Set up environment variables
cp .env.example .env
# Edit .env with your configuration

# Run database migrations
alembic upgrade head

# Start the backend server
uvicorn api.main:app --reload --host 0.0.0.0 --port 8000
```

3. **Frontend setup**
```bash
# Install Node.js dependencies
npm install

# Start the development server
npm run dev
```

4. **Access the application**
- Frontend: http://localhost:3000
- Backend API: http://localhost:8000
- API Documentation: http://localhost:8000/docs

## 🛠️ Development

### Available Scripts

**Frontend (npm)**
```bash
npm run dev          # Start development server
npm run build        # Build for production
npm run start        # Start production server
npm run lint         # Run ESLint
npm run test         # Run Jest tests
npm run typecheck    # TypeScript type checking
```

**Backend (Python)**
```bash
# Development
uvicorn api.main:app --reload

# Testing
pytest
pytest --cov=api

# Database
alembic revision --autogenerate -m "Description"
alembic upgrade head
```

### Environment Configuration

**Frontend (.env.local)**
```bash
NEXT_PUBLIC_API_URL=http://localhost:8000
NEXT_PUBLIC_STRIPE_PUBLISHABLE_KEY=pk_test_...
NEXTAUTH_SECRET=your-secret-key
NEXTAUTH_URL=http://localhost:3000
```

**Backend (.env)**
```bash
# Copy env.template to .env and fill in your actual values
cp env.template .env

# Required environment variables:
# Database
DATABASE_URL=postgresql://user:pass@localhost:5432/clipizy
DB_POOL_SIZE=10

# Security
SECRET_KEY=your-secret-key
JWT_ALGORITHM=HS256

# AWS S3 Storage (Required)
S3_BUCKET=clipizy-dev
S3_REGION=us-east-1
S3_ENDPOINT_URL=https://s3.amazonaws.com
S3_ACCESS_KEY=your-aws-access-key
S3_SECRET_KEY=your-aws-secret-key
```

# AI Services
COMFYUI_URL=http://localhost:8188
RUNPOD_API_KEY=your-runpod-key
PRODUCER_AI_API_KEY=your-producer-key
```

### AWS S3 Storage Setup

Clipizy uses Amazon S3 as the primary storage solution for all file operations.

**Quick Setup:**
```bash
# Interactive setup (recommended)
./scripts/setup_s3_env.sh

# Or manual setup
cp env.template .env
# Edit .env with your S3 credentials
python3 scripts/test_s3_connection.py
```

**Required Steps:**
1. Create S3 buckets: `clipizy-prod`, `clipizy-dev`, `clipizy-test`
2. Create IAM user with S3 permissions
3. Run setup script or manually configure `.env`
4. Test connection: `python3 scripts/test_s3_connection.py`
5. Restart backend to load credentials

**Troubleshooting:**
- See [S3_TROUBLESHOOTING.md](./scripts/S3_TROUBLESHOOTING.md) for common issues
- See [S3_MIGRATION_SUMMARY.md](./S3_MIGRATION_SUMMARY.md) for complete details
- See [AWS_S3_SETUP.md](./AWS_S3_SETUP.md) for AWS configuration

**Benefits of AWS S3:**
- Scalable cloud storage
- Built-in redundancy and durability
- Integration with AWS ecosystem
- Cost-effective for production workloads
- High availability and performance

## 📊 Core Features

### Music Clip Generation
- **Audio Analysis**: Automatic BPM, key, and genre detection
- **Visual Generation**: AI-powered video creation with ComfyUI
- **Template System**: Pre-built visual templates and effects
- **Export Options**: Multiple formats and quality settings

### Project Management
- **Multi-Project Support**: Music clips, video editing, audio editing
- **Auto-Save**: Real-time project persistence
- **Version Control**: Project history and rollback
- **Collaboration**: Team project sharing

### AI Integration
- **ProducerAI**: Music generation and enhancement
- **ComfyUI**: Advanced video generation workflows
- **RunPod**: GPU-accelerated processing
- **Custom Models**: Extensible AI model integration

### User Management
- **Authentication**: JWT-based with OAuth support
- **Credits System**: Usage-based billing
- **Subscription Plans**: Tiered access levels
- **Admin Panel**: User and system management

## 🔧 API Endpoints

### Core Endpoints
```bash
# Authentication
POST /api/auth/login
POST /api/auth/register
POST /api/auth/refresh

# Projects
GET    /api/projects
POST   /api/projects
GET    /api/projects/{id}
PUT    /api/projects/{id}
DELETE /api/projects/{id}

# Music Analysis
POST /api/music-analysis/analyze
GET  /api/music-analysis/{id}

# Video Generation
POST /api/comfyui/generate
GET  /api/comfyui/status/{job_id}

# File Management
POST /api/storage/upload
GET  /api/storage/{file_id}
```

### Health & Monitoring
```bash
GET /health              # Basic health check
GET /health/detailed     # Detailed system status
GET /metrics             # Application metrics
```

## 🎨 Frontend Components

### Key Components
```typescript
// Audio Controls
import { AudioControls } from '@/components/ui/audio-controls'

// Project Management
import { ProjectCard } from '@/components/projects/project-card'
import { ProjectList } from '@/components/projects/project-list'

// Forms
import { BudgetSlider } from '@/components/forms/budget-slider'
import { StepNavigation } from '@/components/forms/step-navigation'

// Layout
import { Navigation } from '@/components/layout/navigation'
import { ProtectedRoute } from '@/components/layout/protected-route'
```

### Custom Hooks
```typescript
// AI Integration
import { useMusicAnalysis } from '@/hooks/ai/use-music-analysis'
import { useVideoGeneration } from '@/hooks/ai/use-video-generation'

// Project Management
import { useProjectManagement } from '@/hooks/storage/use-project-management'
import { useDataPersistence } from '@/hooks/storage/use-data-persistence'

// Business Logic
import { usePricing } from '@/hooks/business/use-pricing'
import { useCredits } from '@/hooks/business/use-credits'
```

## 🗄️ Database Schema

### Core Models
```python
# User Management
class User(Base):
    id: UUID
    email: str
    credits: int
    subscription_plan: str
    created_at: datetime

# Project Management
class Project(Base):
    id: UUID
    user_id: UUID
    name: str
    project_type: str
    settings: JSON
    created_at: datetime

# Media Files
class MediaFile(Base):
    id: UUID
    project_id: UUID
    filename: str
    file_type: str
    file_size: int
    s3_key: str
```

## 🔒 Security Features

### Authentication & Authorization
- JWT-based authentication with refresh tokens
- Role-based access control (RBAC)
- OAuth integration (Google, GitHub)
- Session management with secure cookies

### Input Validation & Sanitization
- Comprehensive input sanitization middleware
- SQL injection prevention
- XSS protection
- File upload validation

### Security Headers
- CORS configuration
- Security headers middleware
- Rate limiting and abuse protection
- Request monitoring and logging

## 📈 Performance Optimizations

### Frontend
- Code splitting and lazy loading
- Image optimization with Next.js
- Memory management for audio/video
- Efficient state management with Context

### Backend
- Database connection pooling
- Async/await throughout
- Query optimization
- Caching with Redis (optional)

## 🧪 Testing

### Frontend Testing
```bash
# Unit tests
npm run test

# Coverage report
npm run test:coverage

# E2E tests (if configured)
npm run test:e2e
```

### Backend Testing
```bash
# Unit tests
pytest

# Coverage report
pytest --cov=api

# Integration tests
pytest tests/integration/
```

## 🚀 Deployment

### Frontend (Vercel)
```bash
# Build and deploy
npm run build
vercel deploy

# Environment variables in Vercel dashboard
NEXT_PUBLIC_API_URL=https://your-api-domain.com
NEXTAUTH_SECRET=your-production-secret
```

### Backend (Docker)
```dockerfile
FROM python:3.11-slim
COPY api/ /app/api/
WORKDIR /app
RUN pip install -r requirements.txt
CMD ["uvicorn", "api.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

### Database
```bash
# Production migration
alembic upgrade head

# Backup
pg_dump clipizy > backup.sql

# Restore
psql clipizy < backup.sql
```

## 📚 Documentation

- [Frontend Architecture](./src/README.md)
- [Backend API Documentation](./api/README.md)
- [API Services Documentation](./api/services/README.md)
- [Testing Guide](./TESTING_GUIDE.md)
- [Storage Onboarding Guide](./STORAGE_ONBOARDING_GUIDE.md)

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

### Development Guidelines
- Follow TypeScript best practices
- Write comprehensive tests
- Update documentation
- Follow the existing code style
- Use conventional commit messages

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🆘 Support

- Create an issue for bugs or feature requests
- Check existing documentation
- Review the module-specific README files
- Contact the development team

---

**Built with ❤️ for scalable, maintainable, and performant AI-powered content creation.**
