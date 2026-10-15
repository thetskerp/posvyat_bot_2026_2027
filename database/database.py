import sqlite3
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path


DATABASE_PATH = Path(__file__).resolve().parent / "bot.db"


class ActiveOrderExistsError(Exception):
    """Raised when a user already has a pending or approved order."""


@dataclass(frozen=True)
class Order:
    id: int
    telegram_id: int
    telegram_username: str | None
    full_name: str
    birthdate: str
    group_name: str
    status: str
    created_at: str
    reviewed_at: str | None
    reviewed_by: int | None


def _connect() -> sqlite3.Connection:
    connection = sqlite3.connect(DATABASE_PATH)
    connection.row_factory = sqlite3.Row
    return connection


def _current_time() -> str:
    return datetime.now().astimezone().isoformat(timespec="seconds")


def _row_to_order(row: sqlite3.Row | None) -> Order | None:
    if row is None:
        return None
    return Order(**dict(row))


def init_db() -> None:
    DATABASE_PATH.parent.mkdir(parents=True, exist_ok=True)

    with _connect() as connection:
        connection.executescript(
            """
            CREATE TABLE IF NOT EXISTS orders (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                telegram_id INTEGER NOT NULL,
                telegram_username TEXT,
                full_name TEXT NOT NULL,
                birthdate TEXT NOT NULL,
                group_name TEXT NOT NULL,
                status TEXT NOT NULL CHECK (
                    status IN ('pending', 'approved', 'rejected')
                ),
                created_at TEXT NOT NULL,
                reviewed_at TEXT,
                reviewed_by INTEGER
            );

            CREATE UNIQUE INDEX IF NOT EXISTS idx_orders_one_active_per_user
            ON orders(telegram_id)
            WHERE status IN ('pending', 'approved');
            """
        )


def create_order(
    telegram_id: int,
    telegram_username: str | None,
    full_name: str,
    birthdate: str,
    group_name: str,
) -> Order:
    try:
        with _connect() as connection:
            cursor = connection.execute(
                """
                INSERT INTO orders (
                    telegram_id,
                    telegram_username,
                    full_name,
                    birthdate,
                    group_name,
                    status,
                    created_at
                )
                VALUES (?, ?, ?, ?, ?, 'pending', ?)
                """,
                (
                    telegram_id,
                    telegram_username,
                    full_name,
                    birthdate,
                    group_name,
                    _current_time(),
                ),
            )
            order_id = cursor.lastrowid
    except sqlite3.IntegrityError as error:
        raise ActiveOrderExistsError from error

    order = get_order(order_id)
    if order is None:
        raise RuntimeError("Created order was not found")
    return order


def get_order(order_id: int) -> Order | None:
    with _connect() as connection:
        row = connection.execute(
            "SELECT * FROM orders WHERE id = ?",
            (order_id,),
        ).fetchone()
    return _row_to_order(row)


def get_active_order_by_telegram_id(telegram_id: int) -> Order | None:
    with _connect() as connection:
        row = connection.execute(
            """
            SELECT *
            FROM orders
            WHERE telegram_id = ?
              AND status IN ('pending', 'approved')
            ORDER BY id DESC
            LIMIT 1
            """,
            (telegram_id,),
        ).fetchone()
    return _row_to_order(row)


def list_orders_by_telegram_id(telegram_id: int) -> list[Order]:
    with _connect() as connection:
        rows = connection.execute(
            """
            SELECT *
            FROM orders
            WHERE telegram_id = ?
            ORDER BY id
            """,
            (telegram_id,),
        ).fetchall()
    return [Order(**dict(row)) for row in rows]


def delete_orders_by_telegram_id(telegram_id: int) -> int:
    with _connect() as connection:
        cursor = connection.execute(
            "DELETE FROM orders WHERE telegram_id = ?",
            (telegram_id,),
        )
    return cursor.rowcount


def update_order_status(
    order_id: int,
    status: str,
    reviewed_by: int,
) -> bool:
    if status not in {"approved", "rejected"}:
        raise ValueError("Unsupported order status")

    with _connect() as connection:
        cursor = connection.execute(
            """
            UPDATE orders
            SET status = ?, reviewed_at = ?, reviewed_by = ?
            WHERE id = ? AND status = 'pending'
            """,
            (status, _current_time(), reviewed_by, order_id),
        )
    return cursor.rowcount == 1


def list_approved_orders() -> list[Order]:
    with _connect() as connection:
        rows = connection.execute(
            """
            SELECT *
            FROM orders
            WHERE status = 'approved'
            ORDER BY full_name COLLATE NOCASE
            """
        ).fetchall()
    return [Order(**dict(row)) for row in rows]
