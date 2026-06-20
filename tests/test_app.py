import tempfile
import unittest

from basari_hesaplama_arayuzu import create_app


class AppTest(unittest.TestCase):
    def test_index_loads(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            app = create_app(temp_dir)
            app.config.update(TESTING=True)
            response = app.test_client().get("/")
            self.assertEqual(response.status_code, 200)
            self.assertIn("ÖĞRENCİ BİLGİ SİSTEMİ".encode("utf-8"), response.data)


if __name__ == "__main__":
    unittest.main()
