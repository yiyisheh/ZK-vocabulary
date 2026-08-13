"""Build the two shipping shapes of the app from web/template.html.

1) SINGLE FILE  ->  <single_file>.html
   Everything inlined, audio as base64 in <script type="application/json"> blocks.
   This is the AirDrop-it-and-it-works copy; it never touches the network.

2) HOSTED (PWA) ->  <docs_dir>/
   index.html      the shell: layout + logic + all entries of TEXT
   audio-us.<h>.bin  raw mp3 bytes of the word clips, concatenated
   audio-ex.<h>.bin  same for the example sentences
   sw.js / manifest / icons

Supports --profile {cet4,zhongkao} to build for different projects.
Default is cet4 (backward compatible).
"""
import argparse
import base64
import hashlib
import json
import shutil
from datetime import datetime
from pathlib import Path

REPO = Path(__file__).parent.parent

PROFILES = {
    "cet4": {
        "data":       REPO / "intermediate" / "entries_full.json",
        "audio":      REPO / "intermediate" / "audio",
        "single":     REPO / "英语四级单词背诵.html",
        "docs":       REPO / "docs",
        "cache_name": "cet4-1250",
        "app_title":  "四级1250",
        "page_title": "四级高频单词 · 背诵",
        "desc":       "2021–2025 真题 · top 1250 · 含词根词缀 · 排版对齐优化版 PDF",
        "top_title":  "四级高频 1250",
        "sync_hint":  "同步码，如 cet4-9f3k",
        "ls_key":     "cet4_reader_v3",
        "snooze_key": "cet4_upd_snooze",
        "manifest": {
            "name": "四级高频单词 · 背诵",
            "short_name": "四级1250",
            "description": "CET-4 高频 1250 词，含词根词缀、离线发音",
        },
    },
    "zhongkao": {
        "data":       REPO / "intermediate" / "entries_full.json",
        "audio":      REPO / "intermediate" / "audio",
        "single":     REPO / "英语中考单词背诵.html",
        "docs":       REPO / "docs",
        "cache_name": "zk-688",
        "app_title":  "中考688",
        "page_title": "中考高频单词 · 背诵",
        "desc":       "历年中考真题 · 688 词 · 含词根词缀 · 排版对齐优化版 PDF",
        "top_title":  "中考高频 688",
        "sync_hint":  "同步码，如 zk-9f3k",
        "ls_key":     "zk_reader_v1",
        "snooze_key": "zk_upd_snooze",
        "manifest": {
            "name": "中考高频单词 · 背诵",
            "short_name": "中考688",
            "description": "中考高频 688 词，含词根词缀、离线发音",
        },
    },
}

parser = argparse.ArgumentParser()
parser.add_argument("--profile", choices=PROFILES, default="zhongkao")
args = parser.parse_args()
P = PROFILES[args.profile]

DATA = json.loads(P["data"].read_text())
AUD = P["audio"]
TPL = (REPO / "web" / "template.html").read_text()
OUT = P["single"]
DOCS = P["docs"]
PWA_DIR = REPO / "web" / "pwa"
CACHE_NAME = P["cache_name"]
MAX_RANK = str(len(DATA))
MIN_BYTES = {"us": 500, "ex": 300}

slim = [{
    "rank": e["rank"], "word": e["word"], "syl": e["syl"],
    "uk": e["uk"], "us": e["us"], "def": e["def"],
    "ex_label": e["ex_label"], "ex": e["ex"], "root": e["root"],
} for e in DATA]


def clips(kind):
    """[(key, bytes)] for one audio set. us is keyed by word (what speak() has), ex by rank."""
    out = []
    for e in DATA:
        f = AUD / kind / f"{e['rank']}.mp3"
        if f.exists() and f.stat().st_size > MIN_BYTES[kind]:
            key = e["word"] if kind == "us" else str(e["rank"])
            out.append((key, f.read_bytes()))
    return out


def inline_json(items):
    return json.dumps({k: base64.b64encode(b).decode("ascii") for k, b in items},
                      ensure_ascii=False, separators=(",", ":"))


def pack(items):
    """Concatenate the clips and index them -> (blob, {key: [offset, length]})."""
    blob, index, off = bytearray(), {}, 0
    for k, b in items:
        blob += b
        index[k] = [off, len(b)]
        off += len(b)
    return bytes(blob), index


us_items, ex_items = clips("us"), clips("ex")
cfg = REPO / "web" / "supabase-config.json"
sync_config = cfg.read_text().strip() if cfg.exists() else "null"

