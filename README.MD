# Phonexa - AI English Pronunciation Game

Phonexa is an interactive web application that helps users improve their English pronunciation through AI-based feedback. The app records your voice, analyzes your pronunciation, and provides specific guidance on how to improve.

<img src="https://github.com/EASS-HIT-PART-A-2025-CLASS-VII/Phonexa/blob/main/frontend/src/ProjectImages/PhonexaLogo.png?raw=true" alt="Phonexa Logo" width="200"/>

## Features

- **AI-Powered Pronunciation Analysis**: Get detailed feedback on your pronunciation.
- **Word-Level Feedback**: See exactly which words need improvement.
- **Interactive Audio Guidance**: Listen to correct pronunciations of difficult words.
- **Phonetic Pronunciation**: Hear proper phonetic pronunciations of challenging sounds.
- **Hebrew Translation Hover**: View Hebrew translations of English sentences by hovering over them.
- **Difficulty Progression**: System adapts to your skill level.
- **Streak Tracking**: Monitor your progress with a streak counter.

## Demo

See Phonexa in action! Watch this demonstration of the app's key features:

[![Phonexa Demo](https://img.youtube.com/vi/NOBqmUZFIhg/0.jpg)](https://youtu.be/NOBqmUZFIhg)

*Click the image above to watch the full demonstration video*

## Tech Stack

- **Frontend**: React with audio recording capabilities
- **Backend**: FastAPI server with Wav2Vec2 for pronunciation analysis
- **LLMTeacher**: Dedicated microservice for sentence generation and phonetic pronunciation
- **ML Model**: Facebook's wav2vec2-lv-60-espeak-cv-ft
- **Containerization**: Docker & Docker Compose
- **TTS**: Edge TTS for natural-sounding pronunciation examples & Azure Speech Services for phonetic pronunciations

## Architecture

Phonexa consists of three microservices:
- **Frontend**: React-based user interface (port 3000)
- **Backend**: Core pronunciation analysis service (port 8000)
- **LLMTeacher**: Sentence generation and phonetic TTS service (port 5000)

## Installation & Setup

### Prerequisites

- [Docker](https://docs.docker.com/get-docker/)
- [Docker Compose](https://docs.docker.com/compose/install/)

### Quick Setup

1. **Clone the repository**
    ```bash
    git clone https://github.com/yourusername/phonexa.git
    cd phonexa
    ```

2. **Download the speech model**
    ```bash
    python download_model.py
    ```
    This creates a model_cache directory containing the required ML model files.

3. **Configure environment variables**
    Create or update `.env` files in the appropriate directories with required API keys:
    - For Azure Speech Services in .env
    - For Mistral LLM key (Sentence Generation)
    - For TOGETHER AI's LLM key (Feedback Generation)

4. **Build and run with Docker**
    ```bash
    docker-compose up --build
    ```

5. **Access the application**
    - Frontend: [http://localhost:3000](http://localhost:3000)
    - Backend API: [http://localhost:8000](http://localhost:8000)
    - LLMTeacher API: [http://localhost:5000](http://localhost:5000)

## Usage Guide

1. **Start a Game**: Click the "START" button on the homepage.
2. **Record Your Voice**: Read the sentence aloud and record your pronunciation.
3. **Get Feedback**: Submit your recording to receive AI analysis.
4. **Review Results**: See your score and detailed pronunciation feedback.
5. **Try Again or Continue**: Choose to retry the sentence or move to the next level.

### Key Components

- **Sentence Display**: Shows the current sentence to pronounce.
- **Recording Interface**: Records your pronunciation attempt.
- **Feedback Panel**: Highlights pronunciation errors with specific improvement tips.
- **Audio Playback**: Listen to both your attempt and the correct pronunciation.
- **Phonetic Playback**: Hear how specific phonetic sounds should be pronounced.
- **Navigation**: Retry current level or progress to the next challenge.

### Translation Feature

Hover over any sentence to see its Hebrew translation. This feature helps non-English speakers understand the meaning of what they're pronouncing.

## Common Issues & Troubleshooting

- **Docker Build Takes Too Long**: Pre-download the model with download_model.py before building.
- **Backend Connection Failed**: Ensure ports 8000 and 5000 are not in use by other applications.
- **Audio Recording Issues**: Check that your browser has microphone permissions.
- **Missing Translations**: The translation API may have rate limits or connection issues.
- **Phonetic Pronunciation Issues**: Verify Azure Speech credentials are properly configured.

## License

MIT

## Credits

- **Speech processing**: Facebook Wav2Vec2
- **Text-to-Speech**: Edge TTS & Azure Speech Services
- **Phoneme Alignment**: Custom implementation based on dynamic programming designed by me, engineered with the help of LLM
- **Sentence Generation**: LLM-based dynamic content generation