# Laundry Management API

[![CI/CD Pipeline](https://github.com/YOUR_USERNAME/laundry-operation/actions/workflows/ci.yml/badge.svg)](https://github.com/YOUR_USERNAME/laundry-operation/actions/workflows/ci.yml)
[![Coverage](https://codecov.io/gh/YOUR_USERNAME/laundry-operation/branch/main/graph/badge.svg)](https://codecov.io/gh/YOUR_USERNAME/laundry-operation)
[![Python Version](https://img.shields.io/badge/python-3.9%2B-blue.svg)](https://www.python.org/downloads/)

API untuk mengelola operasi laundry dengan arsitektur Domain-Driven Design (DDD) yang terdiri dari beberapa Bounded Contexts.

## 📋 Table of Contents

- [Features](#features)
- [Architecture](#architecture)
- [Installation](#installation)
- [Usage](#usage)
- [API Documentation](#api-documentation)
- [Testing](#testing)
- [Deployment](#deployment)
- [Contributing](#contributing)

## ✨ Features

- **Authentication & Authorization**: JWT-based authentication system
- **Order & Laundry Operation**: Core business logic untuk mengelola pesanan dan operasi laundry
- **Billing & Payment**: Sistem perhitungan biaya dan webhook pembayaran
- **Logistics & Notification**: Manajemen pengiriman dan notifikasi
- **Customer & Resources**: Manajemen pelanggan, pekerja, dan mesin laundry
- **Comprehensive Testing**: 95%+ test coverage dengan unit tests
- **CI/CD Pipeline**: Automated testing, linting, and coverage checks

## 🏗️ Architecture

Aplikasi ini menggunakan arsitektur Domain-Driven Design (DDD) dengan beberapa Bounded Contexts:

### Bounded Contexts

1. **Order & Laundry Operation (Core BC)**
   - Manajemen task laundry
   - Status tracking (pending, in_progress, completed)
   - Estimasi durasi

2. **Billing & Payment (Supporting BC)**
   - Perhitungan biaya berdasarkan berat dan tipe layanan
   - Webhook untuk notifikasi pembayaran
   - Status tracking pembayaran

3. **Logistics & Notification (Supporting BC)**
   - Penjadwalan pickup dan delivery
   - Tracking lokasi kurir
   - Sistem notifikasi

4. **Customer & Resources (Generic BC)**
   - Manajemen data pelanggan
   - Manajemen pekerja/karyawan
   - Manajemen mesin laundry

## 🚀 Installation

### Prerequisites

- Python 3.9 atau lebih tinggi
- pip (Python package manager)

### Setup

1. Clone repository:
```bash
git clone https://github.com/YOUR_USERNAME/laundry-operation.git
cd laundry-operation
```

2. Buat virtual environment (recommended):
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. (Optional) Set environment variables:
```bash
export SECRET_KEY="your-secret-key-here"  # Untuk production, gunakan key yang aman
```

## 📖 Usage

### Menjalankan Server

```bash
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

Server akan berjalan di `http://localhost:8000`

### Mengakses Dokumentasi API

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc
- **OpenAPI JSON**: http://localhost:8000/openapi.json

### Authentication

1. **Login untuk mendapatkan token**:
```bash
curl -X POST "http://localhost:8000/auth/login" \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=testuser&password=testpass"
```

Response:
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer"
}
```

2. **Gunakan token untuk mengakses protected endpoints**:
```bash
curl -X GET "http://localhost:8000/laundry/tasks" \
  -H "Authorization: Bearer YOUR_TOKEN_HERE"
```

## 📚 API Documentation

### Authentication Endpoints

- `POST /auth/login` - Login dan mendapatkan JWT token

### Laundry Operation Endpoints

- `GET /laundry/tasks` - Mendapatkan daftar semua tasks (requires auth)
- `GET /laundry/tasks/{task_id}` - Mendapatkan task tertentu (requires auth)

### Billing Endpoints

- `POST /billing/calculate` - Menghitung biaya layanan
- `POST /billing/payment/webhook` - Webhook untuk notifikasi pembayaran
- `GET /billing/status/{transaction_id}` - Mendapatkan status pembayaran

### Logistics Endpoints

- `POST /logistics/schedule-pickup` - Menjadwalkan pickup (requires auth)
- `POST /logistics/schedule-delivery` - Menjadwalkan delivery (requires auth)
- `POST /logistics/send-notification` - Mengirim notifikasi (requires auth)
- `GET /logistics/courier-location/{order_id}` - Mendapatkan lokasi kurir (requires auth)

### Customer & Resources Endpoints

- `POST /customers/customers` - Membuat pelanggan baru (requires auth)
- `GET /customers/customers/{customer_id}` - Mendapatkan data pelanggan (requires auth)
- `POST /customers/workers` - Menambahkan pekerja (requires auth)
- `GET /customers/workers` - Mendapatkan daftar pekerja (requires auth)
- `POST /customers/machines` - Menambahkan mesin laundry (requires auth)
- `GET /customers/machines` - Mendapatkan daftar mesin (requires auth)

## 🧪 Testing

### Menjalankan Tests

```bash
# Menjalankan semua tests
pytest

# Menjalankan tests dengan coverage
pytest --cov=. --cov-report=html

# Menjalankan tests dengan verbose output
pytest -v

# Menjalankan test file tertentu
pytest tests/test_auth.py
```

### Test Coverage

Proyek ini memiliki test coverage minimal 95%. Untuk melihat coverage report:

```bash
pytest --cov=. --cov-report=html
open htmlcov/index.html  # Buka di browser
```

### Test Structure

```
tests/
├── __init__.py
├── conftest.py          # Pytest fixtures
├── test_auth.py         # Authentication tests
├── test_laundry_operation.py  # Laundry operation tests
├── test_billing.py      # Billing tests
├── test_logistics.py    # Logistics tests
├── test_customers.py    # Customer & resources tests
└── test_main.py         # Main app tests
```

## 🚢 Deployment

### Railway

1. Install Railway CLI:
```bash
npm i -g @railway/cli
```

2. Login ke Railway:
```bash
railway login
```

3. Deploy:
```bash
railway up
```

4. Set environment variables di Railway dashboard:
   - `SECRET_KEY`: Secret key untuk JWT

### Vercel

1. Install Vercel CLI:
```bash
npm i -g vercel
```

2. Deploy:
```bash
vercel
```

3. Set environment variables di Vercel dashboard

### Docker (Optional)

1. Build image:
```bash
docker build -t laundry-api .
```

2. Run container:
```bash
docker run -p 8000:8000 -e SECRET_KEY=your-secret-key laundry-api
```

### Environment Variables

Untuk production, set environment variables berikut:

- `SECRET_KEY`: Secret key untuk JWT (harus kuat dan aman)
- `ENVIRONMENT`: `production` atau `development`

## 🔧 Development

### Code Style

Proyek ini menggunakan:
- **Black** untuk code formatting
- **isort** untuk import sorting
- **flake8** untuk linting

Format code:
```bash
black .
isort .
```

### Pre-commit Hooks (Optional)

Install pre-commit hooks:
```bash
pip install pre-commit
pre-commit install
```

## 📝 Project Structure

```
laundry-operation/
├── .github/
│   └── workflows/
│       └── ci.yml          # CI/CD pipeline
├── auth/                   # Authentication module
│   ├── api.py
│   ├── deps.py
│   └── jwt_handler.py
├── laundryoperation/       # Core BC: Laundry operations
│   ├── api.py
│   ├── models.py
│   ├── repository.py
│   └── services.py
├── billing/                # Supporting BC: Billing
│   └── api.py
├── logistics/              # Supporting BC: Logistics
│   └── api.py
├── customers/              # Generic BC: Customers & Resources
│   └── api.py
├── tests/                  # Test files
│   ├── conftest.py
│   ├── test_auth.py
│   ├── test_laundry_operation.py
│   ├── test_billing.py
│   ├── test_logistics.py
│   ├── test_customers.py
│   └── test_main.py
├── main.py                 # FastAPI application
├── requirements.txt        # Dependencies
├── pytest.ini             # Pytest configuration
├── .coveragerc            # Coverage configuration
└── README.md              # This file
```

## 🤝 Contributing

1. Fork repository
2. Buat feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit changes (`git commit -m 'Add some AmazingFeature'`)
4. Push ke branch (`git push origin feature/AmazingFeature`)
5. Buat Pull Request

Pastikan semua tests pass dan coverage tetap di atas 95% sebelum membuat PR.

## 📄 License

This project is licensed under the MIT License.

## 👥 Authors

- Your Name - [@yourusername](https://github.com/yourusername)

## 🙏 Acknowledgments

- FastAPI untuk framework yang luar biasa
- Pytest untuk testing framework
- Semua contributors yang telah membantu

## 📞 Support

Jika ada pertanyaan atau masalah, silakan buat issue di GitHub repository.

---

**Note**: Ganti `YOUR_USERNAME` dengan username GitHub Anda di badge URLs dan clone URL.

