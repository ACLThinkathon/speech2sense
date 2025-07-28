# 🐳 Docker Deployment Guide for Speech2Sense

## 📋 Overview

This guide provides comprehensive instructions for deploying Speech2Sense using Docker containers. The containerized deployment offers improved scalability, easier deployment, and consistent environments across different systems.

## 🏗️ Docker Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    Docker Network                           │
├─────────────────┬─────────────────┬─────────────────────────┤
│   Nginx Proxy   │  FastAPI API    │   Streamlit UI          │
│   Port: 80/443  │  Port: 8000     │   Port: 8501            │
│   (Optional)    │  Container      │   Container             │
└─────────────────┴─────────────────┴─────────────────────────┘
                           │
                  ┌────────▼────────┐
                  │ Shared Volumes  │
                  │ • Database      │
                  │ • Logs          │
                  │ • Temp Files    │
                  └─────────────────┘
```

## 🚀 Quick Start with Docker Compose

### Step 1: Prepare Environment
```bash
# Clone repository
git clone <your-repo-url>
cd speech2sense

# Copy environment template
cp .env.template .env

# Edit .env file with your API keys
nano .env  # or use your preferred editor
```

### Step 2: Build and Start Services
```bash
# Build and start all services
docker-compose up --build

# Or run in background
docker-compose up -d --build

# View logs
docker-compose logs -f
```

### Step 3: Access Applications
- **Dashboard**: http://localhost:8501
- **API Documentation**: http://localhost:8000/docs
- **Health Check**: http://localhost:8000/health

### Step 4: Stop Services
```bash
# Stop all services
docker-compose down

# Stop and remove volumes (caution: deletes data)
docker-compose down -v
```

## 🔧 Manual Docker Deployment

### Build Individual Images

#### API Backend
```bash
# Build API container
docker build -t speech2sense-api -f Dockerfile.api .

# Run API container
docker run -d \
  --name speech2sense-api \
  -p 8000:8000 \
  --env-file .env \
  -v $(pwd)/logs:/app/logs \
  -v $(pwd)/speech2sense.db:/app/speech2sense.db \
  speech2sense-api
```

#### UI Frontend
```bash
# Build UI container
docker build -t speech2sense-ui -f Dockerfile.ui .

# Run UI container
docker run -d \
  --name speech2sense-ui \
  -p 8501:8501 \
  --env-file .env \
  --link speech2sense-api:api \
  speech2sense-ui
```

## 🌐 Production Deployment with Nginx

### Enable Production Profile
```bash
# Start with nginx proxy
docker-compose --profile production up -d --build

# This includes:
# - API Backend (port 8000)
# - UI Frontend (port 8501)
# - Nginx Proxy (port 80/443)
# - Redis Cache (port 6379)
```

### SSL Configuration
```bash
# Create SSL directory
mkdir -p ssl

# Add your SSL certificates
cp your-cert.pem ssl/cert.pem
cp your-key.pem ssl/key.pem

# Update nginx.conf to enable HTTPS
# Uncomment the HTTPS server block in nginx.conf
```

## 🔍 Container Management

### Monitor Container Status
```bash
# Check running containers
docker-compose ps

# View container logs
docker-compose logs api
docker-compose logs ui
docker-compose logs nginx

# Follow logs in real-time
docker-compose logs -f api ui
```

### Container Resource Usage
```bash
# View resource usage
docker stats

# Inspect specific container
docker inspect speech2sense-api
docker inspect speech2sense-ui
```

### Execute Commands in Containers
```bash
# Access API container shell
docker-compose exec api bash

# Access UI container shell
docker-compose exec ui bash

# Run database commands
docker-compose exec api python -c "from databaseLib.database import init_db; init_db()"
```

## 🔧 Configuration Management

### Environment Variables

Create `.env` file with required values:
```bash
# Required API Keys
GROQ_API_KEY=your_groq_api_key_here
HF_TOKEN=your_huggingface_token_here

# Optional Configuration
API_DEBUG=false
LOG_LEVEL=INFO
MAX_AUDIO_FILE_SIZE=104857600
```

### Volume Mounts

The Docker setup includes several volume mounts:
- **Database**: Persistent SQLite database
- **Logs**: Application logs for debugging
- **Temp**: Temporary audio processing files
- **SSL**: SSL certificates for HTTPS

```yaml
volumes:
  - ./speech2sense.db:/app/speech2sense.db
  - ./logs:/app/logs
  - ./temp:/app/temp
  - ./ssl:/etc/nginx/ssl:ro
```

## 📊 Performance Optimization

### Resource Limits
Add resource limits to docker-compose.yml:
```yaml
services:
  api:
    deploy:
      resources:
        limits:
          cpus: '2.0'
          memory: 4G
        reservations:
          cpus: '1.0'
          memory: 2G
