# Audio Converter

Converts audio files into other formats. Put your files in the `input` folder, run the script, and get the converted files in the `output` folder.

It can also pull the audio out of video files (mp4, mov, mkv, webm, avi).

## Folder layout

```
audio_converter/
├── convert_audio.py    the script
├── requirements.txt    Python packages to install
├── README.md           this file
├── input/              put the files you want converted here
└── output/             converted files appear here, one subfolder per format
    ├── mp3/
    ├── wav/
    └── ...
```

## Setup (one time)

1. Install **Python 3.9 or newer** from https://www.python.org/downloads/
   (on Windows, tick "Add Python to PATH" during install).
2. Open a terminal in the `audio_converter` folder and run:

   ```
   pip install -r requirements.txt
   ```

   This installs a copy of **ffmpeg**, the program that does the conversion.
   If ffmpeg is already installed on your computer, the script uses that one instead,
   and this step is optional.

## How to use

1. Copy the audio files you want converted into the `input` folder.
2. Open a terminal in the `audio_converter` folder and run:

   ```
   python convert_audio.py
   ```

3. It lists the files it found and asks which formats you want. Type one or more,
   separated by spaces (for example `mp3 wav`), or type `all`.
4. The converted files are saved in `output/<format>/`. For example, `input/song.wav`
   converted to mp3 becomes `output/mp3/song.mp3`.

You can also give the formats straight away so it doesn't ask:

| Command | What it does |
|---|---|
| `python convert_audio.py` | Asks which formats you want |
| `python convert_audio.py mp3` | Converts every file to mp3 |
| `python convert_audio.py mp3 wav flac` | Converts every file to mp3, wav and flac |
| `python convert_audio.py --all` | Converts every file to every format |
| `python convert_audio.py mp3 -b 320k` | Converts to mp3 at higher quality (320k) |
| `python convert_audio.py mp3 -i "D:\Music" -o "D:\Converted"` | Uses different input and output folders |
| `python convert_audio.py --help` | Shows all options |

## Options

| Option | Default | Meaning |
|---|---|---|
| `formats` | asks you | One or more formats to convert to |
| `--all` | off | Convert to every supported format |
| `-b`, `--bitrate` | `192k` | Quality for lossy formats. Higher is better quality and bigger files. Common values: `128k`, `192k`, `256k`, `320k` |
| `-i`, `--input` | `input` folder | Folder to read files from |
| `-o`, `--output` | `output` folder | Folder to save converted files to |

## Supported formats

| Format | Type | Notes |
|---|---|---|
| `mp3` | Lossy | Plays everywhere. Good default choice |
| `wav` | Lossless | Uncompressed, very large files. Good for editing |
| `flac` | Lossless | Compressed with no quality loss, about half the size of wav |
| `ogg` | Lossy | Ogg Vorbis. Common in games and on Linux |
| `opus` | Lossy | Best quality for its file size. Used for voice and streaming |
| `m4a` | Lossy | AAC audio. The default on Apple devices and iTunes |
| `aac` | Lossy | Raw AAC stream. Use `m4a` unless something specifically needs `.aac` |
| `aiff` | Lossless | Uncompressed, the Apple equivalent of wav |
| `wma` | Lossy | Windows Media Audio, for older Windows software |

**Lossy** formats remove some audio detail to make files smaller. `--bitrate` controls how much detail is kept.
**Lossless** formats keep everything, so `--bitrate` has no effect on them.

**Files it accepts in the `input` folder:**
`.mp3 .wav .flac .ogg .oga .opus .m4a .aac .aiff .aif .wma .mp4 .mov .mkv .webm .avi`.
Any other files are listed as "ignored" and left alone.

## Good to know

- **Original files are never changed or deleted.** The script only reads from `input`.
- **Converting a file to the format it's already in is skipped.** For example, `song.mp3` won't be converted to mp3 again.
- **Running it again overwrites earlier results** with the same name in `output`.
- **Files with the same name but different extensions**, like `song.mp3` and `song.wav`, keep their old extension
  in the new name so neither overwrites the other: `song_mp3.flac` and `song_wav.flac`.
- **Converting lossy to lossless doesn't improve quality.** An mp3 converted to wav or flac sounds the same as the mp3,
  just in a bigger file.
- **Cover art is not copied** to the converted files. Song info like title and artist is kept.
- **Subfolders inside `input` are not scanned.** Put the files directly in `input`.

## Troubleshooting

**`Error: ffmpeg was not found`**
Run `pip install -r requirements.txt` from inside the `audio_converter` folder.

**`No audio files found`**
Make sure the files are directly inside the `input` folder, not in a subfolder, and have one of the extensions listed above.

**`'python' is not recognized`**
Python isn't on your PATH. On Windows, try `py convert_audio.py` instead, or reinstall Python with "Add Python to PATH" ticked.

**A file shows `[fail]`**
The error message from ffmpeg is printed next to it. Usually the file is damaged, not really an audio file, or
copy-protected (DRM), as some files bought from online stores are. The other files still get converted.
