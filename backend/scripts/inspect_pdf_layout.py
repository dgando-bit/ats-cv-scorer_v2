import sys

import pymupdf


def main():
    if len(sys.argv) != 2:
        print("Usage: uv run python scripts/inspect_pdf_layout.py <pdf_file>")
        sys.exit(1)

    file_path = sys.argv[1]

    document = pymupdf.open(file_path)

    for page_number, page in enumerate(document, start=1):
        print("\n" + "=" * 100)
        print(f"PAGE {page_number}")
        print("=" * 100)

        blocks = page.get_text("blocks")

        for index, block in enumerate(blocks):
            x0, y0, x1, y1, text, *_ = block

            text = " ".join(text.split())

            if not text:
                continue

            print(
                f"\nBLOCK {index}"
                f"\n  x0={x0:.1f} y0={y0:.1f}"
                f"\n  x1={x1:.1f} y1={y1:.1f}"
                f"\n  TEXT: {text}"
            )


if __name__ == "__main__":
    main()