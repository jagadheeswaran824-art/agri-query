# 🚀 KrishiSahay Deployment Guide

## Deployment Architecture

KrishiSahay supports multiple deployment strategies to accommodate different infrastructure requirements and scale needs.

```
┌─────────────────────────────────────────────────────────────┐
│                    PRODUCTION DEPLOYMENT                     │
├─────────────────────────────────────────────────────────────┤
│  Load Balancer  │  CDN/Cache   │  Monitoring & Logging      │
│  • NGINX/HAProxy│  • CloudFlare │  • Prometheus/Grafana     │
│  • SSL/TLS      │  • Redis Cache│  • ELK Stack              │
│  • Rate Limiting│  • Asset Opt  │  • Health Checks          │
└─────────────────────────────────────────────────────────────┘
                                │
                                ▼
┌─────────────────────────────────────────────────────────────┐
│                    APPLICATION TIER                         │
├─────────────────────────────────────────────────────────────┤
│  Frontend Cluster │  Backend Services │  AI Processing     │
│  • React/Next.js  │  • Express.js API │  • Python Services │
│  • Static Assets  │  • Authentication │  • GPU Instances   │
│  • Service Worker │  • Rate Limiting  │  • Model Serving   │
└─────────────────────────────────────────────────────────────┘
                                │
                                ▼
┌─────────────────────────────────────────────────────────────┐
│                      DATA TIER                              │
├─────────────────────────────────────────────────────────────┤
│  Vector Database  │  Relational DB   │  Object Storage     │
│  • FAISS Indices  │  • PostgreSQL    │  • AWS S3/MinIO    │
│  • Redis Cache    │  • User Data     │  • Model Artifacts │
│  • Elasticsearch  │  • Analytics     │  • Static Assets   │
└─────────────────────────────────────────────────────────────┘
```

## 🐳 Docker Deployment

### Frontend Container
```dockerfile
# Dockerfile.frontend
FROM node:18-alpine AS builder

WORKDIR /app
COPY package*.json ./
RUN npm ci --only=production

COPY . .
RUN npm run build

FROM nginx:alpine
COPY --from=builder /app/public /usr/share/nginx/html
COPY nginx.conf /etc/nginx/nginx.conf

EXPOSE 80
CMD ["nginx", "-g", "daemon off;"]
```

### Backend Container
```dockerfile
# Dockerfile.backend
FROM python:3.9-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Create non-root user
RUN useradd -m -u 1000 krishisahay
USER krishisahay

EXPOSE 8000
CMD ["python", "-m", "uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
```

### Docker Compose Configuration
```yaml
# docker-compose.yml
version: '3.8'

services:
  frontend:
    build:
      context: .
      dockerfile: Dockerfile.frontend
    ports:
      - "80:80"
    depends_on:
      - backend
    environment:
      - API_URL=http://backend:8000
    networks:
      - krishisahay-network

  backend:
    build:
      context: .
      dockerfile: Dockerfile.backend
    ports:
      - "8000:8000"
    depends_on:
      - postgres
      - redis
    environment:
      - DATABASE_URL=postgresql://user:password@postgres:5432/krishisahay
      - REDIS_URL=redis://redis:6379
      - WATSONX_API_KEY=${WATSONX_API_KEY}
      - WATSONX_PROJECT_ID=${WATSONX_PROJECT_ID}
    volumes:
      - ./data:/app/data
      - ./models:/app/models
    networks:
      - krishisahay-network

  postgres:
    image: postgres:14-alpine
    environment:
      - POSTGRES_DB=krishisahay
      - POSTGRES_USER=user
      - POSTGRES_PASSWORD=password
    volumes:
      - postgres_data:/var/lib/postgresql/data
    networks:
      - krishisahay-network

  redis:
    image: redis:7-alpine
    volumes:
      - redis_data:/data
    networks:
      - krishisahay-network

  nginx:
    image: nginx:alpine
    ports:
      - "443:443"
    volumes:
      - ./nginx.conf:/etc/nginx/nginx.conf
      - ./ssl:/etc/nginx/ssl
    depends_on:
      - frontend
    networks:
      - krishisahay-network

volumes:
  postgres_data:
  redis_data:

networks:
  krishisahay-network:
    driver: bridge
```

