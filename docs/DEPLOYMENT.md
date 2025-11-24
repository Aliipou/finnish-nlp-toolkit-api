# Deployment Guide

Complete guide for deploying the Finnish NLP Toolkit API to various platforms.

## Table of Contents

1. [Docker Deployment](#docker-deployment)
2. [Railway Deployment](#railway-deployment)
3. [Render Deployment](#render-deployment)
4. [Heroku Deployment](#heroku-deployment)
5. [AWS EC2 Deployment](#aws-ec2-deployment)
6. [Environment Variables](#environment-variables)
7. [Production Checklist](#production-checklist)

---

## Docker Deployment

### Using Docker Compose (Recommended)

1. **Build and start all services:**
   ```bash
   docker-compose up -d --build
   ```

2. **View logs:**
   ```bash
   docker-compose logs -f
   ```

3. **Stop services:**
   ```bash
   docker-compose down
   ```

4. **Access services:**
   - API: http://localhost:8000
   - Frontend: http://localhost:8501

### Manual Docker Build

**Build API:**
```bash
docker build -t finnish-nlp-api .
docker run -p 8000:8000 finnish-nlp-api
```

**Build Frontend:**
```bash
cd frontend
docker build -t finnish-nlp-frontend .
docker run -p 8501:8501 finnish-nlp-frontend
```

---

## Railway Deployment

Railway provides easy deployment with automatic CI/CD.

### Steps:

1. **Create Railway Account**
   - Go to https://railway.app
   - Sign up with GitHub

2. **Create New Project**
   - Click "New Project"
   - Select "Deploy from GitHub repo"
   - Choose your repository

3. **Configure Service**
   - Railway auto-detects the Dockerfile
   - Set environment variables (see below)

4. **Environment Variables**
   ```
   PORT=8000
   PYTHON_VERSION=3.11
   ```

5. **Deploy**
   - Push to main branch
   - Railway automatically builds and deploys

6. **Get URL**
   - Railway provides a public URL
   - Example: `https://finnish-nlp-api.up.railway.app`

### railway.json Configuration

Create `railway.json` in root:
```json
{
  "$schema": "https://railway.app/railway.schema.json",
  "build": {
    "builder": "DOCKERFILE",
    "dockerfilePath": "Dockerfile"
  },
  "deploy": {
    "startCommand": "uvicorn app.main:app --host 0.0.0.0 --port $PORT",
    "restartPolicyType": "ON_FAILURE",
    "restartPolicyMaxRetries": 10
  }
}
```

---

## Render Deployment

Render offers free tier for web services.

### Steps:

1. **Create Render Account**
   - Go to https://render.com
   - Sign up with GitHub

2. **Create Web Service**
   - Dashboard → New → Web Service
   - Connect GitHub repository

3. **Configure Build**
   - **Environment**: Docker
   - **Dockerfile Path**: `./Dockerfile`
   - **Instance Type**: Free or Starter

4. **Environment Variables**
   ```
   PORT=8000
   PYTHON_VERSION=3.11
   ```

5. **Deploy**
   - Click "Create Web Service"
   - Render builds and deploys

6. **Custom Domain (Optional)**
   - Settings → Custom Domain
   - Add your domain

### render.yaml Configuration

Create `render.yaml` in root:
```yaml
services:
  - type: web
    name: finnish-nlp-api
    env: docker
    dockerfilePath: ./Dockerfile
    envVars:
      - key: PORT
        value: 8000
      - key: PYTHON_VERSION
        value: 3.11
    healthCheckPath: /health
```

---

## Heroku Deployment

### Prerequisites:
- Heroku CLI installed
- Heroku account

### Steps:

1. **Login to Heroku**
   ```bash
   heroku login
   ```

2. **Create Heroku App**
   ```bash
   heroku create finnish-nlp-api
   ```

3. **Set Stack to Container**
   ```bash
   heroku stack:set container -a finnish-nlp-api
   ```

4. **Create heroku.yml**
   ```yaml
   build:
     docker:
       web: Dockerfile
   run:
     web: uvicorn app.main:app --host 0.0.0.0 --port $PORT
   ```

5. **Deploy**
   ```bash
   git add .
   git commit -m "Deploy to Heroku"
   git push heroku main
   ```

6. **Open App**
   ```bash
   heroku open
   ```

### Set Environment Variables
```bash
heroku config:set PYTHON_VERSION=3.11
heroku config:set LOG_LEVEL=INFO
```

---

## AWS EC2 Deployment

### Prerequisites:
- AWS account
- EC2 instance (t2.micro or larger)
- SSH access to instance

### Steps:

1. **Connect to EC2**
   ```bash
   ssh -i your-key.pem ubuntu@your-ec2-ip
   ```

2. **Install Docker**
   ```bash
   sudo apt update
   sudo apt install -y docker.io docker-compose
   sudo usermod -aG docker ubuntu
   ```

3. **Clone Repository**
   ```bash
   git clone https://github.com/yourusername/finnish-nlp-toolkit.git
   cd finnish-nlp-toolkit
   ```

4. **Configure Environment**
   ```bash
   cp .env.example .env
   nano .env  # Edit configuration
   ```

5. **Start Services**
   ```bash
   docker-compose up -d
   ```

6. **Configure Nginx (Optional)**
   ```nginx
   server {
       listen 80;
       server_name your-domain.com;

       location / {
           proxy_pass http://localhost:8000;
           proxy_set_header Host $host;
           proxy_set_header X-Real-IP $remote_addr;
       }
   }
   ```

7. **Enable Firewall**
   ```bash
   sudo ufw allow 80/tcp
   sudo ufw allow 443/tcp
   sudo ufw allow 8000/tcp
   sudo ufw enable
   ```

---

## Environment Variables

### Required Variables

```env
# API Configuration
API_HOST=0.0.0.0
API_PORT=8000

# Logging
LOG_LEVEL=INFO
```

### Optional Variables

```env
# CORS
CORS_ORIGINS=https://your-frontend.com,https://another-domain.com

# Database (if using)
DATABASE_URL=postgresql://user:password@host:5432/dbname

# Frontend
FRONTEND_PORT=8501
API_BASE_URL=http://api:8000/api
```

### Setting Variables by Platform

**Docker Compose:**
```yaml
environment:
  - API_PORT=8000
  - LOG_LEVEL=INFO
```

**Railway:**
- Dashboard → Variables → Add Variable

**Render:**
- Dashboard → Environment → Add Environment Variable

**Heroku:**
```bash
heroku config:set VARIABLE_NAME=value
```

---

## Production Checklist

### Security

- [ ] Set specific CORS origins (not `*`)
- [ ] Implement API authentication (API keys, OAuth)
- [ ] Enable HTTPS/SSL
- [ ] Sanitize all user inputs
- [ ] Add rate limiting
- [ ] Use environment variables for secrets
- [ ] Enable security headers

### Performance

- [ ] Enable response caching
- [ ] Implement request throttling
- [ ] Set up load balancing
- [ ] Configure auto-scaling
- [ ] Optimize Docker image size
- [ ] Use CDN for static assets

### Monitoring

- [ ] Set up logging service (CloudWatch, Datadog)
- [ ] Configure error tracking (Sentry)
- [ ] Add performance monitoring
- [ ] Set up health check alerts
- [ ] Monitor resource usage
- [ ] Track API metrics

### Reliability

- [ ] Configure auto-restart on failure
- [ ] Set up database backups
- [ ] Implement graceful shutdown
- [ ] Add circuit breakers
- [ ] Configure retry logic
- [ ] Set up disaster recovery

### Testing

- [ ] Run all unit tests
- [ ] Run integration tests
- [ ] Perform load testing
- [ ] Test in staging environment
- [ ] Verify all endpoints
- [ ] Test error scenarios

---

## SSL/HTTPS Configuration

### Using Let's Encrypt with Nginx

```bash
sudo apt install certbot python3-certbot-nginx
sudo certbot --nginx -d your-domain.com
```

### Using Cloudflare

1. Add domain to Cloudflare
2. Update nameservers
3. Enable "Full" SSL mode
4. Automatic HTTPS

---

## Scaling

### Horizontal Scaling

**Docker Compose:**
```bash
docker-compose up -d --scale api=3
```

**Kubernetes:**
```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: finnish-nlp-api
spec:
  replicas: 3
  ...
```

### Load Balancing

**Nginx:**
```nginx
upstream api_backend {
    server api1:8000;
    server api2:8000;
    server api3:8000;
}

server {
    location / {
        proxy_pass http://api_backend;
    }
}
```

---

## Troubleshooting

### Container Won't Start
```bash
# Check logs
docker-compose logs api

# Check container status
docker ps -a

# Rebuild
docker-compose build --no-cache
```

### Port Already in Use
```bash
# Find process using port
lsof -i :8000

# Kill process
kill -9 PID
```

### Permission Issues
```bash
# Fix file permissions
chmod -R 755 .
chown -R $USER:$USER .
```

---

## Support

For deployment issues:
- Check logs first
- Review error messages
- Consult platform documentation
- Open GitHub issue

---

Deployment guide last updated: 2024
