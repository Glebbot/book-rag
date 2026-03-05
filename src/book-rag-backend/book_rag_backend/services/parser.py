import pdfplumber
import pandas as pd
import io
from tabulate import tabulate


class ParserService:

    def __init__(self):
        pass

    def parse_pdf(self, file_bytes: bytes) -> str:
        pages_text = []
        with pdfplumber.open(io.BytesIO(file_bytes)) as pdf:
            for page in pdf.pages:
                tables = page.find_tables()
                if len(tables) > 0:
                    pages_text.append(self.__extract_with_tables(page, tables))
                else:
                    pages_text.append(page.extract_text())

        return "\n".join(pages_text)

    def __extract_with_tables(self, page, tables):
        page_tables = []

        for i, table in enumerate(tables):
            page_tables.append(
                {
                    "id": i,
                    "text": self.__table_to_md(table.extract()),
                    "bbox": {
                        "top": table.bbox[1],
                        "x0": table.bbox[0],
                        "x1": table.bbox[2],
                        "bottom": table.bbox[3],
                    },
                }
            )
        words = page.extract_words()
        full_text = ""
        prev_level = -1
        prev_word = ""
        placed_tables = set()
        table_queue = []
        place_table = False
        for i, word in enumerate(words):
            word_bbox = {
                "top": word["top"],
                "x0": word["x0"],
                "x1": word["x1"],
                "bottom": word["bottom"],
            }
            in_table = self.__find_in_tables(word_bbox, page_tables)
            if in_table is None:
                if i > 0:
                    full_text += prev_word
                    if word_bbox["bottom"] == prev_level:
                        full_text += " "
                    else:
                        full_text += "\n"
                    if place_table:
                        full_text += "".join(table_queue)
                        table_queue = []
                        place_table = False
                prev_level = word_bbox["bottom"]
                prev_word = word["text"]
            else:
                if in_table not in placed_tables:
                    table = page_tables[in_table]
                    table_queue.append("\n" + table["text"] + "\n")
                    place_table = True
                    placed_tables.add(in_table)
        full_text += prev_word
        if place_table:
            full_text += "".join(table_queue)
        return full_text

    @staticmethod
    def __touch_bbox(word_bbox, bbox):
        if (
            word_bbox["bottom"] >= bbox["top"]
            and word_bbox["top"] <= bbox["bottom"]
            and word_bbox["x1"] >= bbox["x0"]
            and word_bbox["x0"] <= bbox["x1"]
        ):
            return True
        return False

    def __find_in_tables(self, word_bbox, tables):
        for table in tables:
            if self.__touch_bbox(word_bbox, table["bbox"]):
                return table["id"]
        return None

    @staticmethod
    def __table_to_md(table):
        df = pd.DataFrame(table[1:], columns=table[0])
        return tabulate(df, headers="firstrow", tablefmt="plain")



