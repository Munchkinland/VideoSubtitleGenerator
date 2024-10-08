# subtitles/srt_generator.py

class SRTGenerator:
  def __init__(self, transcription_segments):
      self.segments = transcription_segments

  def create_srt_file(self, output_path):
      """
      Genera un archivo SRT a partir de los segmentos de transcripción.
      """
      with open(output_path, 'w', encoding='utf-8') as srt_file:
          for i, segment in enumerate(self.segments):
              start_time = self._format_time(segment['start'])
              end_time = self._format_time(segment['end'])
              text = segment['text'].strip()
              srt_file.write(f"{i+1}\n{start_time} --> {end_time}\n{text}\n\n")

  def _format_time(self, seconds):
      """
      Formatea el tiempo en segundos al formato SRT (HH:MM:SS,mmm).
      """
      hours = int(seconds // 3600)
      minutes = int((seconds % 3600) // 60)
      seconds_remainder = int(seconds % 60)
      milliseconds = int((seconds - int(seconds)) * 1000)
      return f"{hours:02}:{minutes:02}:{seconds_remainder:02},{milliseconds:03}"