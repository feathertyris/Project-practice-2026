# Техническое руководство: сайт психологической помощи с «Машиной аффирмаций»

Данное руководство описывает процесс создания одностраничного веб‑приложения на «голом» Python (без фреймворков), которое раздаёт персонализированные аффирмации. В основе лежит кастомный HTTP‑сервер, написанный с использованием встроенной библиотеки `socket`.

---

## Оглавление

1. Архитектура решения
2. Пошаговое создание с нуля
3. Модификация: что добавлено сверх базового HTTP‑сервера
4. Полный код HTTP-сервера
---

## Архитектура решения

Проект состоит из нескольких логических блоков:

1. **Сокет‑сервер** — принимает TCP‑соединения, читает сырой HTTP‑запрос.
2. **Маршрутизатор** (`handle_request`) — определяет, какой ресурс запрошен (`/`, `/next-affirmation`, `/logo.svg` и т. д.).
3. **Менеджер аффирмаций** (`AffirmationManager`) — управляет очередью уникальных фраз, исключая повторения.
4. **Генератор HTML** (`generate_html`) — встраивает текущую аффирмацию в готовый шаблон страницы.
5. **Клиентский JavaScript** — по нажатию кнопки отправляет `fetch`-запрос на `/next-affirmation` и обновляет текст без перезагрузки страницы.

**UML Диаграмма классов**
<img width="698" height="560" alt="image" src="https://github.com/user-attachments/assets/eb81ff06-4552-4032-bcc1-a3e4293c299a" />

---

## Пошаговое создание с нуля

### Шаг 1: HTTP‑сервер на сокетах

Создаём TCP‑сервер, который слушает порт `8080` и принимает входящие подключения в бесконечном цикле.

```python
import socket

server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.bind(('localhost', 8080))
server.listen(5)

print("Сервер запущен на http://localhost:8080")


try:
    while True:
        client, addr = server.accept()                     # Принимаем клиента
        request = client.recv(4096).decode('utf-8', errors='ignore')  # Читаем запрос
        response = handle_request(request)                 # Готовим ответ (см. далее)
        if isinstance(response, str):
            client.sendall(response.encode('utf-8'))       # Отправляем текст
        else:
            client.sendall(response)                       # Отправляем байты (для SVG)
        client.close()
except KeyboardInterrupt:
    print("Сервер остановлен.")
    server.close()
```
### Шаг 2: Парсинг запроса и маршрутизация

Функция `handle_request` извлекает путь из первой строки HTTP-запроса и возвращает соответствующий ответ.

```python
def handle_request(request):
    # Первая строка выглядит как: GET / HTTP/1.1
    request_line = request.split('\n')[0]
    parts = request_line.split(' ')
    path = parts[1] if len(parts) > 1 else '/'


    if path == '/':
        # Отдаём главную HTML‑страницу
        ...
    elif path == '/next-affirmation':
        # AJAX‑эндпоинт, возвращает JSON
        ...
    elif path == '/logo.svg':
        # Раздача файла logo.svg
        ...
    elif path == '/hand-help.svg':
        # Раздача файла hand-help.svg
        ...
    else:
        # 404 Not Found
        ...

```
### Шаг 3: Генерация HTML-страницы

Функция `generate_html` формирует полную HTML-страницу, используя f-строку. В неё подставляются:

- текущая аффирмация;
- количество использованных аффирмаций (`used_count`);
- общее количество аффирмаций (`total_count`).

```html
def generate_html(current_affirmation, used_count, total_count):
    html = f"""<!DOCTYPE html>
<html lang="ru">
<head>
<meta charset="UTF-8" />
<meta name="viewport" content="width=device-width, initial-scale=1.0"/>
<title>Машина аффирмаций</title>
<style>
/* Тут стили, можно вставить базовые или оставить пустыми */
body {{
  font-family: Arial, sans-serif;
  background: linear-gradient(135deg, #f0f4f8, #d9e2ec);
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  min-height: 100vh;
  margin: 0;
}}
.card {{
  background: #fff;
  padding: 2em;
  border-radius: 10px;
  box-shadow: 0 4px 12px rgba(0,0,0,0.1);
  max-width: 400px;
  width: 90%;
  text-align: center;
}}
.affirmation-text {{
  font-size: 1.5em;
  margin-bottom: 1em;
  transition: transform 0.3s;
}}
.counter {{
  margin-top: 1em;
  font-size: 0.9em;
  color: #555;
}}
button {{
  margin-top: 1em;
  padding: 0.5em 1em;
  border: none;
  background-color: #4CAF50;
  color: #fff;
  border-radius: 5px;
  cursor: pointer;
  font-size: 1em;
  transition: background-color 0.3s;
}}
button:hover {{
  background-color: #45a049;
}}
</style>
</head>
<body>
<div class="card">
  <div class="affirmation-text">"{current_affirmation}"</div>
  <button onclick="refreshAffirmation()">Получить новую аффирмацию</button>
  <div class="counter">
    <span>📊 Просмотрено: {used_count} / {total_count}</span><br/>
    <span>💫 Каждая аффирмация уникальна</span>
  </div>
</div>
<script>
async function refreshAffirmation() {{
  const response = await fetch('/next-affirmation');
  const data = await response.json();
  const affirmationDiv = document.querySelector('.affirmation-text');
  // Анимация смены текста
  affirmationDiv.style.transform = 'scale(0.8)';
  setTimeout(() => {{
    affirmationDiv.innerHTML = `"{data.affirmation}"`;
    document.querySelector('.counter span:first-child').innerHTML =
        `📊 Просмотрено: ${{data.used_count}} / ${{data.total_count}}`;
    affirmationDiv.style.transform = 'scale(1)';
  }}, 200);
}}
</script>
</body>
</html>"""
    return html

```
### Шаг 4: Логика аффирмаций без повторов

