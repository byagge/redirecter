## redirecter автоответчик (Pyrogram)

Отдельный скрипт, который **мгновенно** отвечает в личку всем, кто пишет аккаунту с запущенной сессией, кроме пользователей из `blacklist.txt`.

### Настройка

- Отредактируйте `redirecter/config.py`:
  - `API_ID`, `API_HASH`
  - `SESSIONS_DIR` (папка с `.session`)
  - `AUTO_REPLY_TEXT`
  - (опционально) `PROXY_FILE` / `NO_PROXY`
- Добавьте исключения в `redirecter/blacklist.txt` (username или user_id, по одному в строке).

### Запуск

Из корня проекта:

```bash
python redirecter/auto_responder.py
```

### Сессии

- Положите файлы `*.session` в папку `SESSIONS_DIR` (по умолчанию `sessions/`).
- Скрипт запускает автоответчик **во всех сессиях одновременно**.
- Если вы добавили новый `*.session` файл — он автоматически подхватится через пару секунд.

