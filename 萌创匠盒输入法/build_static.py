# -*- coding: utf-8 -*-
"""
静态托管构建脚本（本文件夹 = 萌创匠盒输入法，用于部署到托管平台，不要放进 APK 工程）
1. 词库：编辑 wordlist_src.txt 及 wordlist_src_*.txt（可多个，合并生成），运行后生成 wordlist.txt、wordlist.js
2. 皮肤：运行后生成 skins/list.json 与 skins/white/ 白色壁纸（需 Pillow：pip install Pillow）
3. 把本文件夹整体上传到静态托管；APK 仅通过 URL 拉取词库与皮肤列表
"""
import base64
import os
import re
import json

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
# 支持多个词库源文件（避免单文件过大，托管平台单文件常限制 10MB）
# 会合并所有 wordlist_src*.txt 生成同一份 wordlist.txt / wordlist.js
SRC_GLOB = "wordlist_src*.txt"
SKINS_DIR = os.path.join(SCRIPT_DIR, "skins")

# 皮肤图片尺寸（与 README/skins 说明一致，便于今后做皮肤）
PREVIEW_W, PREVIEW_H = 160, 80   # 预览图：160×80 像素，首页卡片用
BACKGROUND_W, BACKGROUND_H = 720, 320  # 背景图：720×320 像素，键盘背景（含底部横条）拉伸铺满

def to_key(parts):
    key = "".join(re.sub(r"[1-5]$", "", p.strip()) for p in parts).lower()
    key = key.replace("ü", "v").replace("u:", "v")
    for a, b in [("á", "a"), ("à", "a"), ("ā", "a"), ("ǎ", "a"), ("é", "e"), ("è", "e"), ("ē", "e"), ("ě", "e"),
                 ("í", "i"), ("ì", "i"), ("ī", "i"), ("ǐ", "i"), ("ó", "o"), ("ò", "o"), ("ō", "o"), ("ǒ", "o"),
                 ("ú", "u"), ("ù", "u"), ("ū", "u"), ("ǔ", "u")]:
        key = key.replace(a, b)
    return key

# 分类标题正则：# === 分类名 ===
CATEGORY_RE = re.compile(r"^\s*#\s*===\s*(.+?)\s*===\s*$")

def parse_src(path):
    """解析词库源文件，返回 (扁平条目列表, 分类列表)。
    分类列表每项: {"id": "分类名", "name": "分类名", "lines": ["key word", ...]}
    """
    entries = []
    categories = []  # [{"id": str, "name": str, "lines": [str, ...]}, ...]
    current_cat = None  # {"id": str, "name": str, "lines": []}
    seen = set()
    if not os.path.isfile(path):
        return entries, categories
    with open(path, "r", encoding="utf-8") as f:
        for line in f:
            line_stripped = line.strip()
            # 识别分类注释：# === 五金常用词 ===
            m = CATEGORY_RE.match(line_stripped)
            if m:
                cat_name = m.group(1).strip()
                cat_id = cat_name  # APK 可直接用 name 展示或做 key
                current_cat = {"id": cat_id, "name": cat_name, "lines": []}
                categories.append(current_cat)
                continue
            if not line_stripped or line_stripped.startswith("#") or line_stripped == "```":
                continue
            parts = line_stripped.split()
            if len(parts) < 2:
                continue
            word = parts[-1]
            py_parts = [p for p in parts[:-1] if not re.search(r"[\u4e00-\u9fff]", p)]
            if not py_parts:
                continue
            key = to_key(py_parts)
            if not key:
                continue
            if (key, word) in seen:
                continue
            seen.add((key, word))
            entry_line = f"{key} {word}"
            entries.append((key, word))
            if current_cat is not None:
                current_cat["lines"].append(entry_line)
    return entries, categories

def merge_all_src(script_dir):
    """合并所有 wordlist_src*.txt，去重后返回 (扁平条目列表, 分类列表)。"""
    import glob
    pattern = os.path.join(script_dir, SRC_GLOB)
    paths = sorted(glob.glob(pattern))
    all_entries = []
    all_categories = []
    seen = set()
    for path in paths:
        entries, categories = parse_src(path)
        for k, w in entries:
            if (k, w) not in seen:
                seen.add((k, w))
                all_entries.append((k, w))
        all_categories.extend(categories)
    return all_entries, all_categories

