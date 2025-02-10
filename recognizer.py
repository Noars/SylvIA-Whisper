#!/usr/bin/env python

import wave
from faster_whisper import WhisperModel

class Recognizer():
    def __init__(self):
        self.model = WhisperModel("small", device="cuda", compute_type="float32")

    def decode(self, filename):
        segments, _ = self.model.transcribe(filename, language="fr", beam_size=1, task="transcribe", vad_filter=False)
        result = "".join(segment.text for segment in segments)  # Concatène tous les segments transcrits
        return result