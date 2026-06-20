"""JSON tabanlı basit kalıcı veri işlemleri."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any


def ensure_directory(path: Path) -> Path:
    """Klasör yoksa oluşturur ve klasör yolunu döndürür."""
    path.mkdir(parents=True, exist_ok=True)
    return path


def read_json(path: Path, default: Any) -> Any:
    """JSON dosyasını okur; dosya yoksa verilen varsayılan değeri döndürür."""
    if not path.exists():
        return default
    with path.open("r", encoding="utf-8") as file:
        return json.load(file)


def write_json(path: Path, data: Any) -> None:
    """Veriyi UTF-8 JSON dosyası olarak kaydeder."""
    ensure_directory(path.parent)
    with path.open("w", encoding="utf-8") as file:
        json.dump(data, file, ensure_ascii=False, indent=4)
