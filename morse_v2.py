import sys
import numpy as np
import subprocess
from scipy.signal import butter, filtfilt
from scipy.ndimage import gaussian_filter1d

SAMPLE_RATE = 16000
DTYPE = np.int16

MORSE = {
    ".-": "A", "-...": "B", "-.-.": "C", "-..": "D",
    ".": "E", "..-.": "F", "--.": "G", "....": "H",
    "..": "I", ".---": "J", "-.-": "K", ".-..": "L",
    "--": "M", "-.": "N", "---": "O", ".--.": "P",
    "--.-": "Q", ".-.": "R", "...": "S", "-": "T",
    "..-": "U", "...-": "V", ".--": "W", "-..-": "X",
    "-.--": "Y", "--..": "Z",
    "-----": "0", ".----": "1", "..---": "2", "...--": "3",
    "....-": "4", ".....": "5", "-....": "6", "--...": "7",
    "---..": "8", "----.": "9"
}

def bandpass(data, low=100, high=3000):
    b, a = butter(4, [low/(SAMPLE_RATE/2), high/(SAMPLE_RATE/2)], btype='band')
    return filtfilt(b, a, data)

def decode_raw_pcm(filename):
    raw = np.fromfile(filename, dtype=DTYPE).astype(np.float32)

    if len(raw) == 0:
        return "[Tom fil]"

    # Normalisering
    raw /= np.max(np.abs(raw)) + 1e-9

    # (Valfri) bandpass – kommentera bort om det strular
    try:
        filtered = bandpass(raw)
    except:
        filtered = raw

    filtered /= np.max(np.abs(filtered)) + 1e-9

    # Energi
    window = int(0.02 * SAMPLE_RATE)
    energy = np.convolve(filtered**2, np.ones(window)/window, mode="same")

    # Smooth (MYCKET viktigt)
    energy = gaussian_filter1d(energy, sigma=2)

    # Adaptiv threshold
    TH = np.median(energy) + 0.7 * np.std(energy)
    signal = energy > TH

    # Segmentering
    durations = []
    current = signal[0]
    length = 0

    for s in signal:
        if s == current:
            length += 1
        else:
            durations.append((current, length))
            current = s
            length = 1
    durations.append((current, length))

    pip_lengths = [l for s, l in durations if s]

    if not pip_lengths:
        return "[Ingen morse hittad]"

    # Robust "dot"-längd
    unit = np.percentile(pip_lengths, 20)

    morse = ""
    symbol = ""

    for s, l in durations:
        if s:
            if l < 2.5 * unit:
                symbol += "."
            else:
                symbol += "-"
        else:
            if l > 6 * unit:
                morse += MORSE.get(symbol, "?") + " "
                symbol = ""
            elif l > 2.5 * unit:
                morse += MORSE.get(symbol, "?")
                symbol = ""

    if symbol:
        morse += MORSE.get(symbol, "?")

    return morse.strip()

# ==========================
# MAIN
# ==========================

if len(sys.argv) < 2:
    print("Användning: python3 morse.py <ljudfil>")
    sys.exit(1)

input_file = sys.argv[1]

if input_file.lower().endswith(".raw"):
    raw_file = input_file
else:
    raw_file = "temp.raw"
    subprocess.run([
        "ffmpeg", "-y",
        "-i", input_file,
        "-ac", "1",
        "-ar", str(SAMPLE_RATE),
        "-f", "s16le",
        raw_file
    ], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

print(decode_raw_pcm(raw_file))
