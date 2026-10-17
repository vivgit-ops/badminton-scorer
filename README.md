# Badminton Scorer

**On your phone:** https://vivgit-ops.github.io/badminton-scorer/ (use Chrome, tap the mic button).

## Run offline voice on your computer

1. Install Python: https://www.python.org/downloads/ (tick "Add Python to PATH").
   Check it works: `python --version`
2. Download this project: green **Code** button > **Download ZIP**, then unzip it.
3. Open a terminal inside the `desktop` folder and run:

```
pip install vosk sounddevice
python local_voice.py
```

4. Open http://localhost:8000 in your browser and say the score.

The voice model is already in `desktop/model`, so there is nothing else to download. Make sure your microphone is the default input in Windows.

## What to say

- `five three` = 5-3, `ten all` = 10-10, `twenty one fifteen` = 21-15
- `undo` = take back the last score
- `play` = swap the score (5-3 becomes 3-5)
