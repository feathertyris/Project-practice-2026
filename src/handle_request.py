import socket
import random
import os
import json
from collections import deque

# Список поддерживающих аффирмаций
AFFIRMATIONS = [
    "Вы делаете лучше, чем вам кажется",
    "Сегодня - хороший день для маленького шага",
    "Ваши чувства имеют значение",
    "Пауза - это тоже прогресс",
    "Вы не обязаны быть продуктивным каждый час",
    "Вы уже справились со всеми своими плохими днями до этого",
    "Быть добрым к себе - это не слабость, а сила",
    "Ваше существование делает мир лучше уже тем, что вы в нём есть",
    "Разрешите себе сегодня просто быть",
    "Каждое утро - это новое начало"
]

# Класс для управления аффирмациями без повторений
class AffirmationManager:
    def __init__(self, affirmations_list):
        self.original_list = affirmations_list.copy()
        self.remaining = affirmations_list.copy()
        self.history = deque(maxlen=len(affirmations_list))
        random.shuffle(self.remaining)
        print(f"[*] Инициализация менеджера аффирмаций: {len(self.remaining)} аффирмаций")
    
    def get_next(self):
        # Если список оставшихся пуст, сбрасываем
        if not self.remaining:
            print("[*] Список аффирмаций закончился, сбрасываем...")
            # Сбрасываем remaining, исключая те, что в истории
            self.remaining = [a for a in self.original_list if a not in self.history]
            random.shuffle(self.remaining)
            
            # Если всё равно пусто (маловероятно), просто копируем весь список
            if not self.remaining:
                self.remaining = self.original_list.copy()
                random.shuffle(self.remaining)
                self.history.clear()
        
        # Берём следующую аффирмацию
        next_affirmation = self.remaining.pop(0)
        self.history.append(next_affirmation)
        print(f"[*] Выдана аффирмация: {next_affirmation[:30]}... Осталось: {len(self.remaining)}")
        return next_affirmation
    
    def get_current(self):
        return self.history[-1] if self.history else None

# Глобальный менеджер аффирмаций
affirmation_manager = AffirmationManager(AFFIRMATIONS)

