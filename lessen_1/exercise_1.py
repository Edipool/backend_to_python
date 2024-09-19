import json
from typing import Any, Awaitable, Callable


async def app(
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

        if "n" in params:  # проверим, что параметр n есть
            try:  # пытаемся преобразовать n в число
                number = int(params["n"])  # преобразуем в число
                if number < 0:
                    raise ValueError(
                        "Negative number"
                    )  # возвращаем 400 для отрицательного числа

                result = 1  # начинаем с результата 1
                for i in range(2, number + 1):  # проходим по числу до n
                    result *= i  # умножаем на i
                response_body = json.dumps({"result": result})  # возвращаем результат
                status_code = 200  # успешный запрос
            except ValueError:  # если n не является числом или < 0
                response_body = json.dumps({"error": "Invalid or negative number"})
                status_code = 400  # ошибка ввода, статус 400
        else:  # если n не передан
            response_body = json.dumps({"error": "Missing parameter 'n'"})
            status_code = 422  # статус 422, так как параметр отсутствует или неверен

    # проверим, что запрос сделан к пути "/fibonacci"
    elif scope["path"].startswith("/fibonacci/") and scope["method"] == "GET":
        try:
            # Извлекаем параметр n из URL path
            n_str = scope["path"].split("/")[2]
            index = int(n_str)  # преобразуем в число
            if index < 0:
                raise ValueError(
                    "Negative index"
                )  # возвращаем 400 для отрицательного числа

            # Логика подсчета числа Фибоначчи
            a, b = 0, 1
            for _ in range(index):
                a, b = b, a + b
            response_body = json.dumps({"result": a})  # возвращаем результат
            status_code = 200  # успешный запрос
        except (IndexError, ValueError):  # если n не является числом или < 0
            response_body = json.dumps({"error": "Invalid or missing index"})
            status_code = (
                422 if "n" not in scope["path"] else 400
            )  # 422 если не число, 400 если отрицательное

    # проверим, что запрос сделан к пути "/mean"
    elif scope["path"] == "/mean" and scope["method"] == "GET":
        message = await receive()  # получаем тело запроса
        try:
            body = json.loads(
                message.get("body", b"").decode("utf-8")
            )  # парсим тело как JSON
            if not isinstance(body, list) or not all(
                isinstance(x, (int, float)) for x in body
            ):
                raise ValueError("Invalid input")  # если не массив чисел
            if len(body) == 0:
                raise ValueError("Empty array")  # если массив пуст
            mean_value = sum(body) / len(body)  # вычисляем среднее
            response_body = json.dumps({"result": mean_value})  # возвращаем результат
            status_code = 200  # успешный запрос
        except ValueError as e:  # если тело не массив float'ов или оно пустое
            if str(e) == "Empty array":
                response_body = json.dumps({"error": "Empty array"})
                status_code = 400  # ошибка пустого массива, статус 400
            else:
                response_body = json.dumps({"error": "Invalid input"})
                status_code = 422  # ошибка ввода, статус 422

    else:  # если запрос не соответствует нашим ожиданиям
        response_body = json.dumps({"error": "Not Found"})
        status_code = 404  # статус 404, так как запрос некорректен

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


# Пример запросов
# curl "http://localhost:8000/factorial?n=5"
# curl "http://localhost:8000/fibonacci/5"
# curl -X GET -d "[1.0, 2.3, 3.6]" "http://localhost:8000/mean"
if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="localhost", port=8000)
