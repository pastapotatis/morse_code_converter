import numpy as np
from scipy.signal import butter, filtfilt

# ================================
#   FORMATINSTÄLLNINGAR
# ================================
SAMPLE_RATE = 8000
DTYPE = np.int16

# ================================
#   MORSE-TABELL
# ================================
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

# ================================
#   BANDPASSFILTER (300–1200 Hz)
# ================================
def bandpass(data, low=300, high=1200):
    b, a = butter(4, [low/(SAMPLE_RATE/2), high/(SAMPLE_RATE/2)], btype='band')
    return filtfilt(b, a, data)

# ================================
#   DEKODNING
# ================================
def decode_raw_pcm(filename):
    raw = np.fromfile(filename, dtype=DTYPE).astype(np.float32)

    # Normalisera
    raw /= np.max(np.abs(raw))

    # Bandpassfilter (tar bort GSM-brus)
    filtered = bandpass(raw)

    # Energi (mycket stabilare än amplitud)
    window = int(0.015 * SAMPLE_RATE)  # 15 ms
    kernel = np.ones(window) / window
    energy = np.convolve(filtered**2, kernel, mode="same")

    # Adaptiv threshold
    TH = np.percentile(energy, 75) * 0.5
    signal = energy > TH

    # Segmentera pip/paus
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

    # Dot/dash-längd via klustring
    pip_lengths = [l for s, l in durations if s]
    if not pip_lengths:
        return "[Ingen morse hittad]"

    unit = np.median(pip_lengths)

    morse = ""
    symbol = ""

    for s, l in durations:
        if s:  # pip
            if l < 3 * unit:
                symbol += "."
            else:
                symbol += "-"
        else:  # paus
            if l >= 7 * unit:
                morse += MORSE.get(symbol, "?") + " "
                symbol = ""
            elif l >= 3 * unit:
                morse += MORSE.get(symbol, "?")
                symbol = ""

    if symbol:
        morse += MORSE.get(symbol, "?")

    return morse

# ================================
#   KÖR
# ================================
print(decode_raw_pcm("ljud.raw"))
