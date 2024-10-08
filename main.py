# main.py

from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.spinner import Spinner
from kivy.uix.filechooser import FileChooserListView
from kivy.uix.textinput import TextInput
from kivy.uix.colorpicker import ColorPicker
from kivy.uix.popup import Popup
from kivy.core.window import Window
from kivy.uix.behaviors import DragBehavior
from kivy.uix.progressbar import ProgressBar
from kivy.graphics import Color, Rectangle
import threading
import os
import sys

# Establecer la ruta de FFmpeg (hardcodeada)
# Asegúrate de que FFmpeg esté instalado en "C:\ffmpeg\bin\ffmpeg.exe"
os.environ["IMAGEIO_FFMPEG_EXE"] = r"C:\ffmpeg\ffmpeg-2024-08-28-git-b730defd52-full_build\bin\ffmpeg.exe"

# Importar las clases para procesamiento de video y subtítulos
from subtitles.whisper_model import WhisperModel
from subtitles.srt_generator import SRTGenerator
from video_processing.video_loader import VideoLoader
from video_processing.video_subtitle_embedder import VideoSubtitleEmbedder

class DragDropBox(DragBehavior, FloatLayout):
  def __init__(self, **kwargs):
      super(DragDropBox, self).__init__(**kwargs)
      self.drag_rectangle = [self.x, self.y, self.width, self.height]
      self.drag_timeout = 10000
      self.drag_distance = 0

      with self.canvas.before:
          Color(0.9, 0.9, 0.9, 1)  # Color gris claro
          self.rect = Rectangle(size=self.size, pos=self.pos)

      self.bind(size=self._update_rect, pos=self._update_rect)

  def _update_rect(self, instance, value):
      self.rect.pos = instance.pos
      self.rect.size = instance.size

