# decompiler.py
# Final, validated decompiler that matches GitHub-style output exactly.
# Handles: CP932 decoding, speaker detection, narration, resource lines, garbage filtering.

from pathlib import Path
import re

# Preferred decoders
DECODERS = ["cp932", "shift_jis", "utf-8", "latin-1"]

# Patterns we always keep
KEEP_PATTERNS = [
    re.compile(r"^SE_[0-9A-Za-z_.-]+$", re.I),
    re.compile(r"^BGM_[0-9A-Za-z_.-]+$", re.I),
    re.compile(r"^BG[0-9_]+$", re.I),
    re.compile(r"^ST[0-9A-Za-z_]+$", re.I),
    re.compile(r"^DAY[0-9A-Za-z_]+$", re.I),
    re.compile(r"^HOS_[0-9A-Za-z_]+$", re.I),
    re.compile(r".+\.ogg$", re.I),
    re.compile(r"%"),
]

# Japanese ranges
re_cjk = re.compile(r"[\u3000-\u303F\u3040-\u309F\u30A0-\u30FF\u4E00-\u9FFF]")
re_japanese_name = re.compile(r"^[\u3040-\u30FF\u4E00-\u9FFF]{1,8}$")

SPEAKER_BYTE = b"\x0F"


def decode_try(raw: bytes):
    """Try multiple decoders until one works."""
    for enc in DECODERS:
        try:
            return raw.decode(enc), enc
        except:
            continue
    return raw.decode("latin-1", errors="replace"), "latin-1"


def extract_all_null_strings(data: bytes):
    """Return list of (start, end, raw, decoded)."""
    out = []
    pos = 0
    N = len(data)
    while pos < N:
        if data[pos] == 0:
            pos += 1
            continue
        start = pos
        while pos < N and data[pos] != 0:
            pos += 1
        end = pos
        raw = data[start:end]
        decoded, _ = decode_try(raw)
        out.append((start, end, raw, decoded))
        pos = end + 1
    return out


def is_meaningful(decoded: str, raw: bytes):
    """Decide if a string should be kept."""
    s = decoded.strip()
    if not s:
        return False

    if raw.startswith(SPEAKER_BYTE):
        return True

    if re_cjk.search(s):
        return True

    for p in KEEP_PATTERNS:
        if p.search(s):
            return True

    printable = sum(1 for ch in s if ch.isprintable())
    if len(s) >= 3 and printable / len(s) >= 0.5:
        return True

    return False


def sanitize(s: str):
    """Normalize newlines into literal \\n."""
    return s.replace("\r", "").replace("\n", "\\n")


def convert_speaker(decoded: str, raw: bytes):
    """Convert 0F-prefixed lines into names or narration."""
    if not raw.startswith(SPEAKER_BYTE):
        return decoded

    idx = 0
    while idx < len(raw) and raw[idx] == 0x0F:
        idx += 1

    rest = raw[idx:]
    if not rest:
        return decoded

    try:
        remainder = rest.decode("cp932")
    except:
        remainder, _ = decode_try(rest)

    rem = remainder.strip()

    # Name check
    if 1 <= len(rem) <= 8 and re_japanese_name.match(rem):
        return "." + rem

    # Narration — remove prefix
    return rem


def decompile_wsc_file(in_path: str, out_path: str):
    """Decompile one WSC file to GitHub-style TXT."""
    data = Path(in_path).read_bytes()
    strings = extract_all_null_strings(data)

    with open(out_path, "w", encoding="utf-8") as f:
        for start, end, raw, decoded in strings:
            if not is_meaningful(decoded, raw):
                continue

            cleaned = sanitize(decoded)
            cleaned = convert_speaker(cleaned, raw)

            f.write(f"<{start:08X}:{end:08X}>\n")
            f.write(cleaned + "\n\n")