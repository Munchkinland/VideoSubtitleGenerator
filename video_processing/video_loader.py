# video_processing/video_loader.py

import moviepy.editor as mp

class VideoLoader:
  def __init__(self, video_path):
      self.video_path = video_path
      self.video = mp.VideoFileClip(video_path)

  def get_audio(self):
      """
      Devuelve el objeto de audio del video.
      """
      return self.video.audio

  def get_duration(self):
      """
      Devuelve la duración del video en segundos.
      """
      return self.video.duration