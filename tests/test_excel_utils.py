from pathlib import Path
import tempfile
import unittest

import pandas as pd

from basari_hesaplama_arayuzu.excel_utils import (
    calculate_student_success_table,
    generate_table3,
    normalize_percentages,
    validate_numeric_values_between_zero_and_one,
    write_table4_single_sheet,
)


class ExcelUtilsTest(unittest.TestCase):
    def test_normalize_percentages(self):
        result = normalize_percentages({"Öd1": 10, "Öd2": 10, "Quiz": 10, "Vize": 30, "Fin": 40})
        self.assertEqual(result["Fin"], 0.4)

    def test_normalize_percentages_rejects_invalid_total(self):
        with self.assertRaises(ValueError):
            normalize_percentages({"Öd1": 10, "Öd2": 10, "Quiz": 10, "Vize": 10, "Fin": 10})

    def test_generate_table3(self):
        df = pd.DataFrame({
            "Ders Çıktı": ["Ç1"],
            "Öd1": [1],
            "Öd2": [0],
            "Quiz": [1],
            "Vize": [0],
            "Fin": [1],
        })
        result = generate_table3(df, {"Öd1": 10, "Öd2": 10, "Quiz": 10, "Vize": 30, "Fin": 40})
        self.assertAlmostEqual(result.loc[0, "Toplam"], 0.6)

    def test_student_success_table(self):
        tablo3 = pd.DataFrame({
            "Ders Çıktı": ["Ç1"],
            "Öd1": [0.1],
            "Öd2": [0.0],
            "Quiz": [0.1],
            "Vize": [0.0],
            "Fin": [0.4],
            "Toplam": [0.6],
        })
        grades = pd.DataFrame({
            "Öğrenci_No": ["1"],
            "Öd1": [100],
            "Öd2": [50],
            "Quiz": [80],
            "Vize": [90],
            "Fin": [70],
        })
        result = calculate_student_success_table(tablo3, grades)["1"]
        self.assertAlmostEqual(result.loc[0, "Toplam"], 46)
        self.assertAlmostEqual(result.loc[0, "Max"], 60)

    def test_range_validation(self):
        self.assertTrue(validate_numeric_values_between_zero_and_one(pd.DataFrame({"A": [0, 0.5, 1]})))
        self.assertFalse(validate_numeric_values_between_zero_and_one(pd.DataFrame({"A": [0, 2]})))

    def test_write_table4(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            path = Path(temp_dir) / "Tablo4_Output.xlsx"
            write_table4_single_sheet({"1": pd.DataFrame({"Ders Çıktı": ["Ç1"], "Toplam": [80]})}, path)
            self.assertTrue(path.exists())


if __name__ == "__main__":
    unittest.main()
