from langchain_text_splitters import RecursiveCharacterTextSplitter


class SplitterService:
    def __init__(
            self,
            chunk_size: int = 500,  # Размер чанка в символах
            chunk_overlap: int = 50,  # Перекрытие для сохранения контекста
    ):
        self.splitter = RecursiveCharacterTextSplitter(
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap,
            length_function=len,
            is_separator_regex=False,
            # Порядок разделителей: от крупных к мелким
            separators=[
                "\n\n",  # Абзацы
                "\n",  # Строки
                ". ",  # Предложения
                "! ",  # Предложения
                "? ",  # Предложения
                " ",  # Слова
                "",  # Символы
            ],
        )

    def split(self, text: str) -> list[str]:
        if not text or not text.strip():
            return []

        # LangChain возвращает объекты Document, берём только текст
        chunks = self.splitter.split_text(text)
        return chunks