# AutoSRE - Automated Site Reliability Engineering Dashboard

A comprehensive, real-time monitoring and analysis platform for Site Reliability Engineering (SRE) with automated log analysis, system metrics, alerting capabilities, and professional observability stack.

## Project Overview

AutoSRE is a production-ready Site Reliability Engineering (SRE) tool that provides real-time monitoring, intelligent log analysis, and automated insights for web applications. It features a modern dashboard with WebSocket-based real-time updates, automated error detection, statistical analysis, and professional monitoring with Grafana and Prometheus integration.

### What AutoSRE Solves

- **Real-time Monitoring**: Live log analysis with instant error detection
- **Observability**: Complete metrics collection with Prometheus and Grafana
- **Automated Insights**: Intelligent pattern recognition and alerting
- **Production Ready**: Containerized deployment with health checks and security
- **DevOps Integration**: CI/CD pipeline, infrastructure as code, and Kubernetes support

## Key Features

### Core Monitoring

- **Real-time Log Analysis**: Live nginx log parsing with WebSocket updates
- **System Metrics**: CPU, memory, disk, and network monitoring
- **Automated Error Detection**: Intelligent 4xx/5xx error identification
- **Alert System**: Configurable thresholds with real-time notifications

### Professional Observability

- **Prometheus Integration**: Full metrics collection and exposition
- **Grafana Dashboards**: Auto-provisioned professional monitoring dashboards
- **Custom Metrics**: Application-specific metrics and business KPIs
- **Historical Data**: Time-series data for trend analysis

### Production Features

- **Docker Containerization**: Complete containerized deployment
- **Health Checks**: Comprehensive health monitoring for all services
- **Security**: Non-root containers, CORS configuration, security headers
- **Scalability**: Kubernetes manifests and AWS ECS deployment ready

## Architecture

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Frontend      │    │    Backend      │    │     Nginx       │
│   (React)       │◄──►│   (FastAPI)     │◄──►│   (Web Server)  │
│   Port: 3000    │    │   Port: 8000    │    │   Port: 8080    │
│   TypeScript    │    │   WebSocket     │    │   Log Gen.      │
│   Tailwind CSS  │    │   Prometheus    │    │   Traffic       │
└─────────────────┘    └─────────────────┘    └─────────────────┘
         │                       │                       │
         │                       │                       │
         ▼                       ▼                       ▼
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│    Grafana      │    │   Prometheus    │    │   Log Files     │
│   Dashboard     │    │    Metrics      │    │  (access.log)   │
│   Port: 3001    │    │   Endpoint      │    │  (error.log)    │
│   Auto-Prov.    │    │   /metrics      │    │  Real-time      │
└─────────────────┘    └─────────────────┘    └─────────────────┘
```

## Technology Stack

### Backend

- **FastAPI**: Modern Python web framework with async support
- **WebSockets**: Real-time bidirectional communication
- **Prometheus Client**: Metrics collection and exposition
- **psutil**: System metrics collection
- **asyncio**: Asynchronous programming

### Frontend

- **React 19**: Latest React with modern features
- **TypeScript**: Type-safe JavaScript development
- **Tailwind CSS**: Utility-first CSS framework
- **Vite**: Fast build tool and dev server
- **WebSocket API**: Real-time data updates

### Infrastructure

- **Docker**: Containerization for all services
- **Docker Compose**: Multi-service orchestration
- **Nginx**: Web server and reverse proxy
- **Grafana**: Professional monitoring dashboards
- **Prometheus**: Metrics collection and storage

### DevOps & Production

- **GitHub Actions**: CI/CD pipeline with testing and deployment
- **Terraform**: Infrastructure as code for AWS
- **Kubernetes**: Container orchestration manifests
- **AWS ECS**: Cloud deployment configuration

## 📁 Project Structure

```
AutoSRE/
├── 📁 backend/                    # FastAPI backend application
│   ├── 📄 main.py                # Main FastAPI app with WebSocket & Prometheus
│   ├── 📄 requirements.txt       # Python dependencies
│   ├── 📄 Dockerfile             # Backend container configuration
│   └── 📁 app/                   # Legacy app directory
├── 📁 frontend/                   # React frontend application
│   ├── 📁 src/
│   │   ├── 📄 App.tsx            # Main React application
│   │   └── 📁 components/
│   │       └── 📄 Dashboard.tsx  # Real-time dashboard component
│   ├── 📄 package.json           # Node.js dependencies
│   ├── 📄 Dockerfile             # Frontend container configuration
│   └── 📄 nginx.conf             # Frontend nginx configuration
├── 📁 nginx-logs/                 # Nginx server and log generation
│   ├── 📄 Dockerfile             # Nginx container
│   ├── 📄 nginx.conf             # Nginx configuration with logging
│   └── 📁 logs/                  # Access and error logs
├── 📁 grafana/                    # Grafana configuration and dashboards
│   ├── 📁 provisioning/
│   │   ├── 📁 datasources/       # Prometheus datasource config
│   │   └── 📁 dashboards/        # Dashboard provisioning
│   └── 📁 dashboards/            # AutoSRE dashboard JSON
├── 📁 k8s/                        # Kubernetes deployment manifests
│   ├── 📄 backend-deployment.yaml
│   ├── 📄 configmap.yaml
│   └── 📄 namespace.yaml
├── 📁 terraform/                  # Infrastructure as code
│   ├── 📄 main.tf                # AWS ECS infrastructure
│   └── 📄 variables.tf           # Terraform variables
├── 📁 .github/                    # GitHub Actions CI/CD
│   └── 📁 workflows/
│       └── 📄 ci-cd.yml          # Complete CI/CD pipeline
├── 📄 docker-compose.yml          # Multi-service orchestration
├── 📄 Makefile                    # Development workflow automation
├── 📄 traffic_generator.py        # Advanced traffic simulation tool
├── 📄 test_ws.py                  # WebSocket connection test suite
├── 📄 env.example                 # Environment variables template
└── 📄 README.md                   # This comprehensive guide
```

## Quick Start Guide

### Prerequisites

- **Docker & Docker Compose**: Latest version
- **Python 3.11+**: For development and testing tools
- **Node.js 18+**: For frontend development (optional)
- **Git**: For version control

### Step 1: Clone and Setup

```bash
# Clone the repository
git clone <repository-url>
cd AutoSRE