def generate_html(current_affirmation, used_count, total_count):
    html = f"""<!DOCTYPE html>
<html lang="ru">
<head>
    <meta charset="UTF-8" />
    <meta name="viewport" content="width=device-width, initial-scale=1.0" />
    <title>Московский Политех — Помощь психолога</title>
    <style>
        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}

        body {{
            font-family: 'Inter', system-ui, -apple-system, 'Helvetica Neue', 'Segoe UI', Roboto, Helvetica, Arial, sans-serif;
            background-color: #ffffff;
            line-height: 1.5;
        }}

        .wrapper {{
            width: 100%;
            min-height: 100vh;
        }}

        header.container {{
            display: flex;
            justify-content: space-between;
            align-items: center;
            padding: 1rem 5%;
            border-bottom: 1px solid #eee;
            flex-wrap: wrap;
            gap: 1rem;
            background: #ffffff;
        }}

        .logo {{
            display: flex;
            gap: 0.5rem;
            align-items: center;
        }}

        .logo img {{
            max-height: 60px;
            width: auto;
        }}

        .content {{
            padding: 2rem 5%;
        }}

        .hero {{
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 3rem;
            align-items: center;
            max-width: 1280px;
            margin: 0 auto;
        }}

        .main-title {{
            font-size: 2.8rem;
            font-weight: 800;
            line-height: 1.2;
            margin-bottom: 1.2rem;
            background: linear-gradient(135deg, #1a3b5d, #4c9fcf);
            -webkit-background-clip: text;
            background-clip: text;
            color: transparent;
        }}

        .subtitle {{
            font-size: 1.1rem;
            color: #5a6e7e;
            margin-bottom: 2rem;
            max-width: 500px;
        }}

        .illustration {{
            display: flex;
            justify-content: center;
            align-items: center;
        }}

        .illustration img {{
            max-height: 400px;
            width: auto;
        }}

        .affirmation-section {{
            max-width: 1280px;
            margin: 3rem auto 0;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            border-radius: 2rem;
            padding: 2rem 2.5rem;
            box-shadow: 0 8px 24px rgba(0, 0, 0, 0.1);
        }}

        .affirmation-card {{
            background: white;
            border-radius: 1.5rem;
            padding: 2rem;
            text-align: center;
        }}

        .affirmation-icon {{
            font-size: 3rem;
            margin-bottom: 1rem;
        }}

        .affirmation-text {{
            font-size: 1.8rem;
            line-height: 1.4;
            color: #1a202c;
            font-weight: 500;
            margin-bottom: 1.5rem;
            padding: 1rem;
            transition: transform 0.3s ease;
        }}

        .refresh-btn {{
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            border: none;
            padding: 0.8rem 2rem;
            font-size: 1rem;
            font-weight: 600;
            border-radius: 2rem;
            cursor: pointer;
            transition: all 0.3s ease;
            font-family: inherit;
            margin-top: 0.5rem;
        }}

        .refresh-btn:hover {{
            transform: scale(1.05);
            box-shadow: 0 10px 20px rgba(0, 0, 0, 0.2);
        }}

        .affirmation-label {{
            display: inline-block;
            background: #e0e7ff;
            color: #4c51bf;
            padding: 0.3rem 1rem;
            border-radius: 2rem;
            font-size: 0.85rem;
            font-weight: 600;
            margin-bottom: 1rem;
        }}

        .counter {{
            margin-top: 1rem;
            font-size: 0.85rem;
            color: #6b7280;
            display: flex;
            justify-content: center;
            gap: 1rem;
            flex-wrap: wrap;
        }}

        .counter span {{
            background: #f3f4f6;
            padding: 0.25rem 0.75rem;
            border-radius: 1rem;
        }}

        @media (max-width: 768px) {{
            header.container {{
                flex-direction: column;
                text-align: center;
                padding: 1rem 3%;
            }}
            .content {{
                padding: 1.5rem;
            }}
            .hero {{
                grid-template-columns: 1fr;
                text-align: center;
                gap: 2rem;
            }}
            .illustration {{
                order: -1;
            }}
            .main-title {{
                font-size: 2rem;
            }}
            .subtitle {{
                max-width: 100%;
            }}
            .affirmation-text {{
                font-size: 1.3rem;
            }}
        }}
    </style>
</head>
<body>
    <div class="wrapper">
        <header class="container">
            <div class="logo">
                <img src="logo.svg" alt="Логотип Московский Политех" onerror="this.style.display='none'">
            </div>
        </header>

        <main class="content">
            <section class="hero">
                <div class="hero-text">
                    <h1 class="main-title">Сайт психологической помощи Московского Политеха</h1>
                    <p class="subtitle">Иногда справляться с трудностями в одиночку тяжело. Наши психологи помогут найти выход. Консультации бесплатны, конфиденциальны и доступны очно или онлайн.</p>
                </div>
                <div class="illustration">
                    <img src="hand-help.svg" alt="Рука протягивает ладонь маленькому человечку в облаке" onerror="this.style.display='none'">
                </div>
            </section>

            <div class="affirmation-section">
                <div class="affirmation-card">
                    <div class="affirmation-label">Машина аффирмаций</div>
                    <div class="affirmation-icon">🌿</div>
                    <div class="affirmation-text">
                        "{current_affirmation}"
                    </div>
                    <button class="refresh-btn" onclick="refreshAffirmation()">
                        Получить новую аффирмацию ✨
                    </button>
                    <div class="counter">
                        <span>📊 Просмотрено: {used_count} / {total_count}</span>
                        <span>💫 Каждая аффирмация уникальна</span>
                    </div>
                </div>
            </div>

            <div style="height: 1rem;"></div>
        </main>
    </div>

    <script>
        async function refreshAffirmation() {{
            try {{
                const response = await fetch('/next-affirmation');
                const data = await response.json();
                
                if (data.affirmation) {{
                    const textElement = document.querySelector('.affirmation-text');
                    textElement.style.transform = 'scale(1.05)';
                    
                    setTimeout(() => {{
                        textElement.innerHTML = `"${{data.affirmation}}"`;
                        textElement.style.transform = 'scale(1)';
                    }}, 150);
                    
                    document.querySelector('.counter span:first-child').innerHTML = `📊 Просмотрено: ${{data.used_count}} / ${{data.total_count}}`;
                }}
            }} catch (error) {{
                console.error('Ошибка:', error);
                location.reload();
            }}
        }}
    </script>
</body>
</html>"""
    return html

