import hashlib
import io
import logging
import os

import requests
from pydub import AudioSegment

AUDIO_PATH = os.getenv("AUDIO_STORAGE_DIR", "./downloaded_audios")


class InvalidAudioError(Exception):
    """Custom exception for invalid audio files."""
    pass


MIME_TO_EXT = {
    "audio/wav": ".wav",
    "audio/wave": ".wav",
    "audio/x-wav": ".wav",
    "audio/mpeg": ".mp3",
    "audio/mp3": ".mp3",
    "audio/ogg": ".ogg",
    "audio/flac": ".flac",
    "audio/x-flac": ".flac",
    "audio/aac": ".aac",
    "audio/x-aac": ".aac",
    "audio/mp4": ".m4a",
    "audio/x-m4a": ".m4a",
}


class AudioHelper:
    def __init__(self, store_audio=False):
        self.logger = logging.getLogger(__name__)
        self.store_audio = store_audio
        logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

    def _generate_filename(self, url: str) -> str:
        """Generate a unique filename based on the URL hash."""
        return hashlib.md5(url.encode()).hexdigest()

    def _is_valid_audio_url(self, url: str) -> bool:
        """Check if the URL is a valid audio file by inspecting headers."""
        try:
            response = requests.head(url, allow_redirects=True, timeout=5)
            content_type = response.headers.get('Content-Type', '')
            return content_type.startswith('audio/')
        except requests.RequestException as e:
            self.logger.error(f"Failed to validate URL: {e}")
            return False

    def download_audio(self, url: str, filename=None) -> io.BytesIO:
        """Download the audio file and return it as a WAV buffer."""
        if not self._is_valid_audio_url(url):
            self.logger.error("Invalid audio URL")
            raise InvalidAudioError(f"Invalid audio content type")

        try:
            response = requests.get(url, stream=True, timeout=30)
            response.raise_for_status()
            audio_buffer = io.BytesIO(response.content)
            content_type = response.headers.get('Content-Type')

            audio_buffer = self.convert_if_needed(audio_buffer, content_type)
            if self.store_audio:
                if filename is None:
                    filename = self._generate_filename(url)
                full_path = os.path.join(AUDIO_PATH, filename)
                with open(f"{full_path}.wav", 'wb') as f:
                    f.write(audio_buffer.getvalue())
                self.logger.info(f"Audio saved as {filename}.wav")
            return audio_buffer
        except requests.RequestException as e:
            self.logger.error(f"Failed to download audio: {e}")
            return None

    def _convert_to_wav(self, audio_buffer: io.BytesIO, ext: str) -> io.BytesIO:
        """Convert audio to WAV format."""
        try:
            audio_buffer.seek(0)
            audio = AudioSegment.from_file(audio_buffer, format=ext.strip('.'))
            audio = audio.set_frame_rate(16000).set_channels(1)
            wav_buffer = io.BytesIO()
            audio.export(wav_buffer, format='wav')
            wav_buffer.seek(0)
            return wav_buffer
        except Exception as e:
            self.logger.error(f"Failed to convert audio to WAV: {e}")
            return None

    def convert_if_needed(self, audio_buffer, content_type) -> io.BytesIO:
        if audio_buffer.getbuffer().nbytes == 0:
            self.logger.error("Downloaded file is empty")
            return None
        ext = MIME_TO_EXT.get(content_type)
        assert ext is not None, f"content type: {content_type} not supported"
        if ext not in ['.wav', '.wave']:
            return self._convert_to_wav(audio_buffer, ext)

        audio = AudioSegment.from_file(audio_buffer, format=ext.strip('.'))
        if audio.frame_rate != 16000:
            audio = audio.set_frame_rate(16000).set_channels(1)
            wav_buffer = io.BytesIO()
            audio.export(wav_buffer, format='wav')
            wav_buffer.seek(0)
            return wav_buffer
        return audio_buffer

