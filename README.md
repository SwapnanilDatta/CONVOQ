# CONVOQ 💬

**AI-Powered WhatsApp Relationship Analyzer**

CONVOQ digs into your chat history to reveal the hidden dynamics of your relationship. It uses statistical analysis, sentiment tracking, and LLM-powered insights to give you a "Vibe Check" on your text game.

🚀 **Live Demo**: [https://convoq.vercel.app/](https://convoq.vercel.app/)

## 🧬 How It Works (The Metrics)

CONVOQ parses your exported chat logs (supports WhatsApp iOS/Android) and calculates the following metrics. **Privacy Note**: Your raw messages are processed in-memory and typically discarded; only the aggregate stats and specific "deep scan" insights are stored.

### 1. Aura / Persona (e.g., "Synchronized Duo")
*   **What it is**: An AI classification of your relationship dynamic.
*   **How it works**: Uses a **K-Means Clustering** algorithm on vectors of your balance scores (Reply Time, Initiation, Sentiment, Length, Emoji).
    *   *Synchronized Duo*: High balance across all metrics (parity).
    *   *One-Sided*: Low balance scores.
    *   *High-Energy*: High emoji density + volatile sentiment.
    *   *Professional/Dry*: Low emoji density + high stability.

### 2. Reply Balance
*   **Formula**: `Min(Avg Time) / Max(Avg Time)`
*   **Description**: Measures the parity of your *speed*. It does not measure who replies *more*, but who replies *faster*.
    *   *Example*: If you take 5 mins avg and they take 10 mins avg, the balance is 50%. Ideally, this is close to 100%.

### 3. Initiation Balance
*   **Formula**: `Min(Starts) / Max(Starts)`
*   **Definition**: A "Start" is credited to the person who sends a message after a **6-hour gap** of silence.
*   **Description**: Who carries the burden of starting the conversation? A 50/50 split is ideal.

### 4. Sentiment Stability
*   **Formula**: `1.0 - Variance(Sentiment Scores)`
*   **Description**: Measures emotional consistency using VADER sentiment analysis.
    *   *High Score*: Emotional rock (always happy, or always neutral).
    *   *Low Score*: Emotional rollercoaster (swings between negative and positive).

### 5. Ghosting & Reply Times
*   **Reply Time**: The time gap between Person A's message and Person B's response.
*   **Ghosting**: The longest single gap between *different* senders.
*   **Logic**: The system ignores "double texts". If you send 3 messages in a row, the gaps between them count as 0 for reply analysis, ensuring we only measure actual response latency.

### 6. Emoji Density
*   **Formula**: `(Messages with >0 emojis) / (Total Messages)`
*   **Description**: Measures the "color" of the chat. It counts the *frequency* of emoji usage (how often you use them), not the raw volume.

### 7. Toxicity Check (Deep Scan)
*   **How it works**: Uses a **Hugging Face (Toxic-BERT)** model to detect hostile language (`insult`, `threat`, `obscene`).
*   **Impact**: High toxicity heavily penalizes the overall "Health Score".

## 🛠️ Tech Stack
*   **Frontend**: React, Vite, TailwindCSS (Glassmorphism UI)
*   **Backend**: FastAPI, Python
*   **AI/ML**: Scikit-Learn (Clustering), NLTK/VADER (Sentiment), Hugging Face (Toxicity), Groq (Coach/Advice)
*   **Database**: Supabase
*   **Storage**: Messages are cached in-memory (TTL) for "Deep Scan" optimization but not persistently stored for privacy.
