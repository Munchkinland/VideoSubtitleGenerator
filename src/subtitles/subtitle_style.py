from PIL import ImageFont

class SubtitleStyle:
    def __init__(self, font_path="assets/fonts/Arial.ttf", font_size=24, color=(255, 255, 255)):
        self.font_path = font_path
        self.font_size = font_size
        self.color = color

    def get_font(self):
        return ImageFont.truetype(self.font_path, self.font_size)

    def set_style(self, font_path, font_size, color):
        self.font_path = font_path
        self.font_size = font_size
        self.color = color
