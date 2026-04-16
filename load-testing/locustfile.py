import os
from uuid import uuid4
from locust import HttpUser, task, between

_PDF_PATH = os.path.join(os.path.dirname(__file__), "test.pdf")
if not os.path.exists(_PDF_PATH):
    raise FileNotFoundError(
        f"Файл {_PDF_PATH} не найден. Положите тестовый PDF в одну папку со скриптом."
    )

with open(_PDF_PATH, "rb") as f:
    PDF_BYTES = f.read()
PDF_FILENAME = "test.pdf"
PDF_CONTENT_TYPE = "application/pdf"


class PdfUploadUser(HttpUser):
    wait_time = between(5, 10)

    @task
    def upload_pdf(self):
        files = {
            "file": (f"{str(uuid4())}.pdf", PDF_BYTES, PDF_CONTENT_TYPE)
        }

        with self.client.post(
            "/backend/books",
            files=files,
            catch_response=True
        ) as response:
            if 200 <= response.status_code < 300:
                response.success()
            else:
                response.failure(
                    f"HTTP {response.status_code} | {response.text[:200]}"
                )