class SRTGenerator:
    def __init__(self, transcription_segments):
        self.segments = transcription_segments

    def create_srt_file(self, output_path):
        with open(output_path, 'w') as srt_file:
            for i, segment in enumerate(self.segments):
                start_time = self._format_time(segment['start'])
                end_time = self._format_time(segment['end'])
                text = segment['text']
                srt_file.write(f"{i+1}\n{start_time} --> {end_time}\n{text}\n\n")

    def _format_time(self, seconds):
        hours = int(seconds // 3600)
        minutes = int((seconds % 3600) // 60)
        seconds = seconds % 60
        milliseconds = int((seconds - int(seconds)) * 1000)
        return f"{hours:02}:{minutes:02}:{int(seconds):02},{milliseconds:03}"
