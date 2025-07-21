# Swizio AI Diagram Service

An async, stateless Python API service for generating architecture diagrams from natural language descriptions, powered by an LLM agent framework.

## Table of Contents

* [Overview](#overview)
* [Features](#features)
* [Directory Structure](#directory-structure)
* [Prerequisites](#prerequisites)
* [Installation](#installation)

  * [Local Setup](#local-setup)
  * [Docker Setup](#docker-setup)
* [Configuration](#configuration)
* [Usage](#usage)

  * [Diagram Generation Endpoint](#diagram-generation-endpoint)
  * [Assistant-Style Endpoint](#assistant-style-endpoint)
* [Examples](#examples)
* [Testing](#testing)
* [Considerations & Limitations](#considerations--limitations)
* [License](#license)

## Overview

This service exposes endpoints for generating diagrams via the [`diagrams`](https://diagrams.mingrammer.com/) package using an async Python framework (FastAPI). Users describe desired architectures in natural language and receive either a rendered image or code. The core logic is stateless and leverages LLM-powered agents with explicit tool integrations.

## Features

* **Stateless API**: No sessions or database.
* **LLM-driven agents**: Custom tools wrap the `diagrams` package to map natural language to diagram code.
* **Multiple node types**: Supports at least three types (e.g., AWS, GCP, on-prem).
* **Image and code output**: Returns PNG images or Python code snippets.
* **Assistant endpoint**: Interactive mode for clarifications or explanations (bonus).
* **Containerized**: Docker + docker-compose for easy deployment.
* **Tests**: Unit tests for core functionality.

## Directory Structure

```
Swizio/
├── src/
│   ├── main.py          # FastAPI app entrypoint
│   ├── agent.py         # Agent orchestration logic
│   ├── tools.py         # Tool wrappers around diagrams package
│   ├── config.py        # Configuration loader
├── tests/               # Unit tests
├── .env                  # Local environment variables (gitignored)
├── .env.example          # Template for required env vars
├── Dockerfile            # Container build definition
├── docker-compose.yml    # Service orchestration
├── pyproject.toml        # Project metadata & dependencies
├── README.md             # This file
└── .gitignore            # Files to ignore in Git
```

## Prerequisites

* Python 3.10+
* [UV](https://github.com/indygreg/uv) for package management
* Docker & Docker Compose (for containerized deployment)
* An API key for your chosen LLM provider (e.g., Google Gemini)

## Installation

### Local Setup

1. **Clone the repo**:

   ```bash
   git clone https://github.com/your-org/swizio.git
   cd swizio
   ```

2. **Install dependencies**:

   ```bash
   uv install
   ```

3. **Configure environment**:

   ```bash
   cp .env.example .env
   # Edit .env to add your LLM_API_KEY and other settings
   ```

4. **Run the server**:

   ```bash
   uv run src.main:app --reload
   ```

### Docker Setup

1. **Build and start containers**:

   ```bash
   docker-compose up --build
   ```

2. **Service will be available at** `http://localhost:8000`

## Configuration

Copy `.env.example` to `.env` and set the following variables:

```ini
LLM_API_KEY=your_api_key_here
LLM_PROVIDER=gemini
DIAGRAMS_OUTPUT_PATH=/tmp/diagrams
```

Additional settings can be found and documented in `src/config.py`.

## Usage

### Diagram Generation Endpoint

**POST** `/v1/diagram`

* **Request Body**:

  ```json
  { "prompt": "Describe your architecture..." }
  ```
* **Response**: PNG image binary (content-type `image/png`)

### Assistant-Style Endpoint (Bonus)

**POST** `/v1/assist`

* **Request Body**:

  ```json
  { "conversation": [
      { "role": "user", "content": "I need a diagram for a web app..." }
    ]
  }
  ```
* **Response**: JSON with either `image_url`, `code_snippet`, or follow-up questions.

## Examples

### Example 1: Simple Web App

**Input**:

```
Create a diagram showing a basic web application with an Application Load Balancer, two EC2 instances for the web servers, and an RDS database for storage. The web servers should be in a cluster named 'Web Tier'.
```

**Curl**:

```bash
curl -X POST http://localhost:8000/v1/diagram \
  -H "Content-Type: application/json" \
  -d '{"prompt": "Create a diagram showing a basic web application with an Application Load Balancer, two EC2 instances for the web servers, and an RDS database for storage. The web servers should be in a cluster named 'Web Tier'."}' \
  --output web_app.png
```

**Output**: `web_app.png`

### Example 2: Microservices Architecture

**Input**:

```
Design a microservices architecture with three services: an authentication service, a payment service, and an order service. Include an API Gateway for routing, an SQS queue for message passing between services, and a shared RDS database. Group the services in a cluster called 'Microservices'. Add CloudWatch for monitoring.
```

**Curl**:

```bash
curl -X POST http://localhost:8000/v1/diagram \
  -H "Content-Type: application/json" \
  -d '{"prompt": "Design a microservices architecture with three services: an authentication service, a payment service, and an order service. Include an API Gateway for routing, an SQS queue for message passing between services, and a shared RDS database. Group the services in a cluster called 'Microservices'. Add CloudWatch for monitoring."}' \
  --output microservices.png
```

**Output**: `microservices.png`

## Testing

Run unit tests with:

```bash
pytest --cov=src tests/
```

## Considerations & Limitations

* **Stateless**: No session or persistence beyond request lifecycle.
* **LLM Reliability**: Behavior depends on LLM responses; prompts are visible and may require tuning.
* **Tool Coverage**: Supports only the pre-defined node types in `src/tools.py`.
* **Cleanup**: Temporary diagram files are removed after serving.

## License

Licensed under the Apache License, Version 2.0. See [LICENSE](LICENSE) for details.
