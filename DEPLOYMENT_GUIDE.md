# Deployment Guide
## Orange Disease Detection System

## Deployment Options

### Option 1: Render.com (Recommended)

#### Advantages:
- Free tier available
- Easy GitHub integration
- Auto-deploy on git push
- Good documentation
- Sufficient for small-medium traffic

#### Steps:

**1. Prepare Repository**
```bash
# Initialize git if not done
git init
git add .
git commit -m "Initial Orange Disease Detection System"

# Create GitHub repository
# Push to GitHub
git remote add origin <your-github-url>
git push -u origin main
```

**2. Create Procfile**
```bash
# In project root, create Procfile
web: gunicorn backend.app:app
```

**3. Create runtime.txt** (Optional)
```bash
echo "python-3.10.12" > runtime.txt
```

**4. Update requirements.txt**
```bash
pip freeze > requirements.txt
# Add production dependencies
echo "gunicorn==21.2.0" >> requirements.txt
```

**5. Create Render Account**
- Visit render.com
- Sign up with GitHub
- Grant access to your repository

**6. Create Web Service**
- Click "New +" → "Web Service"
- Connect GitHub repository
- Configure:
  - **Name**: orange-disease-detection
  - **Runtime**: Python 3
  - **Build Command**: `pip install -r requirements.txt`
  - **Start Command**: `gunicorn backend.app:app`
  - **Environment**: Free (or paid for more power)

**7. Set Environment Variables**
- In Render Dashboard → Settings
- Add environment variables:
```
DATABASE_HOST=your-db-host
DATABASE_USER=your-db-user
DATABASE_PASSWORD=your-db-password
SECRET_KEY=your-secret-key-here
FLASK_ENV=production
```

**8. Configure Database**
- Use MySQL on AWS RDS or similar managed service
- Update connection string with remote host
- Migrate database schema to remote instance

**9. Deploy**
- Click "Create Web Service"
- Render builds and deploys automatically
- Monitor deployment logs
- Access at: https://orange-disease-detection.onrender.com

**10. Post-Deployment**
```bash
# Verify deployment
curl https://orange-disease-detection.onrender.com/api/health

# Monitor logs
# View in Render dashboard

# Test API endpoints
curl https://orange-disease-detection.onrender.com/api/diseases
```

---

### Option 2: Heroku

#### Advantages:
- Widely used
- Good for learning
- Free tier deprecated (paid only)

#### Steps:

**1. Install Heroku CLI**
```bash
# Windows
choco install heroku-cli

# macOS
brew install heroku/brew/heroku

# Linux
curl https://cli-assets.heroku.com/install.sh | sh
```

**2. Create Procfile**
```
web: gunicorn backend.app:app
```

**3. Create Heroku App**
```bash
heroku login
heroku create orange-disease-detection
heroku create  # Auto-generates name if not specified
```

**4. Set Environment Variables**
```bash
heroku config:set DATABASE_HOST=<your-db-host>
heroku config:set DATABASE_USER=<your-db-user>
heroku config:set DATABASE_PASSWORD=<your-db-password>
heroku config:set SECRET_KEY=<your-secret-key>
```

**5. Deploy**
```bash
git push heroku main
# or
git push heroku master
```

**6. Monitor**
```bash
heroku logs --tail
heroku open
```

---

### Option 3: AWS (EC2 + RDS)

#### Advantages:
- Production-grade
- Scalable
- Full control
- AWS free tier eligible

#### Architecture:
```
Internet → Route53 (DNS) → CloudFront (CDN) → ALB (Load Balancer)
                              ↓
                        EC2 Instances (Flask)
                              ↓
                        RDS MySQL Database
                              ↓
                        S3 (Models, Uploads)
```

#### Steps:

**1. Create EC2 Instance**
- Launch Ubuntu 22.04 LTS instance
- t2.micro (free tier) or t2.small (for better performance)
- Security group: Allow HTTP (80), HTTPS (443), SSH (22)

**2. Connect to Instance**
```bash
ssh -i your-key.pem ubuntu@your-instance-ip
```

**3. Setup Instance**
```bash
sudo apt update && sudo apt upgrade -y
sudo apt install python3 python3-pip mysql-client-core-8.0
sudo apt install nginx supervisor
```

