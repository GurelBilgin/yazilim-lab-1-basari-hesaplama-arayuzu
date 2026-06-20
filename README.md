# Başarı Hesaplama Arayüz Projesi

Bu proje, ders ve öğrenci verilerini Excel dosyaları üzerinden yönetmek için geliştirilmiş Flask tabanlı bir web uygulamasıdır. Uygulama; ders ekleme, öğrenci listesi yükleme, program çıktısı yükleme, ders bazlı tabloları görüntüleme, not tablosu yükleme ve ders çıktısı başarı hesaplamaları için temel bir arayüz sunar.

Proje ilk hâlinde tek dosyalı bir yapıdaydı. Güncel sürümde kodlar modüler hâle getirilmiş, proje klasör yapısı düzenlenmiş, örnek veri dosyaları ayrılmış ve hesaplama fonksiyonları test edilebilir şekilde yeniden yapılandırılmıştır.

## Özellikler

- Flask tabanlı web arayüzü
- Ders ekleme, listeleme ve silme
- Öğrenci listesi Excel dosyası yükleme
- Program çıktıları Excel dosyası yükleme
- Ders bazlı öğrenme çıktısı yükleme
- Tablo 1, Tablo 2, Tablo 3, Tablo 4 ve Tablo 5 dosyalarını ders bazlı görüntüleme
- Not tablosu yükleme ve Excel olarak indirme
- Excel dosyaları üzerinden ders çıktısı başarı hesaplama altyapısı
- Komut satırı üzerinden örnek çıktı üretme
- Modüler ve test edilebilir Python proje yapısı

## Proje Yapısı

```text
basari-hesaplama-arayuzu/
├── README.md
├── pyproject.toml
├── .gitignore
├── data/
│   ├── not_tablosu.xlsx
│   ├── tablo1.xlsx
│   ├── tablo2.xlsx
│   ├── ogrenci_listesi.xlsx
│   ├── ogrenme_ciktilari.xlsx
│   └── program_ciktilari.xlsx
├── src/
│   └── basari_hesaplama_arayuzu/
│       ├── __init__.py
│       ├── app.py
│       ├── cli.py
│       ├── excel_utils.py
│       ├── storage.py
│       ├── templates/
│       └── static/
├── tests/
│   ├── test_excel_utils.py
│   └── test_storage.py
└── uploads/
    └── .gitkeep
```

## Kullanılan Teknolojiler

- Python
- Flask
- pandas
- openpyxl
- xlsxwriter
- Bootstrap
- unittest

## Kurulum

Python 3.10 veya üzeri önerilir.

```bash
python -m pip install -e .
```

## Web Arayüzünü Çalıştırma

Proje ana klasöründe aşağıdaki komut çalıştırılır:

```bash
python -m basari_hesaplama_arayuzu.app
```

veya paket kurulumu sonrasında:

```bash
basari-hesaplama-arayuzu web
```

Uygulama varsayılan olarak şu adreste açılır:

```text
http://127.0.0.1:5000
```

## Komut Satırı ile Örnek Çıktı Üretme

Aşağıdaki komut, `data/` klasöründeki örnek Excel dosyalarını kullanarak `outputs/` klasörü içinde çıktı dosyaları üretir:

```bash
basari-hesaplama-arayuzu hesapla --od1 10 --od2 10 --quiz 10 --vize 30 --fin 40
```

Alternatif olarak Python modülü üzerinden çalıştırılabilir:

```bash
python -m basari_hesaplama_arayuzu.cli hesapla --od1 10 --od2 10 --quiz 10 --vize 30 --fin 40
```

## Giriş Dosyaları

Örnek giriş dosyaları `data/` klasöründe bulunur:

```text
data/tablo1.xlsx
data/tablo2.xlsx
data/not_tablosu.xlsx
data/ogrenci_listesi.xlsx
data/ogrenme_ciktilari.xlsx
data/program_ciktilari.xlsx
```

## Çıktı Dosyaları

Komut satırıyla hesaplama yapıldığında çıktılar `outputs/` klasörüne yazılır:

```text
outputs/Tablo3_Output.xlsx
outputs/Tablo4_Output.xlsx
```

`Tablo3_Output.xlsx`, ders çıktılarının değerlendirme yüzdelerine göre ağırlıklandırılmış hâlini içerir.

`Tablo4_Output.xlsx`, her öğrenci için ders çıktısı bazında başarı yüzdesini gösterir.

## Testler

Testleri çalıştırmak için:

```bash
python -m unittest discover -s tests -v
```

## Geliştirme Notları

- `.idea/`, `__pycache__/` ve çalışma sırasında oluşan dosyalar repodan çıkarılmıştır.
- Yüklenen dosyalar `uploads/` klasöründe tutulur ancak GitHub’a yüklenmez.
- Uygulamanın çalışma verileri `storage/` klasöründe oluşturulur ve repoya dahil edilmez.
- Örnek Excel dosyaları `data/` klasöründe tutulur.

## Hazırlayanlar

- Gürel BİLGİN
- Gizem YALÇIN
- Yerdinat ALİKHAN
- Berkay ARAS