# Verify Docker is running
docker --version
docker-compose --version
```

### Step 2: Start All Services

```bash
# Option 1: Using Makefile (Recommended)
make up

# Option 2: Direct Docker Compose
docker-compose up --build -d

# Verify all services are running
make health
```

### Step 3: Access the Applications

| Service                | URL                   | Description                           |
| ---------------------- | --------------------- | ------------------------------------- |
| **Frontend Dashboard** | http://localhost:3000 | Real-time monitoring dashboard        |
| **Grafana Dashboard**  | http://localhost:3001 | Professional monitoring (admin/admin) |
| **Backend API**        | http://localhost:8000 | FastAPI backend with documentation    |
| **Nginx Server**       | http://localhost:8080 | Web server generating logs            |

### Step 4: Generate Traffic (Optional)

```bash
# Generate realistic traffic for testing
make test-traffic

# Or with custom parameters
python3 traffic_generator.py --duration 60 --concurrent 3 --interval 0.5
```

## Dashboard Features

### Frontend Dashboard (Port 3000)

The main AutoSRE dashboard provides:

- **Real-time Connection Status**: WebSocket connection indicator
- **System Metrics Cards**: CPU, Memory, Disk usage with visual indicators
- **Log Statistics**: Total requests, success rate, error count, status codes
- **Recent Logs**: Latest log entries with intelligent parsing
- **Automated Analysis**: AI-powered insights about log patterns
- **Error Logs**: Filtered 5xx error entries for quick debugging
- **Status Code Distribution**: Visual breakdown of HTTP responses

### Grafana Dashboard (Port 3001)

Professional monitoring dashboard with:

#### System Metrics

- **CPU Usage**: Real-time CPU utilization with alerting thresholds
- **Memory Usage**: Memory consumption monitoring with trends
- **Disk Usage**: Storage utilization tracking
- **Active Connections**: WebSocket connection monitoring

#### Application Metrics

- **HTTP Request Rate**: Requests per second by endpoint
- **HTTP Request Duration**: Response time percentiles (50th, 95th)
- **Application Error Rate**: Error frequency monitoring
- **Total HTTP Requests**: Cumulative request counts by method/endpoint

#### Dashboard Features

- **Auto-refresh**: Updates every 5 seconds
- **Time Range Selection**: Configurable time windows
- **Alert Thresholds**: Visual indicators for critical values
- **Professional Styling**: Dark theme with clear visualizations

## 🔧 Configuration Guide

### Environment Variables

#### Backend Configuration

```bash
# Backend environment variables
LOG_LEVEL=INFO                    # Logging level (DEBUG, INFO, WARNING, ERROR)
UPDATE_INTERVAL=5                 # WebSocket update frequency (seconds)
LOG_FILE_PATH=./nginx-logs/logs/access.log  # Path to nginx access logs
```

#### Frontend Configuration

```bash
# Frontend environment variables
VITE_BACKEND_URL=http://localhost:8000  # Backend API URL
```

#### Grafana Configuration

```bash
# Grafana environment variables
GF_SECURITY_ADMIN_USER=admin      # Admin username
GF_SECURITY_ADMIN_PASSWORD=admin  # Admin password
GF_USERS_ALLOW_SIGN_UP=false     # Disable user registration
```

### Alert Thresholds

Configure alert thresholds in `backend/main.py`:

```python
ALERT_THRESHOLDS = {
    "cpu_usage": 80.0,        # CPU usage percentage
    "memory_usage": 85.0,     # Memory usage percentage
    "disk_usage": 90.0,       # Disk usage percentage
    "error_rate": 10.0        # Error rate percentage
}
```

## API Reference

### Backend API Endpoints

| Endpoint                      | Method    | Description              | Response                                                   |
| ----------------------------- | --------- | ------------------------ | ---------------------------------------------------------- |
| `/health`                     | GET       | Health check             | `{"status": "healthy", "timestamp": "..."}`                |
| `/test`                       | GET       | Test endpoint            | `{"message": "Backend is accessible", "timestamp": "..."}` |
| `/api/metrics`                | GET       | System metrics           | CPU, memory, disk, network metrics                         |
| `/metrics`                    | GET       | Prometheus metrics       | Prometheus-formatted metrics                               |
| `/metrics/api/v1/query`       | GET       | Prometheus instant query | Prometheus query response                                  |
| `/metrics/api/v1/query_range` | GET       | Prometheus range query   | Prometheus range response                                  |
| `/get_logs/`                  | GET       | Raw nginx logs           | `{"logs": "..."}`                                          |
| `/get_error_logs/`            | GET       | Error logs only          | `{"error_logs": "..."}`                                    |
| `/analyze_logs/`              | GET       | Log analysis             | Statistical analysis of logs                               |
| `/summarize_logs/`            | GET       | Log summary              | Human-readable log summary                                 |
| `/ws`                         | WebSocket | Real-time updates        | JSON messages with live data                               |

### Prometheus Metrics

The backend exposes the following Prometheus metrics:

- `http_requests_total`: Total HTTP requests by method, endpoint, status
- `http_request_duration_seconds`: Request duration histogram
- `websocket_active_connections`: Active WebSocket connections
- `application_errors_total`: Total application errors
- `system_cpu_usage_percent`: CPU usage percentage
- `system_memory_usage_percent`: Memory usage percentage
- `system_disk_usage_percent`: Disk usage percentage

### WebSocket Messages

#### Initial Data Message

```json
{
  "type": "initial_data",
  "logs": "...",
  "analysis": {
    "total_requests": 100,
    "status_code_distribution": { "200": 95, "404": 5 },
    "error_count": 5,
    "success_rate": 95.0
  },
  "error_logs": ["..."],
  "summary": "Log Analysis Summary...",
  "timestamp": "2024-01-01T12:00:00Z"
}
```

#### Update Message

```json
{
  "type": "update",
  "analysis": {
    "total_requests": 105,
    "status_code_distribution": { "200": 100, "404": 5 },
    "error_count": 5,
    "success_rate": 95.2
  },
  "summary": "Updated Log Analysis Summary...",
  "timestamp": "2024-01-01T12:00:05Z"
}
```

## Real-time Features

### WebSocket Connection

- **Automatic Connection**: Connects on page load
- **Update Frequency**: Every 5 seconds
- **Reconnection Logic**: Automatic retry with exponential backoff
- **Connection Status**: Visual indicator in the dashboard

### Data Flow

1. **Initial Load**: Full data sent immediately upon connection
2. **Periodic Updates**: Incremental analysis updates every 5 seconds
3. **Error Handling**: Graceful handling of connection issues
4. **Data Types**: Logs, analysis, metrics, and alerts

## 🛠️ Development Guide

### Using Makefile (Recommended)

The project includes a comprehensive Makefile for easy development:

```bash
# Show all available commands
make help