Чтобы аффирмации не повторялись до тех пор, пока не закончатся все уникальные фразы, реализован класс `AffirmationManager`.

```python
from collections import deque
import random

class AffirmationManager:
    def __init__(self, affirmations_list):
        self.original_list = affirmations_list.copy()
        self.remaining = affirmations_list.copy()
        self.history = deque(maxlen=len(affirmations_list))
        random.shuffle(self.remaining)

    def get_next(self):
        if not self.remaining:
            # Все показаны, пересобираем набор, исключая те, что в истории
            self.remaining = [a for a in self.original_list if a not in self.history]
            random.shuffle(self.remaining)
            if not self.remaining:
                # Если вдруг всё равно пусто, сбрасываем полностью
                self.remaining = self.original_list.copy()
                random.shuffle(self.remaining)
            self.history.clear()

        next_affirmation = self.remaining.pop(0)
        self.history.append(next_affirmation)
        return next_affirmation
```
### Шаг 5: AJAX-эндпоинт для обновления контента

Сервер обрабатывает запрос `/next-affirmation`, возвращая JSON с новой аффирмацией и статистикой.

```python
import json

# Внутри handle_request() при path == '/next-affirmation':
if path == '/next-affirmation':
    next_aff = affirmation_manager.get_next()
    used_count = len(affirmation_manager.history)
    total_count = len(AFFIRMATIONS)

    response_data = json.dumps({
        'affirmation': next_aff,
        'used_count': used_count,
        'total_count': total_count,
        'remaining': len(affirmation_manager.remaining)
    })

    response = (
        "HTTP/1.1 200 OK\r\n"
        f"Content-Length: {len(response_data.encode('utf-8'))}\r\n"
        "Content-Type: application/json; charset=utf-8\r\n"
        "Connection: close\r\n"
        "Access-Control-Allow-Origin: *\r\n"
        "\r\n"
        f"{response_data}"
    )
    return response
```
### Шаг 6: Раздача статических файлов (SVG)

Сервер умеет отдавать бинарные SVG-файлы с правильным `Content-Type`. Ниже пример для `logo.svg`:

```python
elif path == '/logo.svg':
    try:
        with open('logo.svg', 'rb') as f:
            body = f.read()
        response = (
            "HTTP/1.1 200 OK\r\n"
            f"Content-Length: {len(body)}\r\n"
            "Content-Type: image/svg+xml\r\n"
            "Connection: close\r\n"
            "\r\n"
        )
        return response.encode() + body
    except:
        return "HTTP/1.1 404 Not Found\r\nContent-Length: 0\r\nConnection: close\r\n\r\n".encode()
```
---
### Модификация: что добавлено сверх базового HTTP-сервера

Базовая задача — реализовать с нуля программный HTTP-сервер на сокетах, способный принимать запросы, парсить их и возвращать ответы. Ниже перечислены улучшения, которые превратили этот базовый сервер в полноценный «сервис аффирмаций».

#### 1. Система аффирмаций с умным менеджером повторов

Поверх базового HTTP-сервера добавлен класс `AffirmationManager`, который:

- Гарантирует, что пользователь **не видит повторяющихся аффирмаций**, пока не пройдёт весь список.
- Использует кольцевую очередь (`deque`) и динамическое обновление оставшегося пула.
- Выводит в логи сервера отладочную информацию о том, какая аффирмация выдана и сколько осталось.

#### 2. Динамическое обновление контента без перезагрузки (AJAX)

- Добавлен отдельный эндпоинт `/next-affirmation`, возвращающий **JSON** вместо HTML.
- На клиентской стороне реализован JavaScript, который выполняет асинхронный `fetch`-запрос и **мгновенно обновляет** текст аффирмации и счётчик без перезагрузки всей страницы.
- Реализована микроанимация (`scale`), которая визуально сглаживает смену контента.

#### 3. Визуальный счётчик прогресса

- В HTML-шаблон добавлен элемент, отображающий статистику: `Просмотрено: X / Y`.
- При каждом AJAX-запросе счётчик обновляется на стороне клиента, не требуя повторного рендеринга страницы.

#### 4. Раздача статических SVG-файлов

- Сервер умеет обрабатывать запросы к статическим ресурсам (`/logo.svg`, `/hand-help.svg`).
- Корректно отдаёт бинарные файлы с заголовком `Content-Type: image/svg+xml`.
- При отсутствии файла возвращает HTTP 404 вместо падения.

#### 5. Адаптивная вёрстка и визуальное оформление

- В ответ сервера встроен полноценный HTML-шаблон с CSS-стилями.
- Добавлены медиазапросы для корректного отображения на мобильных устройствах.
- Использован градиентный фон, карточки, тени, скругления — всё для дружелюбного пользовательского интерфейса.

#### 6. Система логирования работы

- Каждое действие сервера логируется в консоль с визуальными маркерами (`[*]`, `[+]`, `[!]`):
  - Выдача аффирмации.
  - Отправка страницы клиенту.
  - Общее количество просмотренных фраз.
- При запуске сервер выводит информационное сообщение и проверяет наличие SVG-файлов в директории.

---
##  Полный код HTTP-сервера
 Полный код HTTP-сервера находится в [handle_request.py](../src/handle_request.py)
