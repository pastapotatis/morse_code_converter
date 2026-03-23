Converting a Sound File to RAW PCM for Morse Code Decoding

Most Morse decoders require pure PCM samples with no compression, no headers, and no metadata.
Formats like MP3, FLAC, WAV, GSM, AAC, OGG, etc. all contain:

    compression
    headers
    metadata
    block structures

A Morse decoder needs raw amplitude values with uniform sample spacing, so the audio must be converted to RAW PCM first, before using morse_code_converter.py

Below are examples of how to convert common audio formats to RAW PCM using ffmpeg:

Convert MP3 -> RAW
```
ffmpeg -i input.mp3 -f s16le -ac 1 -ar 8000 output.raw
```

Convert .WAV -> RAW
```
ffmpeg -i input.wav -f s16le -ac 1 -ar 8000 output.raw
```

Convert .FLAC -> RAW
```
ffmpeg -i input.flac -f s16le -ac 1 -ar 8000 output.raw
```

Convert .GSM -> RAW
```
ffmpeg -i input.gsm -f s16le -ac 1 -ar 8000 output.raw
```

Convert .OGG -> RAW
```
ffmpeg -i input.ogg -f s16le -ac 1 -ar 8000 output.raw
```

Convert .M4A -> RAW
```
ffmpeg -i input.m4a -f s16le -ac 1 -ar 8000 output.raw
```

etc.
