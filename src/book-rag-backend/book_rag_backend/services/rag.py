# book_rag_backend/services/rag.py
from uuid import UUID
from typing import List
from .qdrant import QdrantService
from .embeddings import EmbeddingsService
from .llm import LLMService


class RAGService:
    def __init__(
            self,
            qdrant: QdrantService,
            embeddings: EmbeddingsService,
            llm: LLMService,
            top_k: int = 5,
            score_threshold: float = 0.7,
            max_context_tokens: int = 200000,
    ):
        self.qdrant = qdrant
        self.embeddings = embeddings
        self.llm = llm
        self.top_k = top_k
        self.score_threshold = score_threshold
        self.max_context_tokens = max_context_tokens

    async def search_in_book(
            self,
            book_id: UUID,
            messages: List[dict],
    ) -> List[dict]:

        # 1. Проверяем существование книги
        if not await self.qdrant.book_exists(book_id):
            raise ValueError("NotFound")

        # 2. Извлекаем последний вопрос пользователя
        user_question = messages[-1]["content"]

        # 3. Embed вопрос
        query_vector = self.embeddings.embed(user_question)

        # 4. Поиск релевантных чанков в книге
        chunks = await self.qdrant.semantic_search_in_book(
            book_id=book_id,
            query_vector=query_vector,
            limit=self.top_k,
            score_threshold=self.score_threshold,
        )

        # 5. Формируем контекст из чанков
        context_parts = []
        for i, chunk in enumerate(chunks, 1):
            context_parts.append(f"[Источник {i}]: {chunk['content']}")
        context = "\n\n".join(context_parts)

        # 6. Строим промпт для LLM
        system_prompt = (
            "Ты — полезный ассистент, отвечающий на вопросы по книге. "
            "Используй только предоставленные источники для ответа. "
            "Если информации недостаточно, честно скажи об этом. "
            "Отвечай на том же языке, на котором задан вопрос."
        )

        # Формируем messages для LLM: system + history + context + question
        llm_messages = [{"role": "system", "content": system_prompt}]

        # Добавляем историю диалога (кроме последнего вопроса)
        for msg in messages[:-1]:
            llm_messages.append({"role": msg["role"], "content": msg["content"]})

        # Добавляем вопрос с контекстом
        augmented_question = (
            f"Контекст из книги:\n{context}\n\n"
            f"Вопрос пользователя: {user_question}"
        )
        llm_messages.append({"role": "user", "content": augmented_question})

        # 7. Вызываем LLM
        answer = await self.llm.generate(llm_messages)

        # 8. Возвращаем обновлённую историю диалога
        return messages + [{"role": "assistant", "content": answer}]