# Development commands
make up              # Start all services
make down            # Stop all services
make logs            # View all logs
make health          # Check service health
make test            # Run all tests
make test-ws         # Test WebSocket connection
make test-traffic    # Generate test traffic

# Development workflow
make rebuild         # Rebuild and restart all services
make rebuild-backend # Rebuild backend only
make rebuild-frontend # Rebuild frontend only
make restart         # Restart all services
make restart-backend # Restart backend only
make restart-frontend # Restart frontend only

# Debugging
make logs-backend    # View backend logs
make logs-frontend   # View frontend logs
make logs-nginx      # View nginx logs
make shell-backend   # Open shell in backend container
make shell-frontend  # Open shell in frontend container

# Code quality
make format          # Format Python code with black
make lint            # Lint Python code with flake8
make install-deps    # Install development dependencies
```

### Local Development

#### Backend Development

```bash
# Stop Docker backend
docker-compose stop backend

# Install dependencies
cd backend
pip install -r requirements.txt

# Run backend locally with hot reload
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

#### Frontend Development

```bash
# Stop Docker frontend
docker-compose stop frontend

# Install dependencies
cd frontend
npm install

# Run frontend locally with hot reload
npm run dev
```

#### Hybrid Development (Recommended)

```bash
# Start only backend services in Docker
docker-compose up nginx

# Run frontend locally for development
cd frontend
npm run dev
```

### Testing

#### WebSocket Testing

```bash
# Test WebSocket connection
make test-ws

# Or directly
python3 test_ws.py
```

#### Traffic Generation Testing

```bash
# Generate test traffic
make test-traffic

# Custom traffic generation
python3 traffic_generator.py --duration 30 --concurrent 2 --interval 0.5
```

#### API Testing

```bash
# Test backend health
curl http://localhost:8000/health

# Test log analysis
curl http://localhost:8000/analyze_logs/

# Test Prometheus metrics
curl http://localhost:8000/metrics
```

#### Nginx Testing

```bash
# Test nginx endpoints
curl http://localhost:8080/
curl http://localhost:8080/health
curl http://localhost:8080/error
curl http://localhost:8080/notfound
```

## Comprehensive Testing Suite

AutoSRE includes a comprehensive testing suite with **21 tests** covering all major functionality, achieving **74% code coverage** and ensuring production reliability.

### Test Structure

```
backend/
├── test_main.py              # Main test suite (21 tests)
├── test_integration.py       # Integration tests
├── pytest.ini               # Pytest configuration
└── requirements.txt          # Test dependencies
```

