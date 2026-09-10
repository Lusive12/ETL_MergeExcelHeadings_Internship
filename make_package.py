"""
make_package.py - Script Otomatis Pembuat Paket Distribusi Monthly HR Report

Cara menjalankan:
  .venv\\Scripts\\python.exe make_package.py
"""
import os
import shutil
import pathlib
import zipfile

def build_package():
    root = pathlib.Path(__file__).resolve().parent
    # Jika dijalankan dari folder Monthly HR Report Automation atau ETL Group
    if not (root / "dist").exists() and (root.parent / "Monthly HR Report Automation").exists():
        root = root.parent / "Monthly HR Report Automation"

    dist_pkg = root / "dist" / "Monthly_HR_Automation_Package"

    print("[1/5] Menyiapkan folder paket distribusi...")
    if dist_pkg.exists():
        shutil.rmtree(dist_pkg)
    dist_pkg.mkdir(parents=True, exist_ok=True)

    print("[2/5] Menyalin hasil kompilasi PyInstaller (_internal & .exe)...")
    src_dist = root / "dist" / "Run_HR_Automation"
    if not src_dist.exists():
        print(f"ERROR: Folder {src_dist} tidak ditemukan!")
        print("Jalankan kompilasi terlebih dahulu: .venv\\Scripts\\pyinstaller --noconfirm Run_HR_Automation.spec")
        return

    for item in src_dist.iterdir():
        dest = dist_pkg / item.name
        if item.is_dir():
            shutil.copytree(item, dest)
        else:
            shutil.copy2(item, dest)

    print("[3/5] Menyalin folder config dan input...")
    shutil.copytree(root / "config", dist_pkg / "config")
    shutil.copytree(root / "input", dist_pkg / "input")

    # Bersihkan file temporer Excel (~$*)
    for temp_file in dist_pkg.glob("input/**/~$*"):
        try:
            temp_file.unlink()
        except Exception:
            pass

    print("[4/5] Membuat folder output/ dan logs/ kosong...")
    (dist_pkg / "output").mkdir(exist_ok=True)
    (dist_pkg / "logs").mkdir(exist_ok=True)

    # Launcher batch script
    bat_content = "@echo off\r\ncd /d \"%~dp0\"\r\ntitle Monthly HR Report Automation\r\nRun_HR_Automation.exe\r\npause\r\n"
    (dist_pkg / "RUN_ME.bat").write_text(bat_content, encoding="utf-8")

    print("[5/5] Mengompres folder menjadi file ZIP siap kirim...")
    zip_path = root / "dist" / "Monthly_HR_Automation_Package.zip"
    if zip_path.exists():
        zip_path.unlink()

    with zipfile.ZipFile(zip_path, "w", compression=zipfile.ZIP_DEFLATED, compresslevel=9) as zipf:
        for file_path in dist_pkg.rglob("*"):
            archive_name = file_path.relative_to(dist_pkg.parent)
            zipf.write(file_path, archive_name)

    size_mb = zip_path.stat().st_size / (1024 * 1024)
    print("=" * 60)
    print("BERHASIL DIBUAT!")
    print(f"Folder Paket : {dist_pkg}")
    print(f"File ZIP     : {zip_path} ({size_mb:.2f} MB)")
    print("=" * 60)

if __name__ == "__main__":
    build_package()
