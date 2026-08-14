# from app.services.layout_extractor import LayoutExtractor
#
#
# PDF_PATH = "data/samples/cv_test.pdf"
#
#
# extractor = LayoutExtractor()
#
# blocks = LayoutExtractor().extract(PDF_PATH)
#
# for block in blocks:
#     print(
#         f"x={block.x0:6.1f} "
#         f"center_x={block.center_x:6.1f} "
#         f"y={block.y0:6.1f} "
#         f"center_y={block.center_y:6.1f} "
#         f"| {block.text!r}"
#     )
import pymupdf

PDF_PATH = "data/samples/cv_test_2.pdf"

with pymupdf.open(PDF_PATH) as document:
    page = document[0]

    print("=== get_text('blocks') ===")

    for i, block in enumerate(page.get_text("blocks")):
        x0, y0, x1, y1, text, *_ = block

        print(
            f"{i:02d} | "
            f"x0={x0:6.1f} "
            f"y0={y0:6.1f} "
            f"x1={x1:6.1f} "
            f"y1={y1:6.1f} | "
            f"{text.strip()!r}"
        )

    print("\n=== get_text('dict') ===")

    data = page.get_text("dict")

    for block in data["blocks"]:
        if "lines" not in block:
            continue

        text = " ".join(
            span["text"]
            for line in block["lines"]
            for span in line["spans"]
        ).strip()

        if not text:
            continue

        print(
            f"x0={block['bbox'][0]:6.1f} "
            f"y0={block['bbox'][1]:6.1f} "
            f"| {text!r}"
        )