### Test Categories

#### 1. **Connection Management Tests** (3 tests)

- ✅ Connection manager initialization
- ✅ Connect and disconnect functionality
- ✅ Broadcast messaging with multiple clients

#### 2. **Alert Management Tests** (4 tests)

- ✅ Alert manager initialization
- ✅ CPU alert triggering (threshold: 80%)
- ✅ Memory alert triggering (threshold: 85%)
- ✅ Error rate alert triggering (threshold: 10%)
- ✅ Alert clearing functionality

#### 3. **Log Analysis Tests** (3 tests)

- ✅ Parse logs function (5xx error detection)
- ✅ Simple log analysis (human-readable summary)
- ✅ Comprehensive log analysis (statistical data)

#### 4. **API Endpoint Tests** (10 tests)

- ✅ Health check endpoint (`/health`)
- ✅ Test endpoint (`/test`)
- ✅ System metrics endpoint (`/api/metrics`) with mocked psutil
- ✅ Prometheus metrics endpoint (`/metrics`)
- ✅ Prometheus query endpoint (`/metrics/api/v1/query`)
- ✅ Prometheus query range endpoint (`/metrics/api/v1/query_range`)
- ✅ Get logs endpoint (`/get_logs/`) with mocked file operations
- ✅ Get error logs endpoint (`/get_error_logs/`) with mocked file operations
- ✅ Summarize logs endpoint (`/summarize_logs/`)
- ✅ Analyze logs endpoint (`/analyze_logs/`)

#### 5. **Prometheus Metrics Tests** (1 test)

- ✅ Metrics registration verification

### Running Tests

#### Complete Test Suite

```bash
# Run all tests with coverage
docker-compose exec backend python -m pytest test_main.py -v --cov=main --cov-report=term-missing

# Run tests in background container
docker-compose exec backend python -m pytest test_main.py -v

# Run specific test categories
docker-compose exec backend python -m pytest test_main.py::TestAPIEndpoints -v
docker-compose exec backend python -m pytest test_main.py::TestAlertManager -v
docker-compose exec backend python -m pytest test_main.py::TestLogAnalysis -v
```

#### Individual Test Classes

```bash
# Test connection management
docker-compose exec backend python -m pytest test_main.py::TestConnectionManager -v

# Test alert system
docker-compose exec backend python -m pytest test_main.py::TestAlertManager -v

# Test log analysis
docker-compose exec backend python -m pytest test_main.py::TestLogAnalysis -v

# Test API endpoints
docker-compose exec backend python -m pytest test_main.py::TestAPIEndpoints -v

# Test Prometheus metrics
docker-compose exec backend python -m pytest test_main.py::TestPrometheusMetrics -v
```

#### Specific Test Methods

```bash
# Test specific functionality
docker-compose exec backend python -m pytest test_main.py::TestAPIEndpoints::test_health_check -v
docker-compose exec backend python -m pytest test_main.py::TestAlertManager::test_cpu_alert_triggering -v
docker-compose exec backend python -m pytest test_main.py::TestLogAnalysis::test_analyze_logs_comprehensive -v
```

### Test Coverage

The test suite provides comprehensive coverage:

- **74% Code Coverage**: Covers all critical business logic
- **21 Test Cases**: Thorough testing of all major components
- **Mocked Dependencies**: Proper isolation of external dependencies
- **Async Testing**: Full async/await support for WebSocket and async functions
- **Error Handling**: Tests for both success and error scenarios

#### Coverage Report

```bash
# Generate detailed coverage report
docker-compose exec backend python -m pytest test_main.py --cov=main --cov-report=html

# View coverage in browser (if running locally)
open backend/htmlcov/index.html
```

### Test Dependencies

```python
# Test dependencies in requirements.txt
pytest==7.4.3
pytest-asyncio==0.21.1
pytest-mock==3.12.0
pytest-cov==4.1.0
```

### Testing Best Practices

#### 1. **Mocking Strategy**

- **File Operations**: Mock `open()` and `os.path.exists()` for file-based tests
- **System Metrics**: Mock `psutil` functions for system metrics tests
- **WebSocket**: Use `TestClient` for WebSocket endpoint testing
- **External Services**: Mock any external API calls

#### 2. **Test Data**

```python
# Sample test data for log analysis
log_data = """192.168.1.1 - - [28/Jun/2025:10:00:00 +0000] "GET / HTTP/1.1" 200 1234 "-" "Mozilla/5.0"
192.168.1.2 - - [28/Jun/2025:10:00:01 +0000] "POST /api/data HTTP/1.1" 201 567 "-" "curl/7.68.0"
192.168.1.3 - - [28/Jun/2025:10:00:02 +0000] "GET /notfound HTTP/1.1" 404 123 "-" "Mozilla/5.0"
192.168.1.4 - - [28/Jun/2025:10:00:03 +0000] "GET /error HTTP/1.1" 500 123 "-" "Mozilla/5.0"
"""
```

#### 3. **Async Testing**

```python
@pytest.mark.asyncio
async def test_async_function():
    # Test async functions properly
    result = await async_function()
    assert result == expected_value
```

#### 4. **Integration Testing**

```bash
# Test complete workflows
docker-compose exec backend python -m pytest test_integration.py -v
```

