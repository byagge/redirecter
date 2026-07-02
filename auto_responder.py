from __future__ import annotations

import asyncio
import logging
from pathlib import Path
from typing import Any

from pyrogram import Client, filters, idle
from pyrogram.errors import FloodWait
from pyrogram.types import Message

import config

log = logging.getLogger("redirecter.auto_responder")


def _read_proxy_info(file_path: str) -> dict[str, Any] | None:
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


def _load_blacklist(blacklist_path: Path) -> tuple[set[int], set[str]]:
    ids: set[int] = set()
    usernames: set[str] = set()

    if not blacklist_path.exists():
        return ids, usernames

    for raw in blacklist_path.read_text(encoding="utf-8").splitlines():
        line = raw.strip()
        if not line or line.startswith("#"):
            continue

        if line.startswith("@"):
            line = line[1:]

        if line.isdigit():
            try:
                ids.add(int(line))
            except Exception:
                continue
        else:
            usernames.add(line.lower())

    return ids, usernames


def _is_blacklisted(message: Message, ids: set[int], usernames: set[str]) -> bool:
    user = message.from_user
    if not user:
        return True

    if user.id in ids:
        return True

    if user.username and user.username.lower() in usernames:
        return True

    return False


async def _send_auto_reply(client: Client, message: Message) -> None:
    text = (getattr(config, "AUTO_REPLY_TEXT", "") or "").strip()
    if not text:
        return

    reply_to = message.id if bool(getattr(config, "REPLY_TO_MESSAGE", True)) else None
    try:
        await client.send_message(message.chat.id, text, reply_to_message_id=reply_to)
    except FloodWait as e:
        wait = int(getattr(e, "value", 0) or getattr(e, "x", 0) or 1)
        log.warning("FloodWait %ss for chat %s", wait, message.chat.id)
        await asyncio.sleep(wait + 1)
        await client.send_message(message.chat.id, text, reply_to_message_id=reply_to)


def _attach_handlers(app: Client, blacklist_path: Path) -> None:
    @app.on_message(filters.private & filters.incoming & ~filters.me & ~filters.service)
    async def _on_private_incoming(client: Client, message: Message) -> None:
        user = message.from_user
        if not user or user.is_bot:
            return

        ids, usernames = _load_blacklist(blacklist_path)
        if _is_blacklisted(message, ids, usernames):
            return

        await _send_auto_reply(client, message)


async def _start_clients_forever() -> None:
    sessions_dir = Path(getattr(config, "SESSIONS_DIR", "sessions")).resolve()
    sessions_dir.mkdir(parents=True, exist_ok=True)

    blacklist_path = Path(__file__).resolve().parent / "blacklist.txt"
    scan_interval = float(getattr(config, "SESSIONS_SCAN_INTERVAL", 3) or 3)

    proxy = None
    if not bool(getattr(config, "NO_PROXY", False)):
        proxy = _read_proxy_info(getattr(config, "PROXY_FILE", "proxy.txt"))

    clients: dict[str, Client] = {}

    async def scan_and_start() -> None:
        for session_file in sessions_dir.glob("*.session"):
            name = session_file.stem
            if name in clients:
                continue

            app = Client(
                name=name,
                api_id=getattr(config, "API_ID", None),
                api_hash=getattr(config, "API_HASH", None),
                workdir=str(sessions_dir),
                proxy=proxy,
            )
            _attach_handlers(app, blacklist_path)
            await app.start()
            clients[name] = app

            me = await app.get_me()
            log.info("[STARTED] %s => %s (id=%s)", name, me.first_name, me.id)

    # Стартуем то, что уже есть, затем постоянно подхватываем новое.
    while True:
        try:
            await scan_and_start()
        except Exception as e:
            log.warning("scan/start failed: %s", e)
        await asyncio.sleep(scan_interval)


def main() -> None:
    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")

    log.info(
        "Auto responder multi-session started. sessions_dir=%s blacklist=%s",
        Path(getattr(config, "SESSIONS_DIR", "sessions")).resolve(),
        Path(__file__).resolve().parent / "blacklist.txt",
    )

    async def runner() -> None:
        asyncio.create_task(_start_clients_forever())
        await idle()

    asyncio.run(runner())


if __name__ == "__main__":
    main()

