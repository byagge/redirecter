from __future__ import annotations

# Отдельный конфиг для redirecter/auto_responder.py

# USER API: https://my.telegram.org/auth
API_ID = 32116176
API_HASH = "6b6707ebebf081ca1ad4e17aa9ef60cd"

# Папка с .session файлами.
# Скрипт будет работать одновременно во всех *.session, и подхватывать новые файлы на лету.
SESSIONS_DIR = "sessions"

# Как часто проверять появление новых сессий (секунды).
SESSIONS_SCAN_INTERVAL = 3

# Прокси (опционально). Формат в файле: host:port:user:password
PROXY_FILE = "proxy.txt"
NO_PROXY = False

# Сообщение, которое будет отправляться каждому входящему ЛС (кроме blacklist).
AUTO_REPLY_TEXT = "Привет! Я сейчас занят, отвечу позже."

# Если True — отвечать реплаем на входящее сообщение.
REPLY_TO_MESSAGE = True