### CI/CD Integration

Tests are automatically run in the GitHub Actions CI/CD pipeline:

```yaml
# .github/workflows/ci-cd.yml
- name: Run Backend Tests
  run: |
    docker-compose exec -T backend python -m pytest test_main.py -v --cov=main --cov-report=xml
```

### Test Maintenance

#### Adding New Tests

1. **Follow Naming Convention**: `test_<functionality>_<scenario>`
2. **Use Descriptive Names**: Clear test method names
3. **Mock Dependencies**: Properly mock external dependencies
4. **Test Edge Cases**: Include error scenarios and boundary conditions
5. **Update Coverage**: Ensure new code is covered by tests

#### Test Organization

```python
class TestNewFeature:
    def test_new_feature_basic_functionality(self):
        # Test basic functionality
        pass

    def test_new_feature_error_handling(self):
        # Test error scenarios
        pass

    def test_new_feature_edge_cases(self):
        # Test boundary conditions
        pass
```

### Performance Testing

#### Load Testing

```bash
# Generate load for testing
make test-traffic

# Custom load testing
python3 traffic_generator.py --duration 300 --concurrent 10 --interval 0.1
```

#### WebSocket Load Testing

```bash
# Test WebSocket under load
python3 test_ws.py --concurrent 50 --duration 60
```

### Test Results Interpretation

#### Passing Tests

- ✅ All functionality working as expected
- ✅ No regressions introduced
- ✅ Code coverage maintained

#### Failing Tests

- 🔍 Check test output for specific failure details
- 🔧 Verify test data and mocking setup
- 🐛 Debug actual functionality issues
- 📝 Update tests if requirements changed

### Testing Workflow

```bash
# Development workflow
make test              # Run all tests
make test-backend      # Run backend tests only
make test-coverage     # Run tests with coverage report
make test-watch        # Run tests in watch mode (if available)

# Before committing
make test              # Ensure all tests pass
make lint              # Check code quality
make format            # Format code
```

## Production Deployment

### Docker Compose Production

```bash
# Production deployment
docker-compose -f docker-compose.yml up -d

# With custom environment
export LOG_LEVEL=WARNING
export UPDATE_INTERVAL=10
docker-compose up -d
```

### Kubernetes Deployment

```bash
# Apply Kubernetes manifests
kubectl apply -f k8s/namespace.yaml
kubectl apply -f k8s/configmap.yaml
kubectl apply -f k8s/backend-deployment.yaml

# Check deployment status
kubectl get pods -n autosre
kubectl get services -n autosre
```

### AWS ECS Deployment

```bash
# Initialize Terraform
cd terraform
terraform init
terraform plan
terraform apply

# Deploy to ECS
aws ecs update-service \
  --cluster autosre-production \
  --service autosre-backend \
  --force-new-deployment
```

### CI/CD Pipeline

The project includes a complete GitHub Actions CI/CD pipeline:

1. **Testing**: Automated testing with coverage reporting
2. **Security Scanning**: Trivy vulnerability scanning
3. **Building**: Multi-platform Docker image building
4. **Deployment**: Automated deployment to staging and production

## 🔧 Troubleshooting Guide

### Common Issues and Solutions

#### 1. Port Already in Use

```bash
# Check what's using the ports
lsof -i :8000
lsof -i :3000
lsof -i :3001
lsof -i :8080

# Stop conflicting services
docker-compose down
docker system prune -f
```

#### 2. WebSocket Connection Issues

```bash
# Check backend logs
docker-compose logs backend

# Test WebSocket manually
python3 test_ws.py

# Check frontend logs
docker-compose logs frontend
```

#### 3. Grafana Dashboard Not Loading

```bash
# Check Grafana logs
docker-compose logs grafana

# Verify datasource connection
curl http://localhost:8000/metrics

# Check Prometheus endpoint
curl http://localhost:8000/metrics/api/v1/query?query=system_cpu_usage_percent
```

#### 4. No Data in Grafana

1. Verify Prometheus datasource is configured correctly
2. Check that backend metrics endpoint is accessible
3. Ensure time range is set appropriately
4. Verify metrics are being generated

#### 5. Frontend Build Errors

```bash
# Clean and rebuild
docker-compose down
docker system prune -f
docker-compose up --build

# Check frontend container logs
docker-compose logs frontend
```

#### 6. Backend Metrics Issues

```bash
# Check if metrics endpoint is working
curl http://localhost:8000/metrics

# Check Prometheus query endpoints
curl "http://localhost:8000/metrics/api/v1/query?query=system_cpu_usage_percent"

# Restart backend if needed
docker-compose restart backend
```

### Health Checks

All services include comprehensive health checks:

```bash
# Check all services
docker-compose ps

# Check specific service health
docker-compose exec backend curl -f http://localhost:8000/health
docker-compose exec frontend curl -f http://localhost:3000
docker-compose exec grafana curl -f http://localhost:3000/api/health
docker-compose exec nginx curl -f http://localhost:80/health
```

### Log Analysis

```bash
# View all logs
docker-compose logs

# View specific service logs
docker-compose logs backend
docker-compose logs frontend
docker-compose logs grafana
docker-compose logs nginx

# Follow logs in real-time
docker-compose logs -f backend

# Check nginx log files
tail -f nginx-logs/logs/access.log
tail -f nginx-logs/logs/error.log
```