def handle_request(request):
    global affirmation_manager
    
    # Разбираем запрос
    request_line = request.split('\n')[0]
    path = request_line.split(' ')[1] if len(request_line.split(' ')) > 1 else '/'
    
    print(f"[*] Запрос: {path}")
    
    # Если запрос к корню - отдаём HTML
    if path == '/':
        current = affirmation_manager.get_next()
        used_count = len(affirmation_manager.history)
        total_count = len(AFFIRMATIONS)
        body = generate_html(current, used_count, total_count)
        response = (
            "HTTP/1.1 200 OK\r\n"
            f"Content-Length: {len(body.encode('utf-8'))}\r\n"
            "Content-Type: text/html; charset=utf-8\r\n"
            "Connection: close\r\n"
            "\r\n"
            f"{body}"
        )
        return response
    
    # Обработка AJAX запроса для получения следующей аффирмации
    elif path == '/next-affirmation':
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
    
    # Если запрос к SVG файлам
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
        except Exception as e:
            print(f"[!] Ошибка загрузки logo.svg: {e}")
            response = "HTTP/1.1 404 Not Found\r\nContent-Length: 0\r\nConnection: close\r\n\r\n"
            return response.encode()
    
    elif path == '/hand-help.svg':
        try:
            with open('hand-help.svg', 'rb') as f:
                body = f.read()
            response = (
                "HTTP/1.1 200 OK\r\n"
                f"Content-Length: {len(body)}\r\n"
                "Content-Type: image/svg+xml\r\n"
                "Connection: close\r\n"
                "\r\n"
            )
            return response.encode() + body
        except Exception as e:
            print(f"[!] Ошибка загрузки hand-help.svg: {e}")
            response = "HTTP/1.1 404 Not Found\r\nContent-Length: 0\r\nConnection: close\r\n\r\n"
            return response.encode()
    
    # Все остальные запросы - 404
    else:
        response = "HTTP/1.1 404 Not Found\r\nContent-Length: 0\r\nConnection: close\r\n\r\n"
        return response.encode()

# Запуск сервера
server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.bind(('localhost', 8080))
server.listen(5)

print("=" * 60)
print("Московский Политех - Сайт психологической помощи с Машиной аффирмаций")
print("=" * 60)
print("Сервер запущен на http://localhost:8080")
print()
print("📝 Логика работы аффирмаций:")
print("  • Аффирмации не повторяются при обновлении")
print("  • После просмотра всех - список перемешивается заново")
print("  • Счётчик показывает сколько уникальных аффирмаций просмотрено")
print()
print("📁 Файлы в текущей директории:")
for file in os.listdir('.'):
    if file.endswith('.svg'):
        print(f"  ✓ {file}")
print()
print("Нажмите Ctrl+C для остановки сервера")
print("=" * 60)

try:
    while True:
        client, addr = server.accept()
        request = client.recv(4096).decode('utf-8', errors='ignore')
        response = handle_request(request)
        if isinstance(response, str):
            client.sendall(response.encode('utf-8'))
        else:
            client.sendall(response)
        client.close()
        print(f"[+] Страница отправлена: {addr}")
        print(f"[+] Просмотрено аффирмаций: {len(affirmation_manager.history)}/{len(AFFIRMATIONS)}")
except KeyboardInterrupt:
    print("\n\n[!] Сервер остановлен. Берегите себя!")
    server.close()
