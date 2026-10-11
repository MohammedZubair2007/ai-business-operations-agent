
# AI Business Operations Agent

An AI-powered business analysis application that compares monthly sales, identifies declining products, and generates actionable recommendations for human review.

The project uses a locally running LLM through Ollama, so it does not require a paid AI API.

## Features

- **Sales analysis:** Compare monthly revenue and units sold.
- **AI recommendations:** Generate practical suggestions for declining products.
- **Local AI inference:** Run Llama 3.2 through Ollama.
- **Database storage:** Store sales records and recommendations in SQLite.
- **Human-in-the-loop approval:** Approve or reject recommendations before taking action.
- **REST API:** Expose functionality through FastAPI.
- **Interactive API documentation:** Explore endpoints through Swagger UI.
- **Automated tests:** Validate month inputs and API health endpoints.

## Architecture

```text
User / API Client
       |
       v
    FastAPI
       |
       v
Business Operations Agent
       |
       +------> Sales Analysis Tools
       |                |
       |                v
       |             SQLite
       |
       +------> Ollama / Llama 3.2
                        |
                        v
              Business Recommendations
                        |
                        v
                Pending Action Drafts
                        |
                        v
                 Human Approval
```

## Technology Stack

| Component | Technology |
|---|---|
| Language | Python |
| API framework | FastAPI |
| Local AI runtime | Ollama |
| Language model | Llama 3.2 (3B) |
| Database | SQLite |
| Data validation | Pydantic |
| Testing | Pytest |
| API documentation | Swagger UI |

## Prerequisites

- Python 3.12
- Git
- Ollama for Windows, macOS, or Linux
- Sufficient memory and disk space to run the selected local model

## Installation

### 1. Clone the repository

```bash
git clone https://github.com/MohammedZubair2007/ai-business-operations-agent.git
cd ai-business-operations-agent
```

### 2. Create and activate a virtual environment

Windows PowerShell:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

### 3. Install Python dependencies

```bash
python -m pip install -r requirements.txt
```

### 4. Download the local AI model

Install Ollama from [ollama.com](https://ollama.com/), then run:

```bash
ollama pull llama3.2:3b
```

Ensure Ollama is running before using AI-powered endpoints.

### 5. Start the API

```bash
python -m uvicorn app.main:app --reload
```

Open the interactive documentation:

- API documentation: http://127.0.0.1:8000/docs
- Health check: http://127.0.0.1:8000/health

The SQLite database and sample sales data are initialized automatically when the application starts.

## API Endpoints

| Method | Endpoint | Description |
|---|---|---|
| GET | `/` | Project information |
| GET | `/health` | API health check |
| POST | `/analysis/run` | Run sales analysis and generate recommendations |
| GET | `/drafts` | List recommendation drafts |
| PATCH | `/drafts/{draft_id}/decision` | Approve or reject a pending draft |

### Example: Run sales analysis

```http
POST /analysis/run?current_month=2026-09&previous_month=2026-08
```

The agent compares the selected months, asks the local model for recommendations, and saves valid recommendations as pending drafts.

### Example: List pending drafts

```http
GET /drafts?status=pending
```

### Example: Approve a draft

```http
PATCH /drafts/3/decision
Content-Type: application/json

{
  "decision": "approved"
}
```

Approval updates the draft status only. It does not execute external business actions.

## Run Tests

Run the automated test suite:

```bash
python -m pytest tests/test_tools.py -v
```

The current tests cover month validation and basic API endpoints.

## Example Business Scenario

The sample dataset compares August and September 2026 sales. In this example:

- Wireless Mouse revenue declines by 50%.
- USB-C Hub revenue declines by approximately 26.67%.
- Laptop Stand revenue increases by 10%.
- Keyboard revenue increases by 20%.

The agent uses these results to generate recommendations for products with declining revenue.

## Safety and Design

- AI-generated recommendations are stored as drafts.
- Human review is required before a draft can be approved.
- Approval changes the stored status; it does not execute an external action.
- SQL queries use parameters for user-supplied values.
- Local environment files, virtual environments, and the SQLite database are excluded from Git.

## Limitations

- The sample sales dataset is illustrative, not real business data.
- AI recommendations may be inaccurate and should be reviewed.
- The application is a local prototype, not a production deployment.
- Authentication, authorization, and production security controls are not yet implemented.

## Future Improvements

- Add more automated tests for sales analysis and approval workflows.
- Add structured logging and improved error handling.
- Build a dashboard for sales trends and pending recommendations.
- Add user authentication and role-based approvals.
- Add support for additional local language models.

## Author

**Mohammed Zubair**

GitHub: [MohammedZubair2007](https://github.com/MohammedZubair2007)

---

Built as a portfolio project exploring local LLMs, business analytics, API development, and human-in-the-loop AI workflows.