### Performance Monitoring

```bash
# Check container resource usage
docker stats

# Check system resources
docker-compose exec backend python -c "import psutil; print(f'CPU: {psutil.cpu_percent()}%, Memory: {psutil.virtual_memory().percent}%')"

# Monitor WebSocket connections
curl http://localhost:8000/metrics | grep websocket_active_connections
```

## 🔒 Security Considerations

### Production Security Checklist

- [ ] **HTTPS/TLS**: Enable SSL certificates for all endpoints
- [ ] **Environment Variables**: Use secure environment variable management
- [ ] **Network Policies**: Implement Kubernetes network policies
- [ ] **RBAC**: Configure role-based access control
- [ ] **Secrets Management**: Use Kubernetes secrets or AWS Secrets Manager
- [ ] **Container Security**: Regular security scanning of container images
- [ ] **Log Rotation**: Implement log rotation for nginx logs
- [ ] **Rate Limiting**: Add rate limiting to API endpoints
- [ ] **Authentication**: Implement proper authentication for Grafana
- [ ] **Backup Strategy**: Regular backups of logs and metrics data

### Security Features Already Implemented

- **Non-root Containers**: All containers run as non-root users
- **Security Headers**: Nginx configured with security headers
- **CORS Configuration**: Proper CORS setup for cross-origin requests
- **Health Checks**: Comprehensive health monitoring
- **Resource Limits**: Container resource limits and requests
- **Security Scanning**: Automated vulnerability scanning in CI/CD

## 📈 Monitoring and Alerting

### Alert Configuration

Configure alerts in `backend/main.py`:

```python
ALERT_THRESHOLDS = {
    "cpu_usage": 80.0,        # Alert when CPU > 80%
    "memory_usage": 85.0,     # Alert when memory > 85%
    "disk_usage": 90.0,       # Alert when disk > 90%
    "error_rate": 10.0        # Alert when error rate > 10%
}
```

### Grafana Alerting

1. **Dashboard Alerts**: Configure alerts directly in Grafana dashboards
2. **Prometheus Alerts**: Set up Prometheus alerting rules
3. **Notification Channels**: Configure email, Slack, or PagerDuty notifications

### Metrics to Monitor

#### System Metrics

- CPU usage percentage
- Memory usage percentage
- Disk usage percentage
- Network I/O

#### Application Metrics

- HTTP request rate
- HTTP request duration
- Error rate
- WebSocket connection count

#### Business Metrics

- Total requests processed
- Success rate
- Response time percentiles
- Error distribution by type

## 🤝 Contributing

### Development Workflow

1. **Fork the repository**
2. **Create a feature branch**
   ```bash
   git checkout -b feature/your-feature-name
   ```
3. **Make your changes**
4. **Test thoroughly**
   ```bash
   make test
   make test-ws
   make test-traffic
   ```
5. **Submit a pull request**

### Code Quality Standards

- **Python**: Use Black for formatting, flake8 for linting
- **TypeScript**: Use ESLint and TypeScript strict mode
- **Testing**: Maintain test coverage above 80%
- **Documentation**: Update README and add inline comments
- **Security**: Follow security best practices

### Testing Guidelines

- **Unit Tests**: Test individual functions and components
- **Integration Tests**: Test API endpoints and WebSocket connections
- **End-to-End Tests**: Test complete user workflows
- **Performance Tests**: Test under load with traffic generator

## 📄 License

This project is open source and available under the MIT License.

## 🆘 Support and Community

### Getting Help

1. **Check the troubleshooting section** in this README
2. **Review the logs** using the provided commands
3. **Test individual components** using the test scripts
4. **Create an issue** with detailed information

### Issue Reporting

When reporting issues, please include:

- **Environment**: OS, Docker version, Python/Node.js versions
- **Steps to reproduce**: Detailed steps to reproduce the issue
- **Expected behavior**: What you expected to happen
- **Actual behavior**: What actually happened
- **Logs**: Relevant log output
- **Screenshots**: If applicable

### Feature Requests

We welcome feature requests! Please:

1. Check if the feature is already planned
2. Describe the use case and benefits
3. Provide implementation suggestions if possible
4. Consider contributing the feature yourself

## Roadmap

### Planned Features

- [ ] **Database Integration**: Persistent storage for logs and metrics
- [ ] **Advanced Analytics**: Machine learning for anomaly detection
- [ ] **Multi-tenancy**: Support for multiple applications
- [ ] **Mobile App**: React Native mobile dashboard
- [ ] **Advanced Alerting**: More sophisticated alert rules and notifications
- [ ] **API Documentation**: Interactive API documentation with Swagger
- [ ] **Performance Optimization**: Caching and query optimization
- [ ] **Backup and Recovery**: Automated backup and disaster recovery

### Performance Improvements

- [ ] **Caching Layer**: Redis integration for improved performance
- [ ] **Database Optimization**: Indexing and query optimization
- [ ] **Load Balancing**: Multiple backend instances with load balancing
- [ ] **CDN Integration**: Content delivery network for static assets

---

**AutoSRE** - Making Site Reliability Engineering accessible and automated!

_Built with ❤️ using modern technologies for production-ready monitoring and observability._