## ☸️ Kubernetes Deployment

### Namespace Configuration
```yaml
# k8s/namespace.yaml
apiVersion: v1
kind: Namespace
metadata:
  name: krishisahay
  labels:
    name: krishisahay
```

### Frontend Deployment
```yaml
# k8s/frontend-deployment.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: krishisahay-frontend
  namespace: krishisahay
spec:
  replicas: 3
  selector:
    matchLabels:
      app: krishisahay-frontend
  template:
    metadata:
      labels:
        app: krishisahay-frontend
    spec:
      containers:
      - name: frontend
        image: krishisahay/frontend:latest
        ports:
        - containerPort: 80
        resources:
          requests:
            memory: "128Mi"
            cpu: "100m"
          limits:
            memory: "256Mi"
            cpu: "200m"
        livenessProbe:
          httpGet:
            path: /health
            port: 80
          initialDelaySeconds: 30
          periodSeconds: 10
        readinessProbe:
          httpGet:
            path: /ready
            port: 80
          initialDelaySeconds: 5
          periodSeconds: 5

---
apiVersion: v1
kind: Service
metadata:
  name: krishisahay-frontend-service
  namespace: krishisahay
spec:
  selector:
    app: krishisahay-frontend
  ports:
  - protocol: TCP
    port: 80
    targetPort: 80
  type: ClusterIP
```

### Backend Deployment
```yaml
# k8s/backend-deployment.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: krishisahay-backend
  namespace: krishisahay
spec:
  replicas: 2
  selector:
    matchLabels:
      app: krishisahay-backend
  template:
    metadata:
      labels:
        app: krishisahay-backend
    spec:
      containers:
      - name: backend
        image: krishisahay/backend:latest
        ports:
        - containerPort: 8000
        env:
        - name: DATABASE_URL
          valueFrom:
            secretKeyRef:
              name: krishisahay-secrets
              key: database-url
        - name: WATSONX_API_KEY
          valueFrom:
            secretKeyRef:
              name: krishisahay-secrets
              key: watsonx-api-key
        resources:
          requests:
            memory: "512Mi"
            cpu: "500m"
          limits:
            memory: "1Gi"
            cpu: "1000m"
        volumeMounts:
        - name: data-volume
          mountPath: /app/data
        - name: models-volume
          mountPath: /app/models
      volumes:
      - name: data-volume
        persistentVolumeClaim:
          claimName: krishisahay-data-pvc
      - name: models-volume
        persistentVolumeClaim:
          claimName: krishisahay-models-pvc

---
apiVersion: v1
kind: Service
metadata:
  name: krishisahay-backend-service
  namespace: krishisahay
spec:
  selector:
    app: krishisahay-backend
  ports:
  - protocol: TCP
    port: 8000
    targetPort: 8000
  type: ClusterIP
```

### Ingress Configuration
```yaml
# k8s/ingress.yaml
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: krishisahay-ingress
  namespace: krishisahay
  annotations:
    kubernetes.io/ingress.class: nginx
    cert-manager.io/cluster-issuer: letsencrypt-prod
    nginx.ingress.kubernetes.io/rate-limit: "100"
    nginx.ingress.kubernetes.io/rate-limit-window: "1m"
spec:
  tls:
  - hosts:
    - krishisahay.com
    - api.krishisahay.com
    secretName: krishisahay-tls
  rules:
  - host: krishisahay.com
    http:
      paths:
      - path: /
        pathType: Prefix
        backend:
          service:
            name: krishisahay-frontend-service
            port:
              number: 80
  - host: api.krishisahay.com
    http:
      paths:
      - path: /
        pathType: Prefix
        backend:
          service:
            name: krishisahay-backend-service
            port:
              number: 8000
```

## 🌩️ Cloud Deployment

