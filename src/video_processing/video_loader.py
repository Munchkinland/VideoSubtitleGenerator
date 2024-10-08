import moviepy.editor as mp

class VideoLoader:
    def __init__(self, video_path):
        self.video_path = video_path
        self.video = mp.VideoFileClip(video_path)

    def get_audio(self):
        return self.video.audio

    def get_duration(self):
        return self.video.duration