**4. Clone and Setup Project**
```bash
cd /home/ubuntu
git clone <your-repository>
cd Orange_Disease_Project
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

**5. Configure Database**
- Create RDS MySQL instance
- Update backend config with RDS endpoint
- Run database initialization

**6. Configure Supervisor**
```bash
sudo nano /etc/supervisor/conf.d/orange.conf
```

Content:
```ini
[program:orange]
directory=/home/ubuntu/Orange_Disease_Project/backend
command=/home/ubuntu/Orange_Disease_Project/venv/bin/gunicorn -w 4 -b 127.0.0.1:5000 app:app
user=ubuntu
autostart=true
autorestart=true
redirect_stderr=true
stdout_logfile=/var/log/orange.log
```

**7. Configure Nginx**
```bash
sudo nano /etc/nginx/sites-available/orange
```

Content:
```nginx
server {
    listen 80;
    server_name your-domain.com;

    location / {
        proxy_pass http://127.0.0.1:5000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }

    location /static {
        alias /home/ubuntu/Orange_Disease_Project/static;
    }
}
```

Enable:
```bash
sudo ln -s /etc/nginx/sites-available/orange /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl restart nginx
```

**8. SSL Certificate (Let's Encrypt)**
```bash
sudo apt install certbot python3-certbot-nginx
sudo certbot --nginx -d your-domain.com
```

**9. Start Services**
```bash
sudo systemctl restart supervisor
sudo systemctl restart nginx
```

---

### Option 4: Docker + Docker Hub

#### Create Dockerfile**
```dockerfile
FROM python:3.10-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

ENV FLASK_APP=backend/app.py
ENV FLASK_ENV=production

EXPOSE 5000

CMD ["gunicorn", "-w", "4", "-b", "0.0.0.0:5000", "backend.app:app"]
```

**Create docker-compose.yml**
```yaml
version: '3.8'

services:
  web:
    build: .
    ports:
      - "5000:5000"
    environment:
      DATABASE_HOST: db
      DATABASE_USER: root
      DATABASE_PASSWORD: password
      SECRET_KEY: your-secret-key
    depends_on:
      - db
    volumes:
      - ./static/uploads:/app/static/uploads

  db:
    image: mysql:8.0
    environment:
      MYSQL_ROOT_PASSWORD: password
      MYSQL_DATABASE: orange_disease_db
    volumes:
      - mysql_data:/var/lib/mysql
    ports:
      - "3306:3306"

volumes:
  mysql_data:
```

**Build and Run**
```bash
docker-compose build
docker-compose up -d
```

---

## Performance Optimization

### 1. Model Optimization
```python
# Quantization (reduces model size by 4x)
import tensorflow as tf

converter = tf.lite.TFLiteConverter.from_saved_model("models/best_model")
converter.optimizations = [tf.lite.Optimize.DEFAULT]
tflite_model = converter.convert()
```

### 2. Caching Layer (Redis)
```python
import redis

cache = redis.Redis(host='localhost', port=6379, db=0)

# In prediction endpoint
cache_key = f"prediction:{image_hash}"
cached_result = cache.get(cache_key)
if cached_result:
    return json.loads(cached_result)
```

### 3. Batch Prediction
```python
# Process multiple images efficiently
predictions = model.predict_on_batch(images_batch)
```

### 4. Load Balancing (Nginx)
```nginx
upstream flask_backend {
    server 127.0.0.1:5000;
    server 127.0.0.1:5001;
    server 127.0.0.1:5002;
    server 127.0.0.1:5003;
}

server {
    listen 80;
    location / {
        proxy_pass http://flask_backend;
    }
}
```

---

## Monitoring and Logging

### 1. Application Logging
```python
import logging

logging.basicConfig(
    filename='app.log',
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)
logger.info("Prediction made for user: " + str(user_id))
```

### 2. Error Tracking (Sentry)
```bash
pip install sentry-sdk

import sentry_sdk
sentry_sdk.init("your-sentry-dsn")
```

### 3. Metrics and Analytics
```python
from prometheus_client import Counter, Histogram

predictions_counter = Counter('predictions_total', 'Total predictions')
prediction_time = Histogram('prediction_duration_seconds', 'Prediction time')

@prediction_time.time()
def predict_disease():
    ...
    predictions_counter.inc()
```

---

## Backup and Disaster Recovery

### 1. Database Backup
```bash
# Daily backup
0 2 * * * mysqldump -u root -p$DB_PASSWORD orange_disease_db > /backups/db_$(date +\%Y\%m\%d).sql

# Upload to S3
aws s3 cp /backups/db_*.sql s3://my-backup-bucket/
```

### 2. Model Backup
```bash
# Version models
s3://models-backup/
├── models/
│   ├── v1.0/best_model.h5
│   ├── v1.1/best_model.h5
│   └── v1.2/best_model.h5
```

### 3. Disaster Recovery Plan
```
RTO (Recovery Time Objective): 1 hour
RPO (Recovery Point Objective): 24 hours

Steps:
1. Restore database from latest backup
2. Deploy latest code from GitHub
3. Verify models are loaded
4. Run smoke tests
5. Notify users
```

---

## Security Hardening

### 1. Environment Secrets
```bash
# Use environment variables, not hardcoded secrets
DATABASE_URL=${DATABASE_URL}
SECRET_KEY=${SECRET_KEY}
API_KEY=${API_KEY}
```

### 2. HTTPS Only
```python
app.config['SESSION_COOKIE_SECURE'] = True
app.config['SESSION_COOKIE_HTTPONLY'] = True
```

### 3. Rate Limiting
```python
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address

limiter = Limiter(
    app=app,
    key_func=get_remote_address,
    default_limits=["200 per day", "50 per hour"]
)

@app.route('/api/predict')
@limiter.limit("10 per minute")
def predict_disease():
    ...
```

### 4. Input Validation
```python
from werkzeug.utils import secure_filename

ALLOWED_EXTENSIONS = {'jpg', 'jpeg', 'png', 'gif'}

if not allowed_file(filename):
    return error("Invalid file type"), 400

filename = secure_filename(filename)
```

---

## Scaling Strategy

### Phase 1: Initial (0-1000 users)
- Single EC2 instance (t2.micro)
- Single MySQL database
- Nginx for web server

### Phase 2: Growth (1000-10000 users)
- 2-3 EC2 instances behind ALB
- RDS MySQL with read replicas
- ElastiCache (Redis) for caching
- CloudFront CDN for static assets

### Phase 3: Scale (10000-100000 users)
- Auto-scaling group (EC2)
- Database sharding by region
- Distributed model serving (TensorFlow Serving)
- Message queue (SQS/RabbitMQ) for async jobs
- Multiple regional deployments

---

## Rollback Strategy

```bash
# In case of deployment issues

# Current Version: v1.2
# Previous Working Version: v1.1

# Rollback command
git checkout v1.1
docker-compose build
docker-compose up -d

# Monitor logs
docker-compose logs -f
```

---

## Cost Estimation (Monthly)

### AWS Option:
```
EC2 (t2.small): $20
RDS MySQL (db.t2.small): $25
S3 Storage: $5
Data Transfer: $10
Route53 DNS: $0.50
---
Total: ~$60/month
```

### Render Option:
```
Web Service (Pay-as-you-go): $10-100 depending on usage
Free tier available for light usage
```

### Heroku Option:
```
Dyno (paid tier): $50/month minimum
```

---

## Deployment Checklist

- [ ] Database configured and initialized
- [ ] Environment variables set
- [ ] Model files uploaded
- [ ] SSL certificate installed
- [ ] Backup system configured
- [ ] Monitoring tools setup
- [ ] Logging configured
- [ ] Rate limiting enabled
- [ ] Security headers set
- [ ] Health check endpoint working
- [ ] Load testing completed
- [ ] Runbooks documented
- [ ] Team trained
- [ ] Monitoring alerts set

---

## Support and Troubleshooting

**For deployment issues:**
1. Check logs: `docker-compose logs -f`
2. Verify environment variables
3. Test database connection
4. Check model files exist
5. Verify port availability
6. Test API endpoints manually

---

**Deployment Complete!** 🚀

Monitor your application and gather user feedback for continuous improvements.
