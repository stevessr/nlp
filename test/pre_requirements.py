import nltk
from nltk.downloader import (
    Downloader,
    ProgressMessage,
    StartPackageMessage,
    FinishPackageMessage,
    ErrorMessage,
)
from tqdm import tqdm

packages = [
    "punkt",
    "punkt_tab",
    "stopwords",
    "wordnet",
    "omw-1.4",
]

dl = Downloader()

for package in packages:
    print(f"\nDownloading: {package}")

    bar = tqdm(
        total=100,
        desc=package,
        unit="%",
        bar_format="{l_bar}{bar}| {n:.0f}/{total:.0f}%"
    )

    last = 0

    for msg in dl.incr_download(package):
        if isinstance(msg, ProgressMessage):
            current = msg.progress
            bar.update(max(0, current - last))
            last = current

        elif isinstance(msg, ErrorMessage):
            bar.close()
            raise RuntimeError(f"{package}: {msg.message}")

    if last < 100:
        bar.update(100 - last)

    bar.close()

print("\n✓ All NLTK data downloaded.")