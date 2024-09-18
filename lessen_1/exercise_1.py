import json
from typing import Any, Awaitable, Callable


async def factorial(
    scope: dict[str, Any],
    receive: Callable[[], Awaitable[dict[str, Any]]],
    send: Callable[[dict[str, Any]], Awaitable[None]],
) -> None:
    assert scope["type"] == "http"  # проверим, что это http запрос

    # проверим, что запрос сделан к пути "/factorial"
    if (
        scope["path"] == "/factorial"
        and scope["method"] == "GET"
        and "query_string" in scope
    ):
        query_params = scope["query_string"].decode(
            "utf-8"
        )  # декодируем параметры в строку
        params = dict(
            param.split("=") for param in query_params.split("&")
        )  # конвертируем в словарь
        # Логика подсчета факториала
        if "number" in params:  # проверим, что параметр number есть
            try:  # пытаемся преобразовать number в число
                number = int(params["number"])  # преобразуем в число
                result = 1  # начинаем с результата 1
                for i in range(2, number + 1):  # проходим по числу до number
                    result *= i  # умножаем на i
                response_body = json.dumps(
                    {"factorial": result}
                )  # возвращаем результат
                status_code = 200  # успешный запрос
            except ValueError:  # если number не является числом
                response_body = json.dumps({"error": "Invalid number"})
                status_code = 400  # ошибка ввода, статус 400
        else:  # если number не передан
            response_body = json.dumps({"error": "Missing number"})
            status_code = 400  # статус 400, так как параметр отсутствует
    else:  # если запрос не соответствует нашим ожиданиям
        response_body = json.dumps({"error": "Invalid request"})
        status_code = 400  # статус 400, так как запрос некорректен

    # отправка http заголовка т.е. статус и другие заголовки
    await send(
        {
            "type": "http.response.start",
            "status": status_code,
            "headers": [(b"content-type", b"application/json")],
        }
    )
    # отправка http тела т.е. содержимого ответа
    await send(
        {
            "type": "http.response.body",
            "body": response_body.encode("utf-8"),
        }
    )


# Пример запроса
# curl "http://localhost:8000/factorial?number=5"
if __name__ == "__main__":
    import uvicorn

    uvicorn.run(factorial, host="localhost", port=8000)
