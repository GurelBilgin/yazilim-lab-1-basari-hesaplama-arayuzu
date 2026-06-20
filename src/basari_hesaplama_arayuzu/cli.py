"""Komut satırı arayüzü."""

from __future__ import annotations

import argparse
from pathlib import Path

from .app import create_app
from .excel_utils import create_outputs


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Başarı hesaplama arayüzü")
    subparsers = parser.add_subparsers(dest="command")

    web_parser = subparsers.add_parser("web", help="Flask web arayüzünü başlatır")
    web_parser.add_argument("--host", default="127.0.0.1")
    web_parser.add_argument("--port", type=int, default=5000)
    web_parser.add_argument("--debug", action="store_true")

    calc_parser = subparsers.add_parser("hesapla", help="Örnek Excel dosyalarından çıktı üretir")
    calc_parser.add_argument("--tablo2", default="data/tablo2.xlsx")
    calc_parser.add_argument("--not-tablosu", default="data/not_tablosu.xlsx")
    calc_parser.add_argument("--output-dir", default="outputs")
    calc_parser.add_argument("--od1", type=float, required=True)
    calc_parser.add_argument("--od2", type=float, required=True)
    calc_parser.add_argument("--quiz", type=float, required=True)
    calc_parser.add_argument("--vize", type=float, required=True)
    calc_parser.add_argument("--fin", type=float, required=True)
    return parser


def main(argv: list[str] | None = None) -> None:
    parser = build_parser()
    args = parser.parse_args(argv)

    if args.command in (None, "web"):
        app = create_app(Path.cwd())
        app.run(host=getattr(args, "host", "127.0.0.1"), port=getattr(args, "port", 5000), debug=getattr(args, "debug", False))
        return

    if args.command == "hesapla":
        percentages = {"Öd1": args.od1, "Öd2": args.od2, "Quiz": args.quiz, "Vize": args.vize, "Fin": args.fin}
        tablo3_path, tablo4_path = create_outputs(args.tablo2, args.not_tablosu, args.output_dir, percentages)
        print(f"Tablo 3 oluşturuldu: {tablo3_path}")
        print(f"Tablo 4 oluşturuldu: {tablo4_path}")
        return

    parser.error("Bilinmeyen komut")


if __name__ == "__main__":
    main()
