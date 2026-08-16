import sys

from app.services.layout_extractor import LayoutExtractor


def main():
    if len(sys.argv) != 2:
        print("Usage: uv run python scripts/run_layout.py <cv_file>")
        sys.exit(1)

    file_path = sys.argv[1]

    extractor = LayoutExtractor()
    blocks = extractor.extract(file_path)

    print("=" * 100)
    print("PDF LAYOUT")
    print("=" * 100)

    for block in blocks:
        print(
            f"\nPAGE={block.page}"
            f" | x={block.x0:.1f}"
            f" | y={block.y0:.1f}"
            f" | center_x={block.center_x:.1f}"
            f"\n  {block.text}"
        )


if __name__ == "__main__":
    main()