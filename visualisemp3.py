import numpy as np
import sounddevice as sd
import pyqtgraph.opengl as gl
from PyQt5 import QtWidgets, QtCore
from PyQt5.QtWidgets import QFileDialog, QProgressBar, QPushButton
from pydub import AudioSegment
import sys
import threading

# === Config ===
samplerate = 44100
blocksize = 1024
fft_size = 512
history = 100
num_bins = fft_size // 2
Z = np.zeros((history, num_bins))

x = np.linspace(0, samplerate / 2, num_bins)
y = np.linspace(0, history, history)

# === Qt App and GL View ===
app = QtWidgets.QApplication([])
window = QtWidgets.QMainWindow()
window.setWindowTitle("🎵 MP3 Visualizer")
window.setGeometry(100, 100, 1000, 600)

central_widget = QtWidgets.QWidget()
layout = QtWidgets.QVBoxLayout(central_widget)
window.setCentralWidget(central_widget)

# === Progress Bar ===
progress_bar = QProgressBar()
progress_bar.setRange(0, 1000)
progress_bar.setTextVisible(False)
layout.addWidget(progress_bar)

# === GL View ===
gl_widget = gl.GLViewWidget()
gl_widget.setBackgroundColor('k')
gl_widget.setCameraPosition(distance=150, elevation=30, azimuth=-135)
layout.addWidget(gl_widget)

# === Surface ===
surface = gl.GLSurfacePlotItem(
    x=x, y=y, z=Z.T,
    shader='heightColor',
    computeNormals=False,
    smooth=True
)
surface.scale(0.03, 1.0, 10.0)
surface.translate(-80, -50, 0)
gl_widget.addItem(surface)

# === Upload Button ===
btn = QPushButton("Upload MP3")
layout.addWidget(btn)

# === Playback State ===
stop_flag = False
total_samples = 1
playback_ptr = 0

# === Progress Timer ===
progress_timer = QtCore.QTimer()

def update_progress():
    if total_samples > 0:
        fraction = min(playback_ptr / total_samples, 1.0)
        progress_bar.setValue(int(fraction * 1000))

# === Visualizer Thread ===
def run_visualizer(audio_data):
    global Z, stop_flag, playback_ptr, total_samples
    playback_ptr = 0
    total_samples = len(audio_data)
    chunk_size = blocksize

    while playback_ptr + chunk_size < total_samples and not stop_flag:
        chunk = audio_data[playback_ptr:playback_ptr + chunk_size]
        windowed = chunk * np.hanning(len(chunk))
        spectrum = np.abs(np.fft.rfft(windowed, n=fft_size))[:num_bins]
        spectrum = np.log1p(spectrum / (np.max(spectrum) + 1e-6))

        Z = np.roll(Z, -1, axis=0)
        Z[-1] = spectrum
        surface.setData(z=Z.T)

        playback_ptr += chunk_size
        sd.sleep(int(1000 * chunk_size / samplerate))

    progress_timer.stop()
    progress_bar.setValue(1000)

# === MP3 Upload Handler ===
def upload_mp3():
    global stop_flag, total_samples, playback_ptr
    stop_flag = True  # Stop current playback
    progress_timer.stop()
    progress_bar.setValue(0)

    filename, _ = QFileDialog.getOpenFileName(None, "Choose MP3", "", "Audio Files (*.mp3)")
    if not filename:
        return

    print(f"Loading {filename}...")
    song = AudioSegment.from_mp3(filename).set_channels(1).set_frame_rate(samplerate)
    audio = np.array(song.get_array_of_samples()).astype(np.float32) / (2 ** 15)

    stop_flag = False
    thread = threading.Thread(target=run_visualizer, args=(audio,))
    thread.start()

    sd.play(audio, samplerate)
    progress_timer.start(100)

btn.clicked.connect(upload_mp3)
progress_timer.timeout.connect(update_progress)

# === Run App ===
window.show()
sys.exit(app.exec_())
