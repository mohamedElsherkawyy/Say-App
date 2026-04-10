# Say App — AI-Powered Expense Tracker API

A FastAPI backend that lets users log their expenses through **voice** or **receipt images**, then get smart financial analysis. Built with Groq LLMs, LangChain, and speech recognition — designed for Egyptian Arabic speakers.

---

## Features

- **Voice-to-Expense**: Upload an audio file (`.ogg`, `.wav`, `.mp3`, etc.) spoken in Egyptian Arabic — the app transcribes it, then extracts and categorizes every expense automatically.
- **Receipt OCR**: Upload a receipt image — the app reads it via a vision LLM and categorizes all line items.
- **Expense Analysis**: Send a list of transactions and get a detailed financial summary with insights and saving tips — all in Egyptian Arabic.

---

## API Endpoints

| Method | Endpoint   | Description                                               |
|--------|------------|-----------------------------------------------------------|
| GET    | `/`        | Health check                                              |
| POST   | `/audio`   | Upload a voice file to extract & categorize expenses      |
| POST   | `/image`   | Upload a receipt image to extract & categorize expenses   |
| POST   | `/analyze` | Analyze a list of transactions and get a financial report |

### `POST /audio`

**Form data:** `voice_file` — any common audio format (`.ogg`, `.wav`, `.mp3`, `.flac`, `.m4a`, `.aac`)

**Response example:**
```json
{
  "response": {
    "categories": {
      "food": "500",
      "transportation": "150",
      "groceries": 300.0
    }
  }
}
```

### `POST /image`

**Form data:** `image_file` — a JPEG or PNG receipt photo

**Response example:**
```json
{
  "response": {
    "categories": {
      "groceries": 245.0,
      "food": "60"
    }
  }
}
```

### `POST /analyze`

**JSON body:**
```json
{
  "transactions": [
    { "month": "April", "amount": 500.0, "category": "food" },
    { "month": "April", "amount": 200.0, "category": "transportation" }
  ]
}
```

**Response example:**
```json
{
  "response": {
    "month": "April",
    "total_spent": 700.0,
    "categories": [...],
    "top_categories": [...],
    "insights": ["معظم مصاريفك في الأكل..."],
    "savings_tips": ["حاول تطبخ في البيت أكتر..."]
  }
}
```

---

## Expense Categories

The app recognizes the following categories:

| Category          | Description                                     |
|-------------------|-------------------------------------------------|
| `food`            | Restaurants, cafes, coffee shops, takeaway      |
| `groceries`       | Supermarkets, fresh produce, household supplies |
| `bills`           | Electricity, water, internet, phone             |
| `transportation`  | Taxi, bus, metro                                |
| `travel`          | Hotels, Airbnb, flights                         |
| `shopping`        | Clothes, shoes, accessories                     |
| `fitness`         | Gym, yoga, sports                               |
| `entertainment`   | Movies, concerts, games                         |
| `healthCare`      | Doctor, pharmacy, hospital, insurance           |
| `education`       | School, university, courses                     |
| `vehicleServices` | Car repair, maintenance, fuel                   |
| `other`           | Anything else                                   |

---

## Tech Stack

| Layer              | Technology                                          |
|--------------------|-----------------------------------------------------|
| API Framework      | FastAPI + Uvicorn                                   |
| LLM Provider       | [Groq](https://groq.com/) (LLaMA 3.3 70B + LLaMA 4 Scout Vision) |
| LLM Orchestration  | LangChain + LangChain-Groq                          |
| Speech-to-Text     | Google Speech Recognition (`SpeechRecognition` lib) |
| Audio Processing   | Librosa + SoundFile                                 |
| Image Processing   | Pillow (compression + base64 encoding)              |
| Data Validation    | Pydantic v2                                         |
| Containerization   | Docker                                              |
| Deployment         | AWS EC2 / Fly.io                                    |
| CI/CD              | GitHub Actions                                      |

---

## Project Structure

```
Say-App/
├── app.py                  # FastAPI app & route definitions
├── config.py               # Environment variable loading (GROQ_API_KEY)
├── llm.py                  # Groq/LangChain LLM calls & response parsing
├── models.py               # Pydantic request/response models
├── prompts.py              # LLM prompt templates
├── Speech_Recognition.py   # Audio transcription (Google STT)
├── encoder.py              # Audio format conversion & image base64 encoding
├── ocr.py                  # Image preprocessing & base64 encoding
├── requirements.txt        # Python dependencies
├── Dockerfile              # Docker image definition
├── fly.toml                # Fly.io deployment configuration
└── .github/
    └── workflows/
        └── deploy.yml      # CI/CD pipeline (GitHub Actions → EC2)
```

---

## Getting Started

### Prerequisites

- Python 3.10+
- A [Groq API key](https://console.groq.com/)

### Installation

```bash
# Clone the repository
git clone <your-repo-url>
cd Say-App

# Create and activate a virtual environment
python -m venv venv
# Windows:
venv\Scripts\activate
# Linux/macOS:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### Environment Variables

Create a `.env` file in the project root:

```env
GROQ_API_KEY=your_groq_api_key_here
```

### Run Locally

```bash
uvicorn app:app --host 0.0.0.0 --port 8000 --reload
```

The API will be available at `http://localhost:8000`.  
Interactive docs: `http://localhost:8000/docs`

---

## Docker

### Build & Run

```bash
docker build -t say-app .
docker run -p 8000:8000 --env-file .env say-app
```

---

## Deployment

### Fly.io

```bash
fly auth login
fly deploy
```

The app is configured in `fly.toml` as `say-app-model-new` in the `cdg` (Paris) region with 1 GB RAM.

### AWS EC2 (via GitHub Actions)

Pushes to the `main` branch automatically trigger the CI/CD pipeline in `.github/workflows/deploy.yml`, which:

1. SSHs into the EC2 instance
2. Pulls the latest code
3. Installs new dependencies
4. Restarts the `sayapp` systemd service

**Required GitHub Secrets:**

| Secret          | Description                  |
|-----------------|------------------------------|
| `EC2_HOST`      | Public IP / hostname of EC2  |
| `EC2_USERNAME`  | SSH username (e.g. `ec2-user`) |
| `EC2_SSH_KEY`   | Private SSH key (PEM content) |

---

## Notes

- Speech recognition is tuned for **Egyptian Arabic (`ar-EG`)** using Google's Speech Recognition API.
- The LLM prompts are designed to handle self-corrections in speech (e.g., "I spent 400... no wait, 500") and always use the last stated amount.
- Receipt images are automatically compressed before being sent to the vision model to reduce latency and cost.
