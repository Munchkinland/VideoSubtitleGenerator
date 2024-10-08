# video_processing/video_subtitle_embedder.py

from moviepy.editor import VideoFileClip, TextClip, CompositeVideoClip
import pysrt

class VideoSubtitleEmbedder:
  def __init__(self, video_path):
      self.video_path = video_path
      self.video = VideoFileClip(video_path)
      self.final_video = None

  def embed_subtitles(self, srt_file, style):
      """
      Incrusta los subtítulos en el video utilizando el archivo SRT y el estilo proporcionado.
      """
      subtitles = pysrt.open(srt_file)
      clips = [self.video]

      for sub in subtitles:
          txt_clip = TextClip(
              sub.text,
              fontsize=style['font_size'],
              font=style['font'],
              color=self._color_to_hex(style['color']),
              method='caption',
              size=(self.video.w * 0.8, None),
              align='center'
          ).set_start(sub.start.ordinal / 1000).set_duration((sub.end.ordinal - sub.start.ordinal) / 1000).set_position(('center', 'bottom'))

          clips.append(txt_clip)

      self.final_video = CompositeVideoClip(clips)

  def save_video(self, output_path):
      """
      Guarda el video final con los subtítulos incrustados.
      """
      if self.final_video:
          self.final_video.write_videofile(output_path, codec='libx264', audio_codec='aac')
      else:
          raise ValueError("No se ha incrustado ningún subtítulo en el video.")

  def _color_to_hex(self, color):
      """
      Convierte el color en formato RGBA al formato hexadecimal.
      """
      r = int(color[0] * 255)
      g = int(color[1] * 255)
      b = int(color[2] * 255)
      return f'#{r:02x}{g:02x}{b:02x}'