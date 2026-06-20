"""Excel okuma, doğrulama ve başarı hesaplama yardımcıları."""

from __future__ import annotations

from pathlib import Path
from typing import Mapping

import pandas as pd

GRADE_COLUMNS = ["Öd1", "Öd2", "Quiz", "Vize", "Fin"]


def read_excel(path: str | Path) -> pd.DataFrame:
    """Excel dosyasını DataFrame olarak okur."""
    return pd.read_excel(path)


def dataframe_to_html(df: pd.DataFrame) -> str:
    """DataFrame'i Bootstrap uyumlu HTML tabloya dönüştürür."""
    return df.to_html(classes="table table-bordered table-striped", index=False)


def validate_numeric_values_between_zero_and_one(df: pd.DataFrame) -> bool:
    """DataFrame içindeki sayısal değerlerin 0 ile 1 aralığında olup olmadığını kontrol eder."""
    numeric_df = df.select_dtypes(include="number")
    if numeric_df.empty:
        return False
    return bool(((numeric_df >= 0) & (numeric_df <= 1)).all().all())


def normalize_percentages(percentages: Mapping[str, float]) -> dict[str, float]:
    """Yüzde değerlerini 0-1 katsayılarına dönüştürür ve toplamın 100 olduğunu doğrular."""
    missing = [column for column in GRADE_COLUMNS if column not in percentages]
    if missing:
        raise ValueError(f"Eksik yüzde alanları: {', '.join(missing)}")

    values = {column: float(percentages[column]) for column in GRADE_COLUMNS}
    total = sum(values.values())
    if round(total, 6) != 100:
        raise ValueError("Yüzde değerlerinin toplamı 100 olmalıdır.")
    return {column: value / 100 for column, value in values.items()}


def generate_table3(tablo2_df: pd.DataFrame, percentage_weights: Mapping[str, float]) -> pd.DataFrame:
    """Tablo 2 ve değerlendirme ağırlıklarından Tablo 3 çıktısını üretir."""
    normalized = normalize_percentages(percentage_weights)
    expected_columns = ["Ders Çıktı", *GRADE_COLUMNS]
    tablo2 = tablo2_df.iloc[:, : len(expected_columns)].copy()
    tablo2.columns = expected_columns

    output = pd.DataFrame()
    output["Ders Çıktı"] = tablo2["Ders Çıktı"]
    for column in GRADE_COLUMNS:
        output[column] = tablo2[column].astype(float) * normalized[column]
    output["Toplam"] = output[GRADE_COLUMNS].sum(axis=1)
    return output


def calculate_student_success_table(tablo3_df: pd.DataFrame, grades_df: pd.DataFrame) -> dict[str, pd.DataFrame]:
    """Her öğrenci için ders çıktısı bazında başarı tablosu üretir."""
    results: dict[str, pd.DataFrame] = {}
    for _, student in grades_df.iterrows():
        student_no = str(student["Öğrenci_No"])
        rows = []
        for _, outcome in tablo3_df.iterrows():
            row = {"Ders Çıktı": outcome["Ders Çıktı"]}
            total = 0.0
            maximum = 0.0
            for column in GRADE_COLUMNS:
                weight = float(outcome[column])
                score = float(student[column])
                weighted_score = score * weight
                row[column] = weighted_score
                total += weighted_score
                maximum += 100 * weight
            row["Toplam"] = total
            row["Max"] = maximum
            row["%Başarı"] = 0 if maximum == 0 else (total / maximum) * 100
            rows.append(row)
        results[student_no] = pd.DataFrame(rows)
    return results


def write_table4_single_sheet(results: Mapping[str, pd.DataFrame], output_path: str | Path) -> Path:
    """Öğrenci başarı tablolarını tek Excel sayfasında bloklar hâlinde kaydeder."""
    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with pd.ExcelWriter(output_path, engine="xlsxwriter") as writer:
        workbook = writer.book
        worksheet = workbook.add_worksheet("Tablo4")
        writer.sheets["Tablo4"] = worksheet

        header_format = workbook.add_format({"bold": True, "align": "center", "border": 1})
        title_format = workbook.add_format({"bold": True, "font_size": 12})
        cell_format = workbook.add_format({"border": 1, "align": "center"})

        current_row = 0
        for student_no, df in results.items():
            worksheet.write(current_row, 0, f"Öğrenci No: {student_no}", title_format)
            current_row += 1
            for col_index, header in enumerate(df.columns):
                worksheet.write(current_row, col_index, header, header_format)
            current_row += 1
            for _, row in df.iterrows():
                for col_index, value in enumerate(row):
                    worksheet.write(current_row, col_index, value, cell_format)
                current_row += 1
            current_row += 2
    return output_path


def create_outputs(
    tablo2_path: str | Path,
    grades_path: str | Path,
    output_dir: str | Path,
    percentages: Mapping[str, float],
) -> tuple[Path, Path]:
    """Tablo 3 ve Tablo 4 çıktı dosyalarını oluşturur."""
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    tablo2_df = pd.read_excel(tablo2_path)
    grades_df = pd.read_excel(grades_path)
    tablo3_df = generate_table3(tablo2_df, percentages)
    tablo3_path = output_dir / "Tablo3_Output.xlsx"
    tablo3_df.to_excel(tablo3_path, index=False)

    results = calculate_student_success_table(tablo3_df, grades_df)
    tablo4_path = write_table4_single_sheet(results, output_dir / "Tablo4_Output.xlsx")
    return tablo3_path, tablo4_path
