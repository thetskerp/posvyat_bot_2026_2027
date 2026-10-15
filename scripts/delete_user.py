import argparse

from database import delete_orders_by_telegram_id, list_orders_by_telegram_id
from database.database import DATABASE_PATH


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Delete all orders belonging to a Telegram user.",
    )
    parser.add_argument(
        "telegram_id",
        type=int,
        help="Numeric Telegram ID of the user",
    )
    parser.add_argument(
        "--yes",
        action="store_true",
        help="Delete without an interactive confirmation",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()

    if not DATABASE_PATH.exists():
        print(f"База данных не найдена: {DATABASE_PATH}")
        return

    orders = list_orders_by_telegram_id(args.telegram_id)
    if not orders:
        print(f"Заявки Telegram ID {args.telegram_id} не найдены.")
        return

    print(f"Найдено заявок: {len(orders)}")
    for order in orders:
        username = f"@{order.telegram_username}" if order.telegram_username else "не указан"
        print(
            f"- №{order.id}: {order.full_name}, "
            f"{order.birthdate}, {order.group_name}, "
            f"{username}, статус: {order.status}"
        )

    if not args.yes:
        confirmation = input(
            "Для удаления всех заявок этого пользователя "
            "введите DELETE: "
        )
        if confirmation != "DELETE":
            print("Удаление отменено.")
            return

    deleted_count = delete_orders_by_telegram_id(args.telegram_id)
    print(f"Удалено заявок: {deleted_count}")


if __name__ == "__main__":
    main()
