from pathlib import Path
import tempfile
import unittest

from basari_hesaplama_arayuzu.storage import read_json, write_json


class StorageTest(unittest.TestCase):
    def test_json_roundtrip(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            path = Path(temp_dir) / "data.json"
            write_json(path, [{"Ders Kodu": "YZM"}])
            self.assertEqual(read_json(path, []), [{"Ders Kodu": "YZM"}])

    def test_missing_json_returns_default(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            self.assertEqual(read_json(Path(temp_dir) / "missing.json", []), [])


if __name__ == "__main__":
    unittest.main()
