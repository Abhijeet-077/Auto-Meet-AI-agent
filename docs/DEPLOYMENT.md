# 🚀 Agentic Calendar - Deployment Guide

## Overview

This guide covers deploying Agentic Calendar to production environments, including cloud platforms, containerization, and scaling considerations.

## 🏗️ Deployment Options

### 1. Cloud Platform Deployment

#### Streamlit Cloud (Recommended for Frontend)
```bash
# 1. Push to GitHub repository
git add .
git commit -m "Deploy to Streamlit Cloud"
git push origin main

# 2. Connect repository to Streamlit Cloud
# 3. Configure environment variables in Streamlit Cloud dashboard
# 4. Deploy with one click
```

#### Heroku Deployment
```bash
# 1. Create Procfile
echo "web: streamlit run streamlit_app_modern.py --server.port=\$PORT --server.address=0.0.0.0" > Procfile

# 2. Create runtime.txt
echo "python-3.9.16" > runtime.txt

# 3. Deploy to Heroku
heroku create your-app-name
heroku config:set GOOGLE_CLIENT_ID=your_client_id
heroku config:set GOOGLE_CLIENT_SECRET=your_client_secret
heroku config:set GEMINI_API_KEY=your_api_key
git push heroku main
```

#### Google Cloud Platform
```bash
# 1. Create app.yaml
cat > app.yaml << EOF
runtime: python39
service: default

env_variables:
  GOOGLE_CLIENT_ID: "your_client_id"
  GOOGLE_CLIENT_SECRET: "your_client_secret"
  GEMINI_API_KEY: "your_api_key"

automatic_scaling:
  min_instances: 1
  max_instances: 10
EOF

# 2. Deploy to App Engine
gcloud app deploy
```

### 2. Docker Deployment

#### Create Dockerfile
```dockerfile
FROM python:3.9-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Expose ports
EXPOSE 8000 8501

# Create startup script
RUN echo '#!/bin/bash\n\
cd backend_api && uvicorn main:app --host 0.0.0.0 --port 8000 &\n\
streamlit run streamlit_app_modern.py --server.port 8501 --server.address 0.0.0.0\n\
' > start.sh && chmod +x start.sh

CMD ["./start.sh"]
```

#### Docker Compose Setup
```yaml
version: '3.8'

services:
  agentic-calendar:
    build: .
    ports:
      - "8000:8000"
      - "8501:8501"
    environment:
      - GOOGLE_CLIENT_ID=${GOOGLE_CLIENT_ID}
      - GOOGLE_CLIENT_SECRET=${GOOGLE_CLIENT_SECRET}
      - GEMINI_API_KEY=${GEMINI_API_KEY}
      - ENCRYPTION_KEY=${ENCRYPTION_KEY}
    volumes:
      - ./data:/app/data
    restart: unless-stopped

  nginx:
    image: nginx:alpine
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./nginx.conf:/etc/nginx/nginx.conf
      - ./ssl:/etc/nginx/ssl
    depends_on:
      - agentic-calendar
    restart: unless-stopped
```

### 3. Kubernetes Deployment

#### Deployment YAML
```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: agentic-calendar
spec:
  replicas: 3
  selector:
    matchLabels:
      app: agentic-calendar
  template:
    metadata:
      labels:
        app: agentic-calendar
    spec:
      containers:
      - name: agentic-calendar
        image: your-registry/agentic-calendar:latest
        ports:
        - containerPort: 8000
        - containerPort: 8501
        env:
        - name: GOOGLE_CLIENT_ID
          valueFrom:
            secretKeyRef:
              name: agentic-secrets
              key: google-client-id
        - name: GOOGLE_CLIENT_SECRET
          valueFrom:
            secretKeyRef:
              name: agentic-secrets
              key: google-client-secret
        - name: GEMINI_API_KEY
          valueFrom:
            secretKeyRef:
              name: agentic-secrets
              key: gemini-api-key
---
apiVersion: v1
kind: Service
metadata:
  name: agentic-calendar-service
spec:
  selector:
    app: agentic-calendar
  ports:
  - name: backend
    port: 8000
    targetPort: 8000
  - name: frontend
    port: 8501
    targetPort: 8501
  type: LoadBalancer
```

## 🔧 Production Configuration

### Environment Variables
```env
# Production API Configuration
API_BASE_URL=https://your-domain.com
FRONTEND_URL=https://your-app.streamlit.app

# Google OAuth (Production)
GOOGLE_CLIENT_ID=your_production_client_id
GOOGLE_CLIENT_SECRET=your_production_client_secret
GOOGLE_REDIRECT_URI=https://your-domain.com/api/v1/oauth/callback

# AI Configuration
GEMINI_API_KEY=your_production_api_key

# Security
ENCRYPTION_KEY=your_production_encryption_key
SECRET_KEY=your_production_secret_key

# Database (if using persistent storage)
DATABASE_URL=postgresql://user:pass@host:port/db

# Monitoring
SENTRY_DSN=your_sentry_dsn
LOG_LEVEL=INFO
```

