## CyberSapient DevOps Project

A production-grade DevOps implementation featuring containerized applications, automated CI/CD pipelines, Kubernetes orchestration, and comprehensive monitoring.

## Project Overview

This project demonstrates application deployment with following technologies:

- Containerized Frontend Application (Docker)
- Multi-Environment Deployment(Staging/Develop + Production)
- Infrastructure as Code (Terraform + AWS)
- Automated CI/CD (GitHub Actions)
- Kubernetes Orchestration (AWS EKS)
- Monitoring & Observability (Prometheus + Grafana)


## Architecture Diagram

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   GitHub Repo   │───▶│  GitHub Actions │───▶│   AWS EKS       │
│   (Source Code) │    │   (CI/CD)       │    │   (Kubernetes)  │
└─────────────────┘    └─────────────────┘    └─────────────────┘
                                │                       │
                                ▼                       ▼
                       ┌─────────────────┐    ┌─────────────────┐
                       │   Amazon ECR    │    │  Prometheus     │
                       │   (Container)   │    │  + Grafana      │
                       └─────────────────┘    └─────────────────┘
```

### Prerequisites

- AWS Account with appropriate permissions
- GitHub repository with secrets configured
- Terraform CLI installed
- kubectl and helm CLI tools

### 1. Clone Repository
```bash
git clone <repository-url>
cd CyberSapient_Project
```

### 2. Configure AWS Credentials
```bash
aws configure
# Enter your AWS Access Key ID, Secret Access Key, and Region
```

### 3. Deploy Infrastructure
```bash
cd terraform
terraform init
terraform plan
terraform apply
```

### 4. Deploy Application
The CI/CD pipeline will automatically deploy:
-  Staging : Push to `develop` branch
-  Production : Push to `main` branch (requires approval)

## 📁 Project Structure

```
CyberSapient_Project/
├── frontend/                    # Application code
│   ├── index.html              # Main application
│   └── Dockerfile              # Container definition
│   
├── terraform/                   # Infrastructure as Code
│   ├── main.tf                 # Terraform config
│   ├── eks.tf                  # EKS cluster
│   ├── monitoring.tf           # Prometheus/Grafana
│   ├── iam.tf                  # IAM role and policies
│   ├── namespace.tf            # Namespace creation based on environment
│   ├── networking.tf           # VPC and subnet
│   └── helm/                   # Kubernetes manifests
├── result/                     # Final Deployment Images and Architecture Diagram 
├── .github/workflows/          # CI/CD pipelines
└── ARCHITECTURE.md             # Detailed architecture docs
```



### Workflow Stages

1. Security Scan - Trivy vulnerability scanning
2. STS - STS to targeted AWS Account
3. Build & Test - Docker image build and testing
4. Terraform Plan - Infrastructure changes review
5. Deploy to Staging - Automatic deployment to staging
6. Deploy to Production - Manual approval required


### Environment Strategy

- Staging:  Manual approval on `main` branch
- Production: Auto-deploy on `develop` branch

## 📊 Monitoring & Observability

### Metrics Available
- HTTP request counts and durations
- Application health status
- Container resource usage
- Kubernetes cluster metrics


## 📈 Scaling & Performance

- Horizontal Scaling : Kubernetes HPA
- High Availability : Multi-AZ deployment
- Resource Optimization : Container limits and requests


## Final Deployment 

You can see the final Deploymnet under the forlder result/Final_Page.png
