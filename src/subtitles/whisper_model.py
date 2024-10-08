import whisper

class WhisperModel:
    def __init__(self, model_size='small'):
        self.model = whisper.load_model(model_size)

    def transcribe_video(self, video_path, language='en'):
        # Transcribe the audio from video and return subtitles with timestamps
        result = self.model.transcribe(video_path, language=language)
        return result['segments']