### AWS Deployment
```yaml
# aws/cloudformation-template.yaml
AWSTemplateFormatVersion: '2010-09-09'
Description: 'KrishiSahay Infrastructure'

Parameters:
  Environment:
    Type: String
    Default: production
    AllowedValues: [development, staging, production]

Resources:
  # VPC Configuration
  VPC:
    Type: AWS::EC2::VPC
    Properties:
      CidrBlock: 10.0.0.0/16
      EnableDnsHostnames: true
      EnableDnsSupport: true
      Tags:
        - Key: Name
          Value: !Sub '${Environment}-krishisahay-vpc'

  # ECS Cluster
  ECSCluster:
    Type: AWS::ECS::Cluster
    Properties:
      ClusterName: !Sub '${Environment}-krishisahay-cluster'
      CapacityProviders:
        - FARGATE
        - FARGATE_SPOT

  # Application Load Balancer
  ApplicationLoadBalancer:
    Type: AWS::ElasticLoadBalancingV2::LoadBalancer
    Properties:
      Name: !Sub '${Environment}-krishisahay-alb'
      Scheme: internet-facing
      Type: application
      Subnets:
        - !Ref PublicSubnet1
        - !Ref PublicSubnet2

  # RDS Database
  Database:
    Type: AWS::RDS::DBInstance
    Properties:
      DBInstanceIdentifier: !Sub '${Environment}-krishisahay-db'
      DBInstanceClass: db.t3.micro
      Engine: postgres
      EngineVersion: '14.9'
      AllocatedStorage: 20
      StorageType: gp2
      DBName: krishisahay
      MasterUsername: !Ref DBUsername
      MasterUserPassword: !Ref DBPassword
      VPCSecurityGroups:
        - !Ref DatabaseSecurityGroup

  # ElastiCache Redis
  RedisCluster:
    Type: AWS::ElastiCache::CacheCluster
    Properties:
      CacheNodeType: cache.t3.micro
      Engine: redis
      NumCacheNodes: 1
      VpcSecurityGroupIds:
        - !Ref RedisSecurityGroup

  # S3 Bucket for static assets
  StaticAssetsBucket:
    Type: AWS::S3::Bucket
    Properties:
      BucketName: !Sub '${Environment}-krishisahay-assets'
      PublicAccessBlockConfiguration:
        BlockPublicAcls: false
        BlockPublicPolicy: false
        IgnorePublicAcls: false
        RestrictPublicBuckets: false
```

### Terraform Configuration
```hcl
# terraform/main.tf
terraform {
  required_version = ">= 1.0"
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
  }
}

provider "aws" {
  region = var.aws_region
}

# VPC Module
module "vpc" {
  source = "terraform-aws-modules/vpc/aws"
  
  name = "${var.environment}-krishisahay-vpc"
  cidr = "10.0.0.0/16"
  
  azs             = ["${var.aws_region}a", "${var.aws_region}b"]
  private_subnets = ["10.0.1.0/24", "10.0.2.0/24"]
  public_subnets  = ["10.0.101.0/24", "10.0.102.0/24"]
  
  enable_nat_gateway = true
  enable_vpn_gateway = false
  
  tags = {
    Environment = var.environment
    Project     = "krishisahay"
  }
}

# EKS Cluster
module "eks" {
  source = "terraform-aws-modules/eks/aws"
  
  cluster_name    = "${var.environment}-krishisahay-cluster"
  cluster_version = "1.28"
  
  vpc_id     = module.vpc.vpc_id
  subnet_ids = module.vpc.private_subnets
  
  node_groups = {
    main = {
      desired_capacity = 2
      max_capacity     = 4
      min_capacity     = 1
      
      instance_types = ["t3.medium"]
      
      k8s_labels = {
        Environment = var.environment
        Application = "krishisahay"
      }
    }
  }
}

# RDS Database
resource "aws_db_instance" "main" {
  identifier = "${var.environment}-krishisahay-db"
  
  engine         = "postgres"
  engine_version = "14.9"
  instance_class = "db.t3.micro"
  
  allocated_storage     = 20
  max_allocated_storage = 100
  storage_type          = "gp2"
  storage_encrypted     = true
  
  db_name  = "krishisahay"
  username = var.db_username
  password = var.db_password
  
  vpc_security_group_ids = [aws_security_group.database.id]
  db_subnet_group_name   = aws_db_subnet_group.main.name
  
  backup_retention_period = 7
  backup_window          = "03:00-04:00"
  maintenance_window     = "sun:04:00-sun:05:00"
  
  skip_final_snapshot = var.environment != "production"
  
  tags = {
    Environment = var.environment
    Project     = "krishisahay"
  }
}
```

## 📊 Monitoring & Observability