# ---------- shared: build a filled template, given the audio-carrying bits ----------
def render(audio_us, audio_ex, audio_index):
    return (TPL
            .replace("__DATA__", json.dumps(slim, ensure_ascii=False, separators=(",", ":")))
            .replace("__AUDIO_US__", audio_us)
            .replace("__AUDIO_EX__", audio_ex)
            .replace("__AUDIO_INDEX__", audio_index)
            .replace("__CACHE_NAME__", CACHE_NAME)
            .replace("__SYNC_CONFIG__", sync_config)
            .replace("__APP_TITLE__", P["app_title"])
            .replace("__PAGE_TITLE__", P["page_title"])
            .replace("__DESC__", P["desc"])
            .replace("__TOP_TITLE__", P["top_title"])
            .replace("__SYNC_HINT__", P["sync_hint"])
            .replace("__LS_KEY__", P["ls_key"])
            .replace("__SNOOZE_KEY__", P["snooze_key"])
            .replace("__MAX_RANK__", MAX_RANK))


def stamp(html, build_hash, build_time):
    return html.replace("__BUILD_INFO__",
                        json.dumps({"v": build_hash, "t": build_time}, ensure_ascii=False))


# ---------- hosted: shell + packs ----------
us_blob, us_index = pack(us_items)
ex_blob, ex_index = pack(ex_items)
us_name = f"audio-us.{hashlib.sha256(us_blob).hexdigest()[:10]}.bin"
ex_name = f"audio-ex.{hashlib.sha256(ex_blob).hexdigest()[:10]}.bin"

audio_index = json.dumps({
    "us": {"file": us_name, "bytes": len(us_blob), "index": us_index},
    "ex": {"file": ex_name, "bytes": len(ex_blob), "index": ex_index},
}, ensure_ascii=False, separators=(",", ":"))

shell = render("", "", audio_index)
build_hash = hashlib.sha256(shell.encode()).hexdigest()[:12]
build_time = datetime.now().strftime("%Y-%m-%d %H:%M")
shell = stamp(shell, build_hash, build_time)

DOCS.mkdir(exist_ok=True)
for old in DOCS.glob("audio-*.bin"):
    if old.name not in (us_name, ex_name):
        old.unlink()
(DOCS / "index.html").write_text(shell)
(DOCS / us_name).write_bytes(us_blob)
(DOCS / ex_name).write_bytes(ex_blob)

precache = ["./index.html", "./manifest.webmanifest",
            "./icon-180.png", "./icon-192.png", "./icon-512.png"]
keep = precache + ["./" + us_name, "./" + ex_name]

manifest = {
    "name": P["manifest"]["name"],
    "short_name": P["manifest"]["short_name"],
    "description": P["manifest"]["description"],
    "start_url": ".",
    "scope": ".",
    "display": "standalone",
    "orientation": "any",
    "background_color": "#f6efdd",
    "theme_color": "#1f5fa8",
    "icons": [
        {"src": "icon-192.png", "sizes": "192x192", "type": "image/png"},
        {"src": "icon-512.png", "sizes": "512x512", "type": "image/png"},
        {"src": "icon-512.png", "sizes": "512x512", "type": "image/png", "purpose": "maskable"},
    ],
}

for f in PWA_DIR.iterdir():
    if f.name == "sw.js":
        (DOCS / f.name).write_text(f.read_text()
                                   .replace("__CACHE_NAME__", CACHE_NAME)
                                   .replace("__PRECACHE__", json.dumps(precache))
                                   .replace("__KEEP__", json.dumps(keep))
                                   .replace("__BUILD_HASH__", build_hash))
    elif f.name == "manifest.webmanifest":
        (DOCS / f.name).write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n")
    else:
        shutil.copy2(f, DOCS / f.name)

shell_kb = (DOCS / "index.html").stat().st_size // 1024
print(f"-> {DOCS}/  shell {shell_kb} KB + {us_name} ({len(us_blob)//1048576} MB) "
      f"+ {ex_name} ({len(ex_blob)//1048576} MB) + sw.js/manifest/icons, ver={build_hash} @ {build_time}")

# ---------- single file: everything inline ----------
single = stamp(render(inline_json(us_items), inline_json(ex_items), "null"), build_hash, build_time)
OUT.parent.mkdir(parents=True, exist_ok=True)
OUT.write_text(single)
print(f"-> {OUT}  ({OUT.stat().st_size//1048576} MB, {len(slim)} entries, "
      f"audio US={len(us_items)} EX={len(ex_items)})")