### Security Hardening

#### HTTPS Configuration
```nginx
server {
    listen 443 ssl http2;
    server_name your-domain.com;

    ssl_certificate /etc/nginx/ssl/cert.pem;
    ssl_certificate_key /etc/nginx/ssl/key.pem;
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers ECDHE-RSA-AES256-GCM-SHA512:DHE-RSA-AES256-GCM-SHA512;

    location /api/ {
        proxy_pass http://localhost:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    location / {
        proxy_pass http://localhost:8501;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        
        # WebSocket support for Streamlit
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
    }
}
```

#### Security Headers
```python
# Add to FastAPI main.py
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from fastapi.middleware.httpsredirect import HTTPSRedirectMiddleware

# HTTPS redirect
app.add_middleware(HTTPSRedirectMiddleware)

# Trusted hosts
app.add_middleware(
    TrustedHostMiddleware, 
    allowed_hosts=["your-domain.com", "*.your-domain.com"]
)

# Security headers
@app.middleware("http")
async def add_security_headers(request, call_next):
    response = await call_next(request)
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-Frame-Options"] = "DENY"
    response.headers["X-XSS-Protection"] = "1; mode=block"
    response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"
    return response
```

## 📊 Monitoring & Logging

### Application Monitoring
```python
# Add to requirements.txt
sentry-sdk[fastapi]
prometheus-client

# Configure in main.py
import sentry_sdk
from sentry_sdk.integrations.fastapi import FastApiIntegration

sentry_sdk.init(
    dsn=os.getenv("SENTRY_DSN"),
    integrations=[FastApiIntegration()],
    traces_sample_rate=1.0,
)
```

### Health Checks
```python
# Enhanced health check endpoint
@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "version": "2.0.0",
        "services": {
            "database": check_database_health(),
            "oauth": check_oauth_health(),
            "ai": check_ai_health()
        }
    }
```

### Logging Configuration
```python
import logging
import sys

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler('/var/log/agentic-calendar.log')
    ]
)
```

## 🔄 CI/CD Pipeline

### GitHub Actions
```yaml
name: Deploy to Production

on:
  push:
    branches: [main]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
    - uses: actions/checkout@v3
    - name: Set up Python
      uses: actions/setup-python@v4
      with:
        python-version: '3.9'
    - name: Install dependencies
      run: |
        pip install -r requirements.txt
    - name: Run tests
      run: |
        python -m pytest tests/

  deploy:
    needs: test
    runs-on: ubuntu-latest
    steps:
    - uses: actions/checkout@v3
    - name: Deploy to Streamlit Cloud
      run: |
        # Deployment script here
        echo "Deploying to production..."
```

## 📈 Scaling Considerations

### Horizontal Scaling
- **Load Balancing**: Use nginx or cloud load balancers
- **Multiple Instances**: Deploy multiple app instances
- **Database Scaling**: Implement read replicas for database
- **Caching**: Add Redis for session and data caching

### Performance Optimization
- **CDN**: Use CloudFlare or AWS CloudFront for static assets
- **Database Optimization**: Implement connection pooling
- **Async Operations**: Use async/await for I/O operations
- **Caching Strategy**: Implement multi-level caching

### Resource Requirements
```yaml
# Minimum production requirements
CPU: 2 cores
RAM: 4GB
Storage: 20GB SSD
Network: 1Gbps

# Recommended production setup
CPU: 4 cores
RAM: 8GB
Storage: 50GB SSD
Network: 10Gbps
```

## 🔒 Backup & Recovery

### Data Backup
```bash
# Database backup script
#!/bin/bash
DATE=$(date +%Y%m%d_%H%M%S)
pg_dump $DATABASE_URL > backup_$DATE.sql
aws s3 cp backup_$DATE.sql s3://your-backup-bucket/
```

### Disaster Recovery
- **Multi-region Deployment**: Deploy across multiple regions
- **Automated Backups**: Daily automated backups to cloud storage
- **Recovery Testing**: Regular disaster recovery testing
- **Documentation**: Maintain recovery procedures documentation

## 📋 Deployment Checklist

### Pre-deployment
- [ ] Environment variables configured
- [ ] SSL certificates installed
- [ ] Domain DNS configured
- [ ] OAuth redirect URIs updated
- [ ] API quotas and billing verified
- [ ] Security headers implemented
- [ ] Monitoring and logging configured

### Post-deployment
- [ ] Health checks passing
- [ ] OAuth flow tested
- [ ] AI chat functionality verified
- [ ] Calendar integration working
- [ ] Performance monitoring active
- [ ] Error tracking configured
- [ ] Backup procedures tested

### Maintenance
- [ ] Regular security updates
- [ ] API key rotation schedule
- [ ] Performance monitoring
- [ ] User feedback collection
- [ ] Feature usage analytics
- [ ] Capacity planning reviews

---

**Ready for production?** Follow this guide step-by-step for a successful deployment!