### Prometheus Configuration
```yaml
# monitoring/prometheus.yml
global:
  scrape_interval: 15s
  evaluation_interval: 15s

rule_files:
  - "krishisahay_rules.yml"

scrape_configs:
  - job_name: 'krishisahay-frontend'
    static_configs:
      - targets: ['frontend:80']
    metrics_path: /metrics
    scrape_interval: 30s

  - job_name: 'krishisahay-backend'
    static_configs:
      - targets: ['backend:8000']
    metrics_path: /metrics
    scrape_interval: 15s

  - job_name: 'krishisahay-ai-services'
    static_configs:
      - targets: ['ai-service:9000']
    metrics_path: /metrics
    scrape_interval: 10s

alerting:
  alertmanagers:
    - static_configs:
        - targets:
          - alertmanager:9093
```

### Grafana Dashboard
```json
{
  "dashboard": {
    "title": "KrishiSahay System Overview",
    "panels": [
      {
        "title": "Query Response Time",
        "type": "graph",
        "targets": [
          {
            "expr": "histogram_quantile(0.95, rate(krishisahay_query_duration_seconds_bucket[5m]))",
            "legendFormat": "95th percentile"
          }
        ]
      },
      {
        "title": "AI Model Performance",
        "type": "graph",
        "targets": [
          {
            "expr": "krishisahay_ai_accuracy_score",
            "legendFormat": "Accuracy Score"
          }
        ]
      },
      {
        "title": "System Resource Usage",
        "type": "graph",
        "targets": [
          {
            "expr": "rate(container_cpu_usage_seconds_total[5m])",
            "legendFormat": "CPU Usage"
          }
        ]
      }
    ]
  }
}
```

## 🔧 Deployment Scripts

### Automated Deployment Script
```bash
#!/bin/bash
# deploy.sh

set -e

ENVIRONMENT=${1:-staging}
VERSION=${2:-latest}

echo "🚀 Deploying KrishiSahay to $ENVIRONMENT environment"

# Build and push Docker images
echo "📦 Building Docker images..."
docker build -t krishisahay/frontend:$VERSION -f Dockerfile.frontend .
docker build -t krishisahay/backend:$VERSION -f Dockerfile.backend .

docker push krishisahay/frontend:$VERSION
docker push krishisahay/backend:$VERSION

# Deploy to Kubernetes
echo "☸️ Deploying to Kubernetes..."
kubectl apply -f k8s/namespace.yaml
kubectl apply -f k8s/secrets.yaml
kubectl apply -f k8s/configmap.yaml

# Update image tags
kubectl set image deployment/krishisahay-frontend frontend=krishisahay/frontend:$VERSION -n krishisahay
kubectl set image deployment/krishisahay-backend backend=krishisahay/backend:$VERSION -n krishisahay

# Wait for rollout
kubectl rollout status deployment/krishisahay-frontend -n krishisahay
kubectl rollout status deployment/krishisahay-backend -n krishisahay

# Run health checks
echo "🏥 Running health checks..."
./scripts/health-check.sh $ENVIRONMENT

echo "✅ Deployment completed successfully!"
```

### Health Check Script
```bash
#!/bin/bash
# scripts/health-check.sh

ENVIRONMENT=${1:-staging}
BASE_URL="https://${ENVIRONMENT}.krishisahay.com"

echo "🏥 Running health checks for $ENVIRONMENT environment"

# Frontend health check
echo "Checking frontend..."
if curl -f "$BASE_URL/health" > /dev/null 2>&1; then
    echo "✅ Frontend is healthy"
else
    echo "❌ Frontend health check failed"
    exit 1
fi

# Backend API health check
echo "Checking backend API..."
if curl -f "$BASE_URL/api/health" > /dev/null 2>&1; then
    echo "✅ Backend API is healthy"
else
    echo "❌ Backend API health check failed"
    exit 1
fi

# AI services health check
echo "Checking AI services..."
if curl -f "$BASE_URL/api/ai/health" > /dev/null 2>&1; then
    echo "✅ AI services are healthy"
else
    echo "❌ AI services health check failed"
    exit 1
fi

echo "🎉 All health checks passed!"
```

This comprehensive deployment guide ensures that KrishiSahay can be deployed reliably across different environments with proper monitoring, scaling, and maintenance capabilities.