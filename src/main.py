from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.spinner import Spinner
from kivy.uix.filechooser import FileChooserIconView
from kivy.uix.textinput import TextInput
from kivy.uix.colorpicker import ColorPicker
from kivy.uix.popup import Popup
from kivy.uix.dropdown import DropDown
from subtitles.whisper_model import WhisperModel
from subtitles.srt_generator import SRTGenerator
from video_processing.video_loader import VideoLoader
from video_processing.video_subtitle_embedder import VideoSubtitleEmbedder
import os

class SubtitleApp(BoxLayout):
    def __init__(self, **kwargs):
        super(SubtitleApp, self).__init__(**kwargs)
        self.orientation = 'vertical'

        # File chooser for selecting a video
        self.add_widget(Label(text="Select video file:"))
        self.file_chooser = FileChooserIconView()
        self.add_widget(self.file_chooser)

        # Spinner for selecting the subtitle language
        self.add_widget(Label(text="Select subtitle language:"))
        self.language_spinner = Spinner(
            text='English',
            values=('English', 'Spanish', 'French', 'German'),
            size_hint=(None, None),
            size=(200, 44)
        )
        self.add_widget(self.language_spinner)

        # Dropdown for selecting the subtitle font
        self.add_widget(Label(text="Select subtitle font:"))
        self.font_dropdown = DropDown()
        for font in ['Arial', 'Times New Roman', 'Courier New', 'Verdana']:
            btn = Button(text=font, size_hint_y=None, height=44)
            btn.bind(on_release=lambda btn: self.font_dropdown.select(btn.text))
            self.font_dropdown.add_widget(btn)

        self.font_button = Button(text='Select Font')
        self.font_button.bind(on_release=self.font_dropdown.open)
        self.add_widget(self.font_button)

        # Color selection
        self.add_widget(Label(text="Select subtitle color:"))
        self.color_picker = ColorPicker()
        self.add_widget(self.color_picker)

        # Animation selection
        self.add_widget(Label(text="Select subtitle animation:"))
        self.animation_spinner = Spinner(
            text='None',
            values=('None', 'Fade In', 'Slide In', 'Bounce'),
            size_hint=(None, None),
            size=(200, 44)
        )
        self.add_widget(self.animation_spinner)

        # Buttons for actions
        self.process_button = Button(text="Generate Subtitles and Video")
        self.process_button.bind(on_press=self.process_video)
        self.add_widget(self.process_button)

        self.download_button = Button(text="Download Subtitles (.srt) and Video")
        self.download_button.bind(on_press=self.download_files)
        self.add_widget(self.download_button)

        # Label to display status
        self.status_label = Label(text="")
        self.add_widget(self.status_label)

    def process_video(self, instance):
        video_path = self.file_chooser.selection[0]
        language = self.language_spinner.text
        font = self.font_dropdown.selected_value if hasattr(self.font_dropdown, 'selected_value') else 'Arial'
        color = self.color_picker.color
        animation = self.animation_spinner.text

        if not video_path:
            self.show_popup("Error", "Please select a video file.")
            return

        # Load video
        video_loader = VideoLoader(video_path)
        video = video_loader.load_video()

        # Generate subtitles
        whisper_model = WhisperModel(language)
        transcript = whisper_model.transcribe(video_path)

        srt_generator = SRTGenerator(transcript)
        subtitle_path = srt_generator.generate_srt(video_path)

        # Embed subtitles into the video
        video_embedder = VideoSubtitleEmbedder(video, subtitle_path, font, color, animation)
        output_video_path = video_embedder.embed_subtitles()

        self.status_label.text = "Subtitles and video generated successfully."

    def download_files(self, instance):
        # Implement logic for downloading .srt and the new video file
        self.show_popup("Download", "Files are ready for download.")

    def show_popup(self, title, message):
        popup = Popup(title=title, content=Label(text=message), size_hint=(None, None), size=(400, 200))
        popup.open()

class SubtitleAppGUI(App):
    def build(self):
        return SubtitleApp()

if __name__ == '__main__':
    SubtitleAppGUI().run()
