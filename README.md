# Spotify Gesture Controller

Control Spotify with hand gestures. 

## Setup

```bash
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
```

Copy `.env.example` to `.env` and fill in your Spotify app credentials.

Make sure `video_capture/hand_landmarker.task` is present, then run from the project root:

```bash
python main.py
```

## Gestures

| Left hand | Right hand | Action |
|-----------|------------|--------|
| Open palm | Open palm | Play / pause |
| Open palm | One finger | Skip |
| Open palm | Two fingers | Previous |
| Fist | Pinch | Volume |

For fun lol + fully human-coded (minimal vibecoding)