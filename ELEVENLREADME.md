\## 🚀 Project Overview

This repository contains a specialized AI Agent built to bridge the language gap for English speakers living in Italy. Unlike traditional translators that struggle with group settings, this tool leverages \*\*ElevenLabs Scribe v2\*\* to handle fast-paced, multi-person dialogue.



\## 🛠️ How It Works

1\. \*\*Dynamic Listening:\*\* Instead of fixed timers, the agent uses a 4-second silence threshold (VAD) to know when a speaker has finished a thought.

2\. \*\*Advanced Diarization:\*\* Utilizing the ElevenLabs Scribe v2 API, the script identifies up to 4+ distinct voices and labels them (Speaker A, Speaker B, etc.).

3\. \*\*Contextual Translation:\*\* Italian transcripts are instantly passed through a translation layer to provide immediate English comprehension.

4\. \*\*Auto-Logging:\*\* At the end of every session (Ctrl+C), the script automatically generates a full `Meeting\_Transcript.txt` for later review.



\## 📦 Tech Stack

\- \*\*Python 3.14.0\*\* (Built and tested on the latest release)

\- \*\*ElevenLabs Scribe v2\*\* (Core STT \& Diarization engine)

\- \*\*SoundDevice \& NumPy\*\* (Real-time audio stream processing)

\- \*\*Deep-Translator\*\* (Instant Italian-to-English translation)

