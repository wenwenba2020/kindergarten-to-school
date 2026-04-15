#!/usr/bin/env python3
"""
生成小程序 tabBar 图标，通过 ComfyUI API（z-image-turbo 模型）
用法: python3 scripts/gen_icons.py [--ckpt MODEL_NAME]
"""
import argparse
import json
import os
import time
import urllib.request
import urllib.error

try:
    from PIL import Image
except ImportError:
    print("请先安装 Pillow: pip install Pillow")
    raise

# === 配置 ===
COMFY_URL = "http://100.90.137.80:8188"
OUTPUT_DIR = "miniprogram/images"
ICON_SIZE = 81  # 微信 tabBar 最佳尺寸

ICONS = [
    {
        "name": "tab-home",
        "prompt": "cute flat icon, tiny house with green roof and round chimney, kawaii style, bold black outline, white background, vibrant colors, simple shape, children app icon, no text, centered composition, 2D illustration",
    },
    {
        "name": "tab-assess",
        "prompt": "cute flat icon, clipboard with orange star sticker on it, kawaii style, bold black outline, white background, vibrant colors, simple shape, children app icon, no text, centered composition, 2D illustration",
    },
    {
        "name": "tab-plan",
        "prompt": "cute flat icon, calendar page with yellow sun drawing on it, kawaii style, bold black outline, white background, vibrant colors, simple shape, children app icon, no text, centered composition, 2D illustration",
    },
    {
        "name": "tab-chat",
        "prompt": "cute flat icon, round speech bubble with purple heart inside, kawaii style, bold black outline, white background, vibrant colors, simple shape, children app icon, no text, centered composition, 2D illustration",
    },
]


def build_workflow(prompt_text: str, ckpt_name: str, seed: int) -> dict:
    """
    Build ComfyUI workflow for z-image-turbo using Nunchaku loader.
    Architecture:
      NunchakuZImageDiTLoader -> MODEL
      CLIPLoader (qwen_image) -> CLIP
      VAELoader (ae.safetensors) -> VAE
      TextEncodeZImageOmni (CLIP + prompt) -> CONDITIONING (positive)
      EmptyLatentImage -> LATENT
      KSampler -> LATENT
      VAEDecode -> IMAGE
      SaveImage -> output
    """
    return {
        "prompt": {
            "1": {
                "class_type": "NunchakuZImageDiTLoader",
                "inputs": {"model_name": ckpt_name},
            },
            "2": {
                "class_type": "CLIPLoader",
                "inputs": {
                    "clip_name": "qwen3_4b_fp8_scaled.safetensors",
                    "type": "qwen_image",
                },
            },
            "3": {
                "class_type": "VAELoader",
                "inputs": {"vae_name": "ae.safetensors"},
            },
            "4": {
                "class_type": "TextEncodeZImageOmni",
                "inputs": {
                    "clip": ["2", 0],
                    "prompt": prompt_text,
                    "auto_resize_images": True,
                },
            },
            "5": {
                "class_type": "EmptyLatentImage",
                "inputs": {"batch_size": 1, "height": 512, "width": 512},
            },
            "6": {
                "class_type": "KSampler",
                "inputs": {
                    "cfg": 1.0,
                    "denoise": 1,
                    "latent_image": ["5", 0],
                    "model": ["1", 0],
                    "negative": ["4", 0],
                    "positive": ["4", 0],
                    "sampler_name": "euler",
                    "scheduler": "simple",
                    "seed": seed,
                    "steps": 4,
                },
            },
            "7": {
                "class_type": "VAEDecode",
                "inputs": {"samples": ["6", 0], "vae": ["3", 0]},
            },
            "8": {
                "class_type": "SaveImage",
                "inputs": {
                    "filename_prefix": "tabicon",
                    "images": ["7", 0],
                },
            },
        }
    }


def post_prompt(workflow: dict) -> str:
    data = json.dumps(workflow).encode("utf-8")
    req = urllib.request.Request(
        f"{COMFY_URL}/prompt",
        data=data,
        headers={"Content-Type": "application/json"},
    )
    with urllib.request.urlopen(req, timeout=30) as resp:
        result = json.loads(resp.read())
    return result["prompt_id"]


def wait_for_completion(prompt_id: str, timeout: int = 300) -> dict:
    start = time.time()
    while time.time() - start < timeout:
        with urllib.request.urlopen(f"{COMFY_URL}/history/{prompt_id}", timeout=10) as resp:
            history = json.loads(resp.read())
        if prompt_id in history:
            return history[prompt_id]
        time.sleep(2)
    raise TimeoutError(f"ComfyUI did not finish in {timeout}s")


def download_image(filename: str, subfolder: str = "") -> bytes:
    url = f"{COMFY_URL}/view?filename={filename}&subfolder={subfolder}&type=output"
    with urllib.request.urlopen(url, timeout=30) as resp:
        return resp.read()


def save_icon(img_bytes: bytes, out_path: str):
    from io import BytesIO
    img = Image.open(BytesIO(img_bytes)).convert("RGBA")
    # 填充白色背景（微信 tabBar 不支持透明）
    bg = Image.new("RGBA", img.size, (255, 255, 255, 255))
    bg.paste(img, mask=img.split()[3])
    bg = bg.convert("RGB")
    bg = bg.resize((ICON_SIZE, ICON_SIZE), Image.LANCZOS)
    bg.save(out_path, "PNG", optimize=True)
    size_kb = os.path.getsize(out_path) / 1024
    print(f"  Saved: {out_path} ({size_kb:.1f} KB)")
    if size_kb > 40:
        print(f"  WARNING: file > 40KB, WeChat may reject it")


def make_grayscale(color_path: str, gray_path: str):
    img = Image.open(color_path).convert("RGB")
    gray = img.convert("L").convert("RGB")
    gray.save(gray_path, "PNG", optimize=True)
    print(f"  Gray: {gray_path}")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--ckpt", default="svdq-int4_r256-z-image-turbo.safetensors",
                        help="ComfyUI z-image model name (exact filename in diffusion_models/)")
    args = parser.parse_args()

    os.makedirs(OUTPUT_DIR, exist_ok=True)

    for i, icon in enumerate(ICONS):
        print(f"\n[{i+1}/{len(ICONS)}] Generating {icon['name']}...")
        workflow = build_workflow(icon["prompt"], args.ckpt, seed=42 + i * 100)

        try:
            prompt_id = post_prompt(workflow)
        except Exception as e:
            print(f"  ERROR posting prompt: {e}")
            continue

        print(f"  prompt_id: {prompt_id}, waiting...")

        try:
            history = wait_for_completion(prompt_id)
        except TimeoutError as e:
            print(f"  ERROR: {e}")
            continue

        outputs = history["outputs"]

        # 找到 SaveImage 节点的输出
        img_info = None
        for node_id, node_out in outputs.items():
            if "images" in node_out:
                img_info = node_out["images"][0]
                break

        if not img_info:
            print(f"  ERROR: no image output found, history status: {history.get('status', {})}")
            continue

        try:
            img_bytes = download_image(img_info["filename"], img_info.get("subfolder", ""))
        except Exception as e:
            print(f"  ERROR downloading image: {e}")
            continue

        active_path = os.path.join(OUTPUT_DIR, f"{icon['name']}-active.png")
        default_path = os.path.join(OUTPUT_DIR, f"{icon['name']}.png")

        save_icon(img_bytes, active_path)
        make_grayscale(active_path, default_path)

    print("\nDone! All icons saved to", OUTPUT_DIR)


if __name__ == "__main__":
    main()
