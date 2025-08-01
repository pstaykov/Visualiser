# 3D Audio Spectrum Visualizer

A real-time 3D audio spectrum visualizer built in Python using PyQtGraph and PyQt5.  
Supports live microphone input and MP3 playback with visual feedback.

## Features

- Visualize real-time audio from mic or MP3 file
- see frequency and magnitude
- MP3 playback progress bar (2D overlay)

## Prototype

it started as a simple 2D visualiser using matplotlib <br>
<img src="proto.png" width="600"/>

## Screenshots

the microphone Visualiser looks like this when you hum a note. the x axis represents the frequencies y the time and z the magnitude.
<img src="screenshot.png" width="600"/>

## Installation

Make sure you have Python 3.9–3.11 installed.

Install dependencies:

```bash
pip install numpy sounddevice pyqt5 pyqtgraph pydub
