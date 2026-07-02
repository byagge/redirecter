from __future__ import annotations

import argparse
from pathlib import Path
from typing import Any

from pyrogram import Client

import config


def read_proxy_info(file_path: str) -> dict[str, Any] | None:
    path = Path(file_path)
    if not path.exists():
        return None

    parts = path.read_text(encoding="utf-8").strip().split(":")
    if len(parts) != 4 or not all(parts):
        raise SystemExit(
            f"В {file_path} нужна одна строка: host:port:user:password (4 поля через двоеточие)."
        )

    host, port, username, password = parts
    try:
        port_int = int(port)
    except ValueError as e:
        raise SystemExit(f"Некорректный порт в {file_path}: {port}") from e

    return {
        "scheme": "socks5",
        "hostname": host,
        "port": port_int,
        "username": username,
        "password": password,
    }


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Создание .session файла Telegram-аккаунта (Pyrogram) в папку sessions."
    )
    parser.add_argument(
        "--session-name",
        required=True,
        help='Имя сессии без расширения .session (например: "acc1").',
    )
    parser.add_argument(
        "--sessions-dir",
        default=getattr(config, "SESSIONS_DIR", "sessions"),
        help='Папка, куда сохранить .session (по умолчанию из config.SESSIONS_DIR).',
    )
    parser.add_argument(
        "--api-id",
        type=int,
        default=config.API_ID,
        help="API_ID (по умолчанию из redirecter/config.py).",
    )
    parser.add_argument(
        "--api-hash",
        default=config.API_HASH,
        help="API_HASH (по умолчанию из redirecter/config.py).",
    )
    parser.add_argument(
        "--proxy-file",
        default=getattr(config, "PROXY_FILE", "proxy.txt"),
        help='Путь к файлу прокси host:port:user:password (по умолчанию из config.PROXY_FILE).',
    )
    parser.add_argument(
        "--no-proxy",
        action="store_true",
        default=bool(getattr(config, "NO_PROXY", False)),
        help="Не использовать прокси (перекрывает config.NO_PROXY).",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()

    session_name = args.session_name.strip()
    if not session_name:
        raise SystemExit("session-name не может быть пустым.")

    sessions_dir = Path(args.sessions_dir).resolve()
    sessions_dir.mkdir(parents=True, exist_ok=True)

    session_path = sessions_dir / f"{session_name}.session"
    if session_path.exists():
        raise SystemExit(f"Сессия уже существует: {session_path}")

    proxy = None if args.no_proxy else read_proxy_info(args.proxy_file)
    if proxy:
        print(f"[INFO] Используется прокси из {args.proxy_file}")
    else:
        print("[INFO] Прокси не используется")

    app = Client(
        name=session_name,
        api_id=args.api_id,
        api_hash=args.api_hash,
        workdir=str(sessions_dir),
        proxy=proxy,
    )

    with app:
        me = app.get_me()
        print(f"[OK] Авторизация успешна: {me.first_name} (id={me.id})")

    print(f"[OK] Сессия сохранена: {session_path}")
    print("[OK] Можно запускать автоответчик, он подхватит сессию автоматически.")


if __name__ == "__main__":
    main()

