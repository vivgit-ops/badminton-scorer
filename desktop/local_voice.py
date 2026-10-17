"""
Offline voice for the Badminton Scorer.
Listens to your microphone with Vosk (no internet) and sends what it hears
to the scorer page, which is served at http://localhost:8000

Folder layout:
  local_voice.py
  index.html      <- the scorer page (rename badminton-scorer.html to index.html)
  model/          <- unzipped Vosk model (rename its folder to "model")

Install once:  pip install vosk sounddevice
Run:           python local_voice.py
"""
import json
import queue
import threading
from http.server import ThreadingHTTPServer, BaseHTTPRequestHandler
from pathlib import Path

import sounddevice as sd
from vosk import Model, KaldiRecognizer, SetLogLevel

SetLogLevel(-1)
HERE = Path(__file__).parent
MODEL_DIR = HERE / "model"
PORT = 8000

# Only these words are recognised, which keeps scores accurate.
WORDS = ("zero one two three four five six seven eight nine ten eleven twelve "
         "thirteen fourteen fifteen sixteen seventeen eighteen nineteen "
         "twenty thirty all undo love play").split()

clients = []
lock = threading.Lock()


def broadcast(text):
    with lock:
        for q in list(clients):
            q.put(text)


class Handler(BaseHTTPRequestHandler):
    def log_message(self, *args):
        pass

    def do_GET(self):
        if self.path == "/events":
            self.send_response(200)
            self.send_header("Content-Type", "text/event-stream")
            self.send_header("Cache-Control", "no-cache")
            self.end_headers()
            q = queue.Queue()
            with lock:
                clients.append(q)
            try:
                while True:
                    try:
                        text = q.get(timeout=15)
                        self.wfile.write(f"data: {text}\n\n".encode())
                    except queue.Empty:
                        self.wfile.write(b": keep-alive\n\n")
                    self.wfile.flush()
            except Exception:
                pass
            finally:
                with lock:
                    if q in clients:
                        clients.remove(q)
        else:
            data = (HERE / "index.html").read_bytes()
            self.send_response(200)
            self.send_header("Content-Type", "text/html; charset=utf-8")
            self.send_header("Content-Length", str(len(data)))
            self.end_headers()
            self.wfile.write(data)


def listen():
    model = Model(str(MODEL_DIR))
    rec = KaldiRecognizer(model, 16000, json.dumps(WORDS + ["[unk]"]))
    audio = queue.Queue()

    def callback(indata, frames, time, status):
        audio.put(bytes(indata))

    with sd.RawInputStream(samplerate=16000, blocksize=8000, dtype="int16",
                           channels=1, callback=callback):
        print("Listening... say the score, for example: five three")
        while True:
            if rec.AcceptWaveform(audio.get()):
                text = json.loads(rec.Result()).get("text", "")
                text = text.replace("[unk]", "").strip()
                if text:
                    print("Heard:", text)
                    broadcast(text)


if __name__ == "__main__":
    threading.Thread(target=listen, daemon=True).start()
    print(f"Open http://localhost:{PORT} in your browser (Ctrl+C to stop)")
    ThreadingHTTPServer(("127.0.0.1", PORT), Handler).serve_forever()
