class ParserService:
    """
    Заглушка: возвращает фиктивный текст вместо парсинга PDF.
    В будущем заменить на парсер спунтика???.
    """

    def parse_pdf(self, content: bytes) -> str:
        # Проверка на пустой файл
        if not content or len(content) == 0:
            raise ValueError("Empty file")

        return "Это тестовый контент книги. " * 100



