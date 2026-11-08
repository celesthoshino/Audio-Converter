"""
Audio Converter
---------------
Put audio files in the "input" folder, run this script, and the converted
files show up in the "output" folder (one subfolder per format).

    python convert_audio.py              # asks which formats you want
    python convert_audio.py mp3 wav      # convert everything to mp3 and wav
    python convert_audio.py --all        # convert everything to every format

See README.md for all the details.
"""

import argparse
import shutil
import subprocess
import sys
from collections import Counter
from pathlib import Path

# The input/output folders live next to this script, so it works no matter
# which folder you run it from.
BASE_DIR = Path(__file__).resolve().parent
INPUT_DIR = BASE_DIR / "input"
OUTPUT_DIR = BASE_DIR / "output"

# format name -> (file extension, ffmpeg codec arguments, is_lossy)
FORMATS = {
    "mp3":  (".mp3",  ["-c:a", "libmp3lame"], True),
    "wav":  (".wav",  ["-c:a", "pcm_s16le"], False),
    "flac": (".flac", ["-c:a", "flac"], False),
    "ogg":  (".ogg",  ["-c:a", "libvorbis"], True),
    "opus": (".opus", ["-c:a", "libopus"], True),
    "m4a":  (".m4a",  ["-c:a", "aac"], True),
    "aac":  (".aac",  ["-c:a", "aac"], True),
    "aiff": (".aiff", ["-c:a", "pcm_s16be"], False),
    "wma":  (".wma",  ["-c:a", "wmav2"], True),
}

# Files in the input folder with these extensions get converted. Video files
# are accepted too: their audio track is extracted.
INPUT_EXTENSIONS = {
    ".mp3", ".wav", ".flac", ".ogg", ".oga", ".opus", ".m4a", ".aac",
    ".aiff", ".aif", ".wma", ".mp4", ".mov", ".mkv", ".webm", ".avi",
}


def find_ffmpeg() -> str:
    """Use ffmpeg from PATH if it's installed, otherwise the copy that comes with imageio-ffmpeg."""
    system_ffmpeg = shutil.which("ffmpeg")
    if system_ffmpeg:
        return system_ffmpeg
    try:
        import imageio_ffmpeg
        return imageio_ffmpeg.get_ffmpeg_exe()
    except (ImportError, RuntimeError):
        sys.exit(
            "Error: ffmpeg was not found.\n"
            "Fix it by running:  pip install -r requirements.txt\n"
            "(or install ffmpeg yourself: https://ffmpeg.org/download.html)"
        )


def clean_formats(words: list[str]) -> list[str]:
    """Lowercase, drop leading dots and commas, and remove duplicates (keeping order)."""
    formats = []
    for word in words:
        for part in word.replace(",", " ").split():
            fmt = part.lower().lstrip(".")
            if fmt not in formats:
                formats.append(fmt)
    return formats


def unknown_formats(formats: list[str]) -> list[str]:
    return [f for f in formats if f not in FORMATS]


def ask_formats() -> list[str]:
    """Keep asking until the user types valid formats."""
    print("\nAvailable formats: " + ", ".join(FORMATS))
    while True:
        answer = input("Which formats do you want? (e.g. 'mp3 wav', or 'all'): ")
        answer = answer.strip().lstrip("﻿").lower()
        if answer == "all":
            return list(FORMATS)
        formats = clean_formats([answer])
        unknown = unknown_formats(formats)
        if formats and not unknown:
            return formats
        if unknown:
            print(f"  Unknown format(s): {', '.join(unknown)}. Try again.")
        else:
            print("  Please type at least one format.")


def find_input_files(input_dir: Path) -> list[Path]:
    """Return the audio files in input_dir. Other files are listed as ignored."""
    audio_files = []
    for path in sorted(input_dir.iterdir(), key=lambda p: p.name.lower()):
        if not path.is_file() or path.name.startswith("."):
            continue
        if path.suffix.lower() in INPUT_EXTENSIONS:
            audio_files.append(path)
        else:
            print(f"  [ignored] {path.name} (not a supported audio/video file)")
    return audio_files