def ensure_skins_white():
    """生成 skins/white/ 下的 preview.png、background.png（白色壁纸）。尺寸：preview 160×80，background 720×320。"""
    white_dir = os.path.join(SKINS_DIR, "white")
    os.makedirs(white_dir, exist_ok=True)
    try:
        from PIL import Image
        Image.new("RGB", (PREVIEW_W, PREVIEW_H), (255, 255, 255)).save(os.path.join(white_dir, "preview.png"))
        Image.new("RGB", (BACKGROUND_W, BACKGROUND_H), (255, 255, 255)).save(os.path.join(white_dir, "background.png"))
        print("已生成 skins/white/preview.png (%d×%d)、background.png (%d×%d)" % (PREVIEW_W, PREVIEW_H, BACKGROUND_W, BACKGROUND_H))
    except ImportError:
        # 无 Pillow 时用最小 1×1 白图（部分环境可能解码失败，建议安装 Pillow：pip install Pillow）
        WHITE_1X1_B64 = "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mP8z8BQDwAEhQGAhKmMIQAAAABJRU5ErkJggg=="
        data = base64.b64decode(WHITE_1X1_B64)
        for name in ("preview.png", "background.png"):
            with open(os.path.join(white_dir, name), "wb") as f:
                f.write(data)
        print("已生成 skins/white 白图（1×1，无 Pillow 时降级）；建议安装 Pillow 后重新运行以生成 %d×%d / %d×%d" % (PREVIEW_W, PREVIEW_H, BACKGROUND_W, BACKGROUND_H))
    # 汇总所有皮肤：以「一个皮肤一个文件夹、文件夹名为皮肤名」扫描 skins/
    list_data = collect_all_skins()
    list_path = os.path.join(SKINS_DIR, "list.json")
    with open(list_path, "w", encoding="utf-8") as f:
        json.dump(list_data, f, ensure_ascii=False, indent=2)
    print("已生成 skins/list.json（共 %d 个皮肤，应用内两列一排展示）" % len(list_data))


def collect_all_skins():
    """扫描 skins 下所有子文件夹，每个子文件夹 = 一个皮肤（文件夹名 = 皮肤名）。"""
    list_data = []
    if not os.path.isdir(SKINS_DIR):
        return list_data
    for name in sorted(os.listdir(SKINS_DIR)):
        if name.startswith("."):
            continue
        skin_dir = os.path.join(SKINS_DIR, name)
        if not os.path.isdir(skin_dir):
            continue
        skin_id = name
        entry = {"id": skin_id, "name": skin_id, "previewUrl": "", "backgroundUrl": ""}
        skin_json_path = os.path.join(skin_dir, "skin.json")
        if os.path.isfile(skin_json_path):
            try:
                with open(skin_json_path, "r", encoding="utf-8") as f:
                    manifest = json.load(f)
                prefix = "skins/" + skin_id + "/"
                entry["name"] = manifest.get("name", skin_id)
                entry["previewUrl"] = (prefix + manifest["previewUrl"]) if manifest.get("previewUrl") else ""
                entry["backgroundUrl"] = (prefix + manifest["backgroundUrl"]) if manifest.get("backgroundUrl") else ""
                entry["skinManifestUrl"] = prefix + "skin.json"
                if os.path.isfile(os.path.join(skin_dir, "intro.json")):
                    entry["introUrl"] = prefix + "intro.json"
                if manifest.get("intro"):
                    entry["intro"] = manifest["intro"]
                if manifest.get("keyAssets"):
                    entry["keyAssets"] = manifest["keyAssets"]
            except Exception:
                pass
        if not entry["previewUrl"] and os.path.isfile(os.path.join(skin_dir, "preview.png")):
            entry["previewUrl"] = "skins/" + skin_id + "/preview.png"
        if not entry["backgroundUrl"] and os.path.isfile(os.path.join(skin_dir, "background.png")):
            entry["backgroundUrl"] = "skins/" + skin_id + "/background.png"
        list_data.append(entry)
    return list_data


def main():
    entries, categories = merge_all_src(SCRIPT_DIR)
    txt_path = os.path.join(SCRIPT_DIR, "wordlist.txt")
    with open(txt_path, "w", encoding="utf-8") as f:
        for key, word in entries:
            f.write(f"{key} {word}\n")
    js_path = os.path.join(SCRIPT_DIR, "wordlist.js")
    with open(js_path, "w", encoding="utf-8") as f:
        f.write("// 萌创匠盒输入法 - 远程词库（由 build_static.py 生成，含分类供 APK 按类推荐）\n")
        data = {
            "lines": [f"{k} {v}" for k, v in entries],
            "categories": categories,
        }
        f.write("var REMOTE_WORDLIST = " + json.dumps(data, ensure_ascii=False, indent=2) + ";\n")
    ensure_skins_white()
    print("已生成 %d 条词库（%d 个分类）-> wordlist.txt、wordlist.js" % (len(entries), len(categories)))
    print("请把本文件夹（萌创匠盒输入法）整体部署到静态托管；APK 拉取后皮肤两列一排展示，点开可看介绍。")
    return 0

if __name__ == "__main__":
    exit(main())
