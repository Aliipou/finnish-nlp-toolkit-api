"""
Download and setup required NLP models and data

This script downloads:
1. UDPipe Finnish model
2. spaCy Finnish model
3. Sample Finnish text corpus
"""
import os
import urllib.request
import sys
from pathlib import Path

def download_file(url: str, dest: str):
    """Download file with progress"""
    print(f"Downloading from {url}")
    print(f"Saving to {dest}")

    def progress(count, block_size, total_size):
        percent = int(count * block_size * 100 / total_size)
        sys.stdout.write(f"\r{percent}% ")
        sys.stdout.flush()

    urllib.request.urlretrieve(url, dest, progress)
    print("\n[OK] Download complete")


def setup_directories():
    """Create necessary directories"""
    dirs = [
        "data/models",
        "data/corpus",
        "data/datasets",
        "data/cache"
    ]

    for dir_path in dirs:
        Path(dir_path).mkdir(parents=True, exist_ok=True)
        print(f"[OK] Created directory: {dir_path}")


def download_udpipe_model():
    """Download Finnish UDPipe model"""
    model_url = "https://lindat.mff.cuni.cz/repository/xmlui/bitstream/handle/11234/1-3131/finnish-tdt-ud-2.5-191206.udpipe"
    model_path = "data/models/finnish-tdt-ud-2.5-191206.udpipe"

    if os.path.exists(model_path):
        print(f"[SKIP] UDPipe model already exists at {model_path}")
        return

    print("\n[INFO] Downloading UDPipe Finnish model...")
    try:
        download_file(model_url, model_path)
    except Exception as e:
        print(f"[ERROR] Failed to download UDPipe model: {e}")
        print("Please download manually from:")
        print("https://lindat.mff.cuni.cz/repository/xmlui/handle/11234/1-3131")


def download_spacy_model():
    """Download spaCy Finnish model"""
    print("\n[INFO] Downloading spaCy Finnish model...")
    print("Running: python -m spacy download fi_core_news_sm")

    import subprocess
    try:
        subprocess.run([sys.executable, "-m", "spacy", "download", "fi_core_news_sm"], check=True)
        print("[OK] spaCy model installed")
    except subprocess.CalledProcessError as e:
        print(f"[ERROR] Failed to install spaCy model: {e}")
        print("Try manually: python -m spacy download fi_core_news_sm")
    except FileNotFoundError:
        print("[ERROR] spaCy not installed")
        print("Install with: pip install spacy")


def install_voikko():
    """Instructions for installing Voikko"""
    print("\n[INFO] Voikko Installation Instructions:")
    print("=" * 60)
    print("Voikko requires system-level installation:")
    print()
    print("Ubuntu/Debian:")
    print("  sudo apt-get install libvoikko1 voikko-fi")
    print("  pip install libvoikko")
    print()
    print("macOS:")
    print("  brew install libvoikko")
    print("  pip install libvoikko")
    print()
    print("Windows:")
    print("  Download from: https://voikko.puimula.org/")
    print("  Install libvoikko DLL")
    print("  pip install libvoikko")
    print("=" * 60)


def download_sample_corpus():
    """Download sample Finnish text corpus"""
    print("\n[INFO] Creating sample Finnish corpus...")

    corpus_path = "data/corpus/sample_finnish.txt"

    sample_texts = """
Kissa istui ikkunalaudalla ja katseli ulos.
Aurinko paistoi kirkkaasti taivaalla.
Lapset leikkivät puistossa iloisesti.
Koira juoksi nopeasti puutarhassa.
Talo oli vanha ja kaunis.
Kirja oli hyvin mielenkiintoinen.
Opettaja selitti oppilaille uuden asian.
Auto pysähtyi liikennevaloihin.
Lintu lauloi oksalla kauniisti.
Kukka kukkii kesällä värikkäänä.
"""

    with open(corpus_path, 'w', encoding='utf-8') as f:
        f.write(sample_texts.strip())

    print(f"[OK] Sample corpus created at {corpus_path}")


def main():
    """Main setup function"""
    print("=" * 60)
    print("Finnish NLP Toolkit - Model Download Script")
    print("=" * 60)

    # Create directories
    print("\n1. Setting up directories...")
    setup_directories()

    # Download UDPipe model
    print("\n2. Setting up UDPipe...")
    download_udpipe_model()

    # Download spaCy model
    print("\n3. Setting up spaCy...")
    download_spacy_model()

    # Voikko instructions
    print("\n4. Voikko setup...")
    install_voikko()

    # Sample corpus
    print("\n5. Setting up sample corpus...")
    download_sample_corpus()

    print("\n" + "=" * 60)
    print("[SUCCESS] Setup complete!")
    print("=" * 60)
    print("\nNext steps:")
    print("1. Install Voikko (see instructions above)")
    print("2. Run tests: pytest app/tests/")
    print("3. Start API: uvicorn app.main:app --reload")
    print("=" * 60)


if __name__ == "__main__":
    main()
