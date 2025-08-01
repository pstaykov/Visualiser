import numpy as np
import sounddevice as sd
import pyqtgraph.opengl as gl
from PyQt5 import QtWidgets
import sys

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
w = gl.GLViewWidget()
w.setWindowTitle("🎵 3D Audio Surface")
w.setGeometry(100, 100, 1000, 600)
w.setBackgroundColor('k')

# Move camera to see the full graph from the left
w.setCameraPosition(distance=150, elevation=30, azimuth=-135)  # -135 = view from bottom-left corner
w.show()

# === Surface Plot ===
surface = gl.GLSurfacePlotItem(
    x=x,
    y=y,
    z=Z.T,
    shader='heightColor',
    computeNormals=False,
    smooth=True  # ✅ smooth surface
)

surface.scale(0.03, 1.0, 10.0)       # Adjust scaling
surface.translate(-80, -50, 0)  # Shift X to start at left edge
w.addItem(surface)

# === Audio Callback ===
def audio_callback(indata, frames, time, status):
    global Z
    if status:
        print(status)

    samples = indata[:, 0] * np.hanning(len(indata))
    spectrum = np.abs(np.fft.rfft(samples, n=fft_size))[:num_bins]
    spectrum = np.log1p(spectrum / (np.max(spectrum) + 1e-6))

    Z = np.roll(Z, -1, axis=0)
    Z[-1] = spectrum
    surface.setData(z=Z.T)

# === Audio Stream ===
stream = sd.InputStream(
    channels=1,
    callback=audio_callback,
    samplerate=samplerate,
    blocksize=blocksize
)
stream.start()

# === Start App Loop ===
if __name__ == '__main__':
    sys.exit(app.exec_())