class SubtitleApp(BoxLayout):
  def __init__(self, **kwargs):
      super(SubtitleApp, self).__init__(**kwargs)
      self.orientation = 'vertical'
      self.spacing = 10
      self.padding = 10

      # Inicializar variables para rutas de archivos
      self.subtitle_path = ''
      self.output_video_path = ''

      # Área de arrastrar y soltar
      self.drag_drop_box = DragDropBox(size_hint=(1, None), height=200)
      self.drag_drop_label = Label(
          text="Arrastra y suelta tu archivo de video aquí\no haz clic para seleccionar",
          size_hint=(1, 1),
          color=(0, 0, 0, 1)  # Texto negro
      )
      self.drag_drop_box.add_widget(self.drag_drop_label)
      self.drag_drop_box.bind(on_touch_up=self.on_drag_drop)
      self.add_widget(self.drag_drop_box)

      # Selector de archivos oculto inicialmente
      self.file_chooser = FileChooserListView(filters=['*.mp4', '*.avi', '*.mov'], size_hint=(1, None), height=0)
      self.file_chooser.bind(selection=self.on_file_select)
      self.add_widget(self.file_chooser)

      # Etiqueta de estado del archivo
      self.file_status_label = Label(text="", size_hint_y=None, height=30, color=(0, 0.7, 0, 1))  # Texto verde
      self.add_widget(self.file_status_label)

      # Barra de progreso
      self.progress_bar = ProgressBar(max=100, size_hint_y=None, height=20)
      self.add_widget(self.progress_bar)

      # Indicador de carga
      self.loading_label = Label(text="", size_hint_y=None, height=30)
      self.add_widget(self.loading_label)

      # Selección de idioma
      language_layout = BoxLayout(size_hint_y=None, height=50)
      language_layout.add_widget(Label(text="Idioma de subtítulos:", size_hint_x=None, width=150))
      self.language_spinner = Spinner(
          text='English',
          values=('English', 'Spanish', 'French', 'German'),
          size_hint_x=None,
          width=200
      )
      language_layout.add_widget(self.language_spinner)
      self.add_widget(language_layout)

      # Selección de fuente
      font_layout = BoxLayout(size_hint_y=None, height=50)
      font_layout.add_widget(Label(text="Fuente de subtítulos:", size_hint_x=None, width=150))
      self.font_spinner = Spinner(
          text='Arial',
          values=('Arial', 'Times New Roman', 'Courier New', 'Verdana'),
          size_hint_x=None,
          width=200
      )
      font_layout.add_widget(self.font_spinner)
      self.add_widget(font_layout)

      # Tamaño de fuente
      font_size_layout = BoxLayout(size_hint_y=None, height=50)
      font_size_layout.add_widget(Label(text="Tamaño de fuente:", size_hint_x=None, width=150))
      self.font_size_input = TextInput(text='24', multiline=False, input_filter='int', size_hint_x=None, width=200)
      font_size_layout.add_widget(self.font_size_input)
      self.add_widget(font_size_layout)

      # Selección de color
      color_layout = BoxLayout(size_hint_y=None, height=50)
      color_layout.add_widget(Label(text="Color de subtítulos:", size_hint_x=None, width=150))
      self.color_button = Button(text='Seleccionar Color', size_hint_x=None, width=200)
      self.color_button.bind(on_release=self.show_color_picker)
      color_layout.add_widget(self.color_button)
      self.add_widget(color_layout)

      # Selección de animación
      animation_layout = BoxLayout(size_hint_y=None, height=50)
      animation_layout.add_widget(Label(text="Animación de subtítulos:", size_hint_x=None, width=150))
      self.animation_spinner = Spinner(
          text='None',
          values=('None', 'Fade In', 'Slide In', 'Bounce'),
          size_hint_x=None,
          width=200
      )
      animation_layout.add_widget(self.animation_spinner)
      self.add_widget(animation_layout)

      # Botones de acción
      button_layout = BoxLayout(size_hint_y=None, height=50, spacing=10)
      self.process_button = Button(text="Generar Subtítulos y Video")
      self.process_button.bind(on_press=self.process_video)
      button_layout.add_widget(self.process_button)

      self.download_button = Button(text="Descargar Archivos", disabled=True)
      self.download_button.bind(on_press=self.download_files)
      button_layout.add_widget(self.download_button)
      self.add_widget(button_layout)

      # Etiqueta de estado
      self.status_label = Label(text="", size_hint_y=None, height=50)
      self.add_widget(self.status_label)

      # Vincular el evento on_drop_file
      Window.bind(on_drop_file=self._on_file_drop)

  def on_drag_drop(self, instance, touch):
      if self.drag_drop_box.collide_point(*touch.pos):
          self.file_chooser.height = 300
          self.drag_drop_box.height = 0

  def _on_file_drop(self, window, file_path, x, y):
      self.process_file_selection(file_path.decode('utf-8'))
      return True

  def on_file_select(self, instance, value):
      if value:
          self.process_file_selection(value[0])

  def process_file_selection(self, file_path):
      file_name = os.path.basename(file_path)
      self.file_chooser.selection = [file_path]
      self.drag_drop_label.text = f"Archivo seleccionado: {file_name}"
      self.file_status_label.text = f"Archivo cargado: {file_name}"
      self.drag_drop_box.height = 50  # Reducir el tamaño del cuadro de arrastrar y soltar
      self.file_chooser.height = 0  # Ocultar el selector de archivos

  def show_color_picker(self, instance):
      color_picker = ColorPicker()
      popup = Popup(title='Seleccionar Color de Subtítulos', content=color_picker, size_hint=(0.9, 0.9))
      color_picker.bind(color=self.on_color)
      popup.open()

  def on_color(self, instance, value):
      # Actualizar el color del botón con el color seleccionado
      self.color_button.background_color = value

  def process_video(self, instance):
      if not self.file_chooser.selection:
          self.show_popup("Error", "Por favor, selecciona un archivo de video.")
          return

      # Obtener los parámetros seleccionados
      self.video_path = self.file_chooser.selection[0]
      self.language = self.language_spinner.text
      self.font = self.font_spinner.text
      try:
          self.font_size = int(self.font_size_input.text)
      except ValueError:
          self.show_popup("Error", "El tamaño de fuente debe ser un número entero.")
          return
      self.color = self.color_button.background_color
      self.animation = self.animation_spinner.text

      # Desactivar botones y reiniciar la barra de progreso
      self.process_button.disabled = True
      self.download_button.disabled = True
      self.progress_bar.value = 0
      self.status_label.text = "Procesando video..."
      self.loading_label.text = "Procesando..."

      # Iniciar el procesamiento en un hilo separado
      threading.Thread(target=self.process_video_thread).start()

  def process_video_thread(self):
      try:
          total_steps = 4  # Número de pasos en el procesamiento real
          step = 0

          # Paso 1: Cargar el video
          self.update_progress(step, total_steps, "Cargando video...")
          video_loader = VideoLoader(self.video_path)
          video = video_loader.video
          step += 1
          self.update_progress(step, total_steps, "Transcribiendo audio...")

          # Paso 2: Transcribir audio
          whisper_model = WhisperModel()
          language_code = self.get_language_code(self.language)
          transcription = whisper_model.transcribe_video(self.video_path, language=language_code)
          step += 1
          self.update_progress(step, total_steps, "Generando archivo SRT...")

          # Paso 3: Generar archivo SRT
          srt_generator = SRTGenerator(transcription)
          srt_filename = os.path.splitext(os.path.basename(self.video_path))[0] + '.srt'
          self.subtitle_path = os.path.join(os.path.dirname(self.video_path), srt_filename)
          srt_generator.create_srt_file(self.subtitle_path)
          step += 1
          self.update_progress(step, total_steps, "Incrustando subtítulos en el video...")

          # Paso 4: Incrustar subtítulos en el video
          video_embedder = VideoSubtitleEmbedder(self.video_path)
          output_filename = os.path.splitext(os.path.basename(self.video_path))[0] + '_subtitled.mp4'
          self.output_video_path = os.path.join(os.path.dirname(self.video_path), output_filename)

          # Crear un diccionario para el estilo
          style = {
              'font': self.font,
              'font_size': self.font_size,
              'color': self.color,
              'animation': self.animation
          }

          video_embedder.embed_subtitles(self.subtitle_path, style)
          video_embedder.save_video(self.output_video_path)
          step += 1
          self.update_progress(step, total_steps, "Procesamiento completo.")

          # Actualizar el estado final
          self.status_label.text = "Video procesado exitosamente."
          self.loading_label.text = ""
          self.process_button.disabled = False
          self.download_button.disabled = False
      except Exception as e:
          self.status_label.text = f"Error: {str(e)}"
          self.loading_label.text = ""
          self.process_button.disabled = False
          self.download_button.disabled = True

  def update_progress(self, current_step, total_steps, message):
      progress = (current_step / total_steps) * 100
      self.progress_bar.value = progress
      self.status_label.text = message

  def download_files(self, instance):
      # Implementar lógica para descargar los archivos generados
      if os.path.exists(self.output_video_path) and os.path.exists(self.subtitle_path):
          message = f"Archivos generados:\n{self.output_video_path}\n{self.subtitle_path}"
          self.show_popup("Descarga", message)
      else:
          self.show_popup("Error", "Los archivos no están disponibles para descargar.")

  def show_popup(self, title, message):
      popup = Popup(title=title, content=Label(text=message),
                    size_hint=(0.8, 0.4))
      popup.open()

  def get_language_code(self, language_name):
      """
      Devuelve el código de idioma correspondiente al nombre del idioma.
      """
      language_codes = {
          'English': 'en',
          'Spanish': 'es',
          'French': 'fr',
          'German': 'de'
      }
      return language_codes.get(language_name, 'en')

class SubtitleAppGUI(App):
  def build(self):
      self.title = "Generador de Subtítulos"
      return SubtitleApp()

if __name__ == '__main__':
  SubtitleAppGUI().run()