def output_stem(src: Path, duplicate_stems: set[str]) -> str:
    """
    Name for the converted file (without extension). Two inputs like "song.mp3"
    and "song.wav" would both become "song.flac", so for those the original
    extension is kept in the name: "song_mp3.flac" and "song_wav.flac".
    """
    if src.stem.lower() in duplicate_stems:
        return f"{src.stem}_{src.suffix.lstrip('.').lower()}"
    return src.stem


def convert(ffmpeg: str, src: Path, fmt: str, out_path: Path, bitrate: str) -> bool:
    """Convert one file to one format. Returns True on success."""
    _, codec_args, lossy = FORMATS[fmt]
    cmd = [ffmpeg, "-y", "-hide_banner", "-loglevel", "error",
           "-i", str(src),
           "-vn",  # drop cover art / video
           *codec_args]
    if lossy:
        cmd += ["-b:a", bitrate]
    cmd.append(str(out_path))

    result = subprocess.run(cmd, capture_output=True, encoding="utf-8", errors="replace")
    if result.returncode != 0:
        out_path.unlink(missing_ok=True)  # don't leave half-written files behind
        error_lines = result.stderr.strip().splitlines() or ["unknown error"]
        print(f"  [fail] {fmt:<5} {error_lines[-1]}")  # last line is the actual reason
        return False

    size_kb = out_path.stat().st_size / 1024
    print(f"  [ok]   {fmt:<5} -> {fmt}/{out_path.name}  ({size_kb:,.0f} KB)")
    return True


def main():
    parser = argparse.ArgumentParser(
        description="Convert every audio file in the input folder into other formats.",
        epilog="Supported formats: " + ", ".join(FORMATS),
    )
    parser.add_argument("formats", nargs="*", help="formats to convert to, e.g. mp3 wav flac")
    parser.add_argument("--all", action="store_true", help="convert to every supported format")
    parser.add_argument("-b", "--bitrate", default="192k",
                        help="quality for lossy formats like mp3/ogg/m4a (default: 192k)")
    parser.add_argument("-i", "--input", type=Path, default=INPUT_DIR,
                        help="folder to read files from (default: the input folder)")
    parser.add_argument("-o", "--output", type=Path, default=OUTPUT_DIR,
                        help="folder to save files to (default: the output folder)")
    args = parser.parse_args()

    # Check formats typed on the command line before doing anything else.
    formats = list(FORMATS) if args.all else clean_formats(args.formats)
    unknown = unknown_formats(formats)
    if unknown:
        sys.exit(f"Error: unknown format(s): {', '.join(unknown)}\n"
                 f"Supported: {', '.join(FORMATS)}")

    ffmpeg = find_ffmpeg()
    args.input.mkdir(parents=True, exist_ok=True)
    args.output.mkdir(parents=True, exist_ok=True)

    print(f"Looking in: {args.input}")
    files = find_input_files(args.input)
    if not files:
        print("No audio files found. Put the files you want converted in that folder, then run this again.")
        return

    print(f"Found {len(files)} file(s):")
    for f in files:
        print(f"  - {f.name}")

    if not formats:
        formats = ask_formats()

    stem_counts = Counter(f.stem.lower() for f in files)
    duplicate_stems = {stem for stem, count in stem_counts.items() if count > 1}

    converted = skipped = failed = 0
    for i, src in enumerate(files, start=1):
        print(f"\n[{i}/{len(files)}] {src.name}")
        for fmt in formats:
            ext = FORMATS[fmt][0]
            if src.suffix.lower() == ext:
                print(f"  [skip] {fmt:<5} (file is already {fmt})")
                skipped += 1
                continue
            fmt_dir = args.output / fmt
            fmt_dir.mkdir(exist_ok=True)
            out_path = fmt_dir / (output_stem(src, duplicate_stems) + ext)
            if convert(ffmpeg, src, fmt, out_path, args.bitrate):
                converted += 1
            else:
                failed += 1

    print(f"\nDone: {converted} converted, {skipped} skipped, {failed} failed.")
    print(f"Converted files are in: {args.output}")
    if failed:
        sys.exit(1)


if __name__ == "__main__":
    try:
        main()
    except (KeyboardInterrupt, EOFError):
        print("\nCancelled.")
        sys.exit(1)
