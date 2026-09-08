"""Oje Defteri — tek dosya üretici.

src/oje-defteri.html içindeki yer tutucuyu vendor/ altındaki barkod
okuyucuyla değiştirip kök dizine dağıtılabilir oje-defteri.html yazar.
Çalıştırmak için:  python build.py
"""

from pathlib import Path

KOK = Path(__file__).parent
KAYNAK = KOK / "src" / "oje-defteri.html"
KUTUPHANE = KOK / "vendor" / "zxing.min.js"
CIKTI = KOK / "oje-defteri.html"

YER_TUTUCU = "/*__BARKOD_KUTUPHANESI__*/"


SITE = KOK / "site"


def main() -> None:
    html = KAYNAK.read_text(encoding="utf-8")
    if YER_TUTUCU not in html:
        raise SystemExit(f"Yer tutucu bulunamadı: {YER_TUTUCU}")

    kutuphane = KUTUPHANE.read_text(encoding="utf-8")
    html = html.replace(YER_TUTUCU, kutuphane)

    boyut = len(html.encode("utf-8")) / 1024

    # 1) Telefona doğrudan atılabilen tek dosya
    CIKTI.write_text(html, encoding="utf-8")
    print(f"{CIKTI.name} yazıldı — {boyut:.0f} KB")

    # 2) Web adresine konacak sürüm (manifest ve ikonlar site/ içinde durur)
    SITE.mkdir(exist_ok=True)
    (SITE / "index.html").write_text(html, encoding="utf-8")
    print(f"site/index.html yazıldı — {boyut:.0f} KB")


if __name__ == "__main__":
    main()