```

### Scaling Services
```bash
# Scale API containers
docker-compose up -d --scale api=3

# Scale with load balancer
docker-compose up -d --scale api=3 --scale ui=2
```

### Caching with Redis
```bash
# Start with Redis caching
docker-compose --profile production up -d

# Monitor Redis
docker-compose exec redis redis-cli monitor
```

## 🛡️ Security Considerations

### Network Security
```yaml
# Custom network configuration
networks:
  speech2sense-network:
    driver: bridge
    ipam:
      config:
        - subnet: 172.20.0.0/16
```

### Container Security
```bash
# Run containers as non-root user
RUN adduser --disabled-password --gecos '' appuser
USER appuser

# Read-only file system
docker run --read-only -v /tmp:/tmp speech2sense-api
```

### Secrets Management
```bash
# Use Docker secrets instead of environment variables
echo "your_api_key" | docker secret create groq_api_key -

# Reference in docker-compose.yml
secrets:
  - groq_api_key
```

## 🔄 Health Checks and Monitoring

### Built-in Health Checks
```yaml
healthcheck:
  test: ["CMD", "curl", "-f", "http://localhost:8000/health"]
  interval: 30s
  timeout: 10s
  retries: 3
  start_period: 60s
```

### Monitoring Stack
```bash
# Add monitoring services to docker-compose.yml
services:
  prometheus:
    image: prom/prometheus
    ports:
      - "9090:9090"

  grafana:
    image: grafana/grafana
    ports:
      - "3000:3000"
```

### Log Aggregation
```bash
# Centralized logging with ELK stack
services:
  elasticsearch:
    image: docker.elastic.co/elasticsearch/elasticsearch:7.15.0
  
  logstash:
    image: docker.elastic.co/logstash/logstash:7.15.0
  
  kibana:
    image: docker.elastic.co/kibana/kibana:7.15.0
```

## 🔧 Troubleshooting

### Common Issues

#### Container Won't Start
```bash
# Check container logs
docker-compose logs api

# Check container status
docker-compose ps

# Rebuild containers
docker-compose up --build --force-recreate
```

#### Port Already in Use
```bash
# Find process using port
lsof -i :8000  # Linux/macOS
netstat -ano | findstr :8000  # Windows

# Change ports in docker-compose.yml
ports:
  - "8001:8000"  # External:Internal
```

#### Out of Memory
```bash
# Increase Docker memory limits
# Docker Desktop -> Settings -> Resources -> Memory

# Check container memory usage
docker stats speech2sense-api
```

#### File Permission Issues
```bash
# Fix file permissions
sudo chown -R $USER:$USER ./logs ./temp

# Or run with correct user ID
docker-compose run --user $(id -u):$(id -g) api
```

### Debugging Commands

```bash
# Enter container for debugging
docker-compose exec api bash

# Check container environment
docker-compose exec api env

# Test API connectivity
docker-compose exec ui curl http://api:8000/health

# View detailed logs
docker-compose logs --details api
```

## 🚀 Production Deployment Checklist

### Pre-deployment
- [ ] Set production environment variables
- [ ] Configure SSL certificates
- [ ] Set up monitoring and alerting
- [ ] Configure backup strategy
- [ ] Test with production data

### Security
- [ ] Restrict CORS origins
- [ ] Enable rate limiting
- [ ] Use secrets management
- [ ] Set up firewall rules
- [ ] Enable container security scanning

### Performance
- [ ] Set resource limits
- [ ] Configure caching
- [ ] Enable compression
- [ ] Set up load balancing
- [ ] Monitor resource usage

### Monitoring
- [ ] Set up health checks
- [ ] Configure log aggregation
- [ ] Set up metrics collection
- [ ] Create alerting rules
- [ ] Test failover scenarios

## 📋 Maintenance

### Regular Tasks
```bash
# Update containers
docker-compose pull
docker-compose up -d

# Clean up unused images
docker image prune -a

# Backup database
docker-compose exec api cp /app/speech2sense.db /app/backup/

# View disk usage
docker system df
```

### Database Maintenance
```bash
# Backup database
docker-compose exec api sqlite3 /app/speech2sense.db ".backup /app/backup/backup.db"

# Restore database
docker-compose exec api sqlite3 /app/speech2sense.db ".restore /app/backup/backup.db"
```

---

## 🎉 Deployment Complete!

Your Speech2Sense application is now running in Docker containers with production-ready configuration. Monitor the health checks and logs to ensure everything is working correctly.

**Quick Commands:**
- Start: `docker-compose up -d --build`
- Stop: `docker-compose down`
- Logs: `docker-compose logs -f`
- Status: `docker-compose ps`