## 🔗 External Application Integration

AutoSRE is designed as a **universal monitoring platform** that can connect to any application. This section explains how to integrate your unfinished or existing applications with AutoSRE for comprehensive monitoring and observability.

### Integration Approaches

#### **1. Direct Log File Integration (Easiest)**

Your application writes logs to files that AutoSRE reads:

```bash
# Your app writes logs to a shared volume
your-app/
├── logs/
│   ├── access.log    # HTTP access logs
│   └── error.log     # Error logs
└── docker-compose.yml

# AutoSRE reads from the same volume
autosre/
├── docker-compose.yml
└── nginx-logs/logs/  # Points to your app's logs
```

**Setup:**

```yaml
# Your app's docker-compose.yml
version: '3.8'
services:
  your-app:
    build: .
    volumes:
      - ./logs:/app/logs  # Mount logs directory
    environment:
      - LOG_FILE_PATH=/app/logs/access.log
      - ERROR_LOG_FILE_PATH=/app/logs/error.log

# AutoSRE's docker-compose.yml (modified)
services:
  backend:
    volumes:
      - ../your-app/logs:/app/nginx-logs/logs  # Point to your app's logs
    environment:
      - LOG_FILE_PATH=/app/nginx-logs/logs/access.log
      - ERROR_LOG_FILE_PATH=/app/nginx-logs/logs/error.log
```

#### **2. HTTP API Integration (Recommended)**

Your application sends metrics directly to AutoSRE's API using the provided client library.

### AutoSRE Client Library

AutoSRE provides a Python client library for easy integration:

#### **Installation**

```bash
# Copy the client library to your project
cp autosre_client.py /path/to/your/app/

# Install dependencies
pip install requests
```

#### **Basic Usage**

```python
from autosre_client import AutoSREClient

# Initialize client
autosre = AutoSREClient("http://localhost:8000", "my-app")

# Send metrics
autosre.send_metrics({
    "endpoint": "/api/users",
    "response_time": 150,
    "status_code": 200,
    "user_count": 1000
})

# Send logs
autosre.send_logs([
    "User login successful",
    "Database query completed"
])
```

#### **Advanced Usage**

```python
# Send HTTP request metrics
autosre.send_request_metric(
    endpoint="/api/users",
    method="POST",
    response_time=150,
    status_code=201,
    user_id="user123"
)

# Send error logs
autosre.send_error_log(
    error_message="Database connection timeout",
    error_type="ERROR",
    stack_trace="Traceback (most recent call last):\n  File...",
    database="postgresql",
    timeout=30
)

# Get application metrics
metrics = autosre.get_application_metrics()
print(f"Current metrics: {metrics}")

# List connected applications
apps = autosre.list_applications()
print(f"Connected apps: {apps}")
```

### Integration Examples

#### **FastAPI Middleware Integration**

```python
from fastapi import FastAPI, Request
import time
from autosre_client import AutoSREClient

app = FastAPI()
autosre = AutoSREClient("http://localhost:8000", "my-fastapi-app")

@app.middleware("http")
async def autosre_middleware(request: Request, call_next):
    start_time = time.time()

    # Process request
    response = await call_next(request)

    # Send metrics to AutoSRE
    response_time = int((time.time() - start_time) * 1000)
    autosre.send_request_metric(
        endpoint=str(request.url.path),
        method=request.method,
        response_time=response_time,
        status_code=response.status_code
    )

    return response

@app.get("/api/users")
async def get_users():
    # Your API logic here
    return {"users": ["user1", "user2"]}
```

#### **Flask Integration**

```python
from flask import Flask, request, g
import time
from autosre_client import AutoSREClient

app = Flask(__name__)
autosre = AutoSREClient("http://localhost:8000", "my-flask-app")

@app.before_request
def before_request():
    g.start_time = time.time()

@app.after_request
def after_request(response):
    if hasattr(g, 'start_time'):
        response_time = int((time.time() - g.start_time) * 1000)
        autosre.send_request_metric(
            endpoint=request.path,
            method=request.method,
            response_time=response_time,
            status_code=response.status_code
        )
    return response

@app.route('/api/users')
def get_users():
    return {"users": ["user1", "user2"]}
```

#### **Django Integration**

```python
# middleware.py
import time
from autosre_client import AutoSREClient

class AutoSREMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response
        self.autosre = AutoSREClient("http://localhost:8000", "my-django-app")

    def __call__(self, request):
        start_time = time.time()

        response = self.get_response(request)

        response_time = int((time.time() - start_time) * 1000)
        self.autosre.send_request_metric(
            endpoint=request.path,
            method=request.method,
            response_time=response_time,
            status_code=response.status_code
        )

        return response

# settings.py
MIDDLEWARE = [
    # ... other middleware
    'your_app.middleware.AutoSREMiddleware',
]
```

### AutoSRE API Endpoints for Integration

AutoSRE provides several endpoints for external application integration:

#### **Custom Metrics Endpoint**

```bash
POST /api/metrics/custom
Content-Type: application/json

{
    "app_name": "my-app",
    "endpoint": "/api/users",
    "response_time": 150,
    "status_code": 200,
    "user_count": 1000,
    "custom_metric": "value"
}
```

#### **Logs Endpoint**

