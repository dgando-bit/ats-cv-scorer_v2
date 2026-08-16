import sys

from app.services.layout_analyzer import LayoutAnalyzer
from app.services.layout_extractor import LayoutExtractor


def main():
    if len(sys.argv) != 2:
        print(
            "Usage: "
            "uv run python scripts/run_layout_analyzer.py <cv_file>"
        )
        sys.exit(1)

    file_path = sys.argv[1]

    extractor = LayoutExtractor()
    blocks = extractor.extract(file_path)

    analyzer = LayoutAnalyzer()
    columns = analyzer.analyze(blocks)

    for column_name, column in columns.items():

        print("\n" + "=" * 100)
        print(column_name.upper())
        print("=" * 100)

        for block in column.blocks:
            print(
                f"y={block.y0:7.1f} "
                f"x={block.x0:7.1f} "
                f"| {block.text}"
            )


if __name__ == "__main__":
    main()