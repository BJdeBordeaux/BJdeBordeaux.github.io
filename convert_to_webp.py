#!/usr/bin/env python3
"""
图片转 WebP 格式脚本
用法: python3 convert_to_webp.py <输入图片路径> [输出目录]
- 输入: 支持 jpg/jpeg/png 等常见格式
- 输出: 默认存到 images/moments/ 目录，格式为 WebP
"""

import sys
import os
from pathlib import Path
from PIL import Image

def convert_to_webp(src_path: str, dst_dir: str = None) -> str:
    """将图片转换为 WebP 格式"""
    src_path = Path(src_path)
    if not src_path.exists():
        raise FileNotFoundError(f"文件不存在: {src_path}")

    # 默认输出目录
    if dst_dir is None:
        dst_dir = src_path.parent.parent / "images" / "moments"
    else:
        dst_dir = Path(dst_dir)

    dst_dir.mkdir(parents=True, exist_ok=True)

    # 生成输出文件名（保持原名，仅换扩展名）
    dst_name = src_path.stem + ".webp"
    dst_path = dst_dir / dst_name

    # 转换
    img = Image.open(src_path)
    if img.mode in ('RGBA', 'P'):
        img = img.convert('RGB')
    img.save(dst_path, 'WEBP', quality=85, method=6)

    # 输出信息
    src_size = src_path.stat().st_size
    dst_size = dst_path.stat().st_size
    print(f"✓ {src_path.name} -> {dst_path.name}")
    print(f"  {src_size/1024:.1f}KB -> {dst_size/1024:.1f}KB (压缩 {100*(1-dst_size/src_size):.1f}%)")

    return str(dst_path)


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print(__doc__)
        sys.exit(1)

    src = sys.argv[1]
    dst = sys.argv[2] if len(sys.argv) > 2 else None

    try:
        convert_to_webp(src, dst)
    except Exception as e:
        print(f"错误: {e}", file=sys.stderr)
        sys.exit(1)