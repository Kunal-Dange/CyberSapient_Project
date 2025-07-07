# 🚀 CyberSapient DevOps Project

A production-grade DevOps implementation featuring containerized applications, automated CI/CD pipelines, Kubernetes orchestration, and comprehensive monitoring.

## 🎯 Project Overview

This project demonstrates enterprise-level DevOps practices with:

- **Containerized Frontend Application** (Docker + Nginx)
- **Multi-Environment Deployment** (Staging + Production)
- **Infrastructure as Code** (Terraform + AWS)
- **Automated CI/CD** (GitHub Actions)
- **Kubernetes Orchestration** (AWS EKS)
- **Monitoring & Observability** (Prometheus + Grafana)
- **Secrets Management** (AWS Secrets Manager)

## 🏗️ Architecture

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

## 🚀 Quick Start

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
- **Staging**: Push to `develop` branch
- **Production**: Push to `main` branch (requires approval)

## 📁 Project Structure

```
CyberSapient_Project/
├── frontend/                    # Application code
│   ├── index.html              # Main application
│   ├── Dockerfile              # Container definition
│   ├── nginx.conf              # Web server config
│   └── metrics.html            # Prometheus metrics
├── terraform/                   # Infrastructure as Code
│   ├── main.tf                 # Main Terraform config
│   ├── eks.tf                  # EKS cluster
│   ├── monitoring.tf           # Prometheus/Grafana
│   ├── secrets.tf              # Secrets management
│   └── helm/                   # Kubernetes manifests
├── .github/workflows/          # CI/CD pipelines
└── ARCHITECTURE.md             # Detailed architecture docs
```

## 🔄 CI/CD Pipeline

### Workflow Stages

1. **Security Scan** - Trivy vulnerability scanning
2. **Build & Test** - Docker image build and testing
3. **Terraform Plan** - Infrastructure changes review
4. **Deploy to Staging** - Automatic deployment to staging
5. **Deploy to Production** - Manual approval required
6. **Health Checks** - Post-deployment verification

### Environment Strategy

- **Staging**: Auto-deploy on `develop` branch
- **Production**: Manual approval on `main` branch

## 📊 Monitoring & Observability

### Metrics Available
- HTTP request counts and durations
- Application health status
- Container resource usage
- Kubernetes cluster metrics

### Access Monitoring
```bash
# Get Grafana URL
kubectl get svc -n monitoring prometheus-grafana

# Get Prometheus URL
kubectl get svc -n monitoring prometheus-kube-prometheus-prometheus
```

## 🔐 Security Features

- **Container Security**: Trivy vulnerability scanning
- **Infrastructure Security**: IAM roles with least privilege
- **Secrets Management**: AWS Secrets Manager integration
- **Network Security**: VPC with private subnets

## 🛠️ Technology Stack

| Component | Technology |
|-----------|------------|
| **Application** | HTML5, CSS3, JavaScript |
| **Container** | Docker, Nginx |
| **Orchestration** | Kubernetes (AWS EKS) |
| **Infrastructure** | Terraform, AWS |
| **CI/CD** | GitHub Actions |
| **Monitoring** | Prometheus, Grafana |
| **Secrets** | AWS Secrets Manager |

## 📈 Scaling & Performance

- **Horizontal Scaling**: Kubernetes HPA
- **Load Balancing**: AWS Load Balancer
- **High Availability**: Multi-AZ deployment
- **Resource Optimization**: Container limits and requests

## 🆘 Troubleshooting

### Common Issues

1. **Terraform Apply Fails**
   ```bash
   terraform plan -refresh-only
   terraform apply -auto-approve
   ```

2. **Kubernetes Pod Issues**
   ```bash
   kubectl get pods -n <namespace>
   kubectl describe pod <pod-name>
   kubectl logs <pod-name>
   ```

3. **Monitoring Access**
   ```bash
   kubectl port-forward svc/prometheus-grafana 3000:80 -n monitoring
   # Access Grafana at http://localhost:3000
   ```

## 📞 Support

For issues and questions:
1. Check the [ARCHITECTURE.md](ARCHITECTURE.md) for detailed documentation
2. Review GitHub Actions logs for CI/CD issues
3. Check AWS CloudWatch for infrastructure logs

## 🎯 Next Steps

- [ ] Add database integration
- [ ] Implement blue-green deployments
- [ ] Add more comprehensive monitoring
- [ ] Set up alerting rules
- [ ] Implement backup strategies

---

**Built with ❤️ for CyberSapient DevOps Challenge**
