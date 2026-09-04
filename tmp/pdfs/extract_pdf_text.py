import json
import sys
from pathlib import Path

from pypdf import PdfReader


def main() -> None:
    source = Path(sys.argv[1])
    destination = Path(sys.argv[2])
    reader = PdfReader(str(source))
    records = []
    total_characters = 0

    for page_number, page in enumerate(reader.pages, start=1):
        text = page.extract_text() or ""
        total_characters += len(text)
        records.append({"page": page_number, "text": text})

    destination.write_text(
        json.dumps(records, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    print(
        json.dumps(
            {
                "pages": len(records),
                "characters": total_characters,
                "output": str(destination),
            },
            ensure_ascii=False,
        )
    )


if __name__ == "__main__":
    main()
