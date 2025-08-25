# SPL Source

A FastAPI-based web application for data sourcing and management.

## Overview

This application provides a REST API for managing data with authentication, user management, and data source integration. Built with FastAPI and designed for scalable deployment.

## Features

- FastAPI web framework
- User authentication and authorization
- Health monitoring endpoints
- Data source integration
- Business logic services
- Configurable environment settings

## Prerequisites

- Python 3.13+
- UV (Python package manager)
- Docker and Docker Compose (optional)

## Quick Start

### 1. Environment Setup

Create a `.env` file in the project root with the following configuration:

```env
# Authentication Configuration
AUTH_STRING="your-secret-auth-string"
PORT="3001"
HOST="localhost"

# Source Configuration
SOURCE_BASE_URL=https://your-source-url.com
SOURCE_USERNAME=your_username
SOURCE_PASSWORD=your_password
```

### 2. Running with UV (Recommended)

Install dependencies:
```bash
uv sync
```

Run the application:
```bash
uv run python main.py
```

### 3. Running with Docker Compose

Build and run with Docker:
```bash
docker-compose up --build
```

The application will be available at `http://localhost:4000` (Docker) or your configured host/port (UV).

## Development

Install development dependencies:
```bash
uv sync --group dev
```

Run linting:
```bash
uv run ruff check
```

## Project Structure

```
├── app/                    # Application core
│   ├── controllers/        # API controllers
│   ├── middleware/         # Custom middleware
│   ├── models/            # Data models
│   ├── services/          # Business logic
│   └── mappers/           # Data mappers
├── config/                # Configuration files
├── utils/                 # Utility functions
├── main.py               # Application entry point
└── docker-compose.yaml   # Docker configuration
```

## API Documentation

Once running, visit `/docs` for interactive API documentation (Swagger UI) or `/redoc` for alternative documentation.

## License

This project is licensed under the terms specified in the project configuration.