```bash
POST /api/logs
Content-Type: application/json

{
    "app_name": "my-app",
    "logs": [
        "User login successful",
        "Database query completed",
        "Error: Connection timeout"
    ]
}
```

#### **Application Management**

```bash
# List connected applications
GET /api/applications

# Get metrics for specific application
GET /api/applications/{app_name}/metrics
```

### Testing the Integration

#### **Run the Example Integration**

```bash
# Start AutoSRE first
docker-compose up -d

# Run the example integration
python3 example_integration.py
```

#### **Test with Your Application**

```bash
# Test the client library
python3 autosre_client.py

# Test specific endpoints
curl -X POST http://localhost:8000/api/metrics/custom \
  -H "Content-Type: application/json" \
  -d '{"app_name": "test-app", "endpoint": "/test", "response_time": 100}'

curl -X POST http://localhost:8000/api/logs \
  -H "Content-Type: application/json" \
  -d '{"app_name": "test-app", "logs": ["Test log entry"]}'
```

### Integration Workflow

#### **Step 1: Start AutoSRE**

```bash
# Start AutoSRE monitoring platform
docker-compose up -d

# Verify it's running
curl http://localhost:8000/health
```

#### **Step 2: Install the Client Library**

```bash
# Copy the client library to your project
cp autosre_client.py /path/to/your/app/

# Install dependencies
pip install requests
```

#### **Step 3: Integrate with Your Application**

```python
# In your application
from autosre_client import AutoSREClient

# Initialize client
autosre = AutoSREClient("http://localhost:8000", "your-app-name")

# Send metrics when API calls happen
def your_api_endpoint():
    start_time = time.time()

    # Your API logic here
    result = process_request()

    # Send metrics to AutoSRE
    response_time = int((time.time() - start_time) * 1000)
    autosre.send_request_metric(
        endpoint="/api/your-endpoint",
        method="POST",
        response_time=response_time,
        status_code=200
    )

    return result
```

#### **Step 4: Monitor Your Application**

- **AutoSRE Dashboard**: http://localhost:3000
- **Grafana Dashboard**: http://localhost:3001
- **Backend API**: http://localhost:8000/docs

### What You'll See

#### **In AutoSRE Dashboard:**

- ✅ Real-time metrics from your application
- ✅ Request/response times
- ✅ Error rates and logs
- ✅ Custom application metrics
- ✅ System resource usage

#### **In Grafana:**

- 📈 Historical data and trends
- Professional monitoring dashboards
- 🔔 Alerting capabilities
- 🔍 Custom queries and visualizations

### Advanced Integration Options

#### **1. Database Integration**

```python
# Store metrics in your database and sync with AutoSRE
def store_and_sync_metrics(metrics):
    # Store in your database
    db.metrics.insert(metrics)

    # Sync with AutoSRE
    autosre.send_metrics(metrics)
```

#### **2. Log Aggregation**

```python
# Send all your application logs to AutoSRE
import logging

class AutoSREHandler(logging.Handler):
    def emit(self, record):
        log_entry = self.format(record)
        autosre.send_logs([log_entry])

# Add to your logger
logger = logging.getLogger()
logger.addHandler(AutoSREHandler())
```

#### **3. Custom Business Metrics**

```python
# Send custom business metrics
autosre.send_metrics({
    "orders_per_minute": 15,
    "revenue_today": 2500.50,
    "active_users": 1250,
    "conversion_rate": 2.5
})
```

### Benefits for Your Application

1. **Immediate Monitoring**: Get professional monitoring without building it
2. **Real-time Insights**: See what's happening in your app instantly
3. **Error Tracking**: Catch and analyze errors early
4. **Performance Monitoring**: Track response times and bottlenecks
5. **Professional Dashboards**: Beautiful Grafana dashboards out of the box
6. **Scalable**: Works with any size application
7. **Production Ready**: Enterprise-grade monitoring solution

### Troubleshooting Integration

#### **Common Issues**

1. **Connection Refused**

   ```bash
   # Check if AutoSRE is running
   docker-compose ps
   curl http://localhost:8000/health
   ```

2. **CORS Errors**

   ```python
   # Ensure your app's domain is in AutoSRE's CORS settings
   # Check backend/main.py CORS configuration
   ```

3. **Metrics Not Appearing**

   ```bash
   # Check AutoSRE logs
   docker-compose logs backend

   # Test API endpoints manually
   curl -X POST http://localhost:8000/api/metrics/custom \
     -H "Content-Type: application/json" \
     -d '{"app_name": "test", "test": "value"}'
   ```

#### **Debug Mode**

```python
# Enable debug logging
import logging
logging.basicConfig(level=logging.DEBUG)

# Create client with debug
autosre = AutoSREClient("http://localhost:8000", "debug-app")
```

### Integration Checklist

- [ ] AutoSRE is running (`docker-compose up -d`)
- [ ] Client library is installed (`autosre_client.py`)
- [ ] Dependencies are installed (`pip install requests`)
- [ ] Application can reach AutoSRE (`curl http://localhost:8000/health`)
- [ ] Metrics are being sent (check AutoSRE dashboard)
- [ ] Logs are being sent (check AutoSRE dashboard)
- [ ] Grafana dashboards are working (http://localhost:3001)
