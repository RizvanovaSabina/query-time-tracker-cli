import argparse
import sys
import time
import re

import requests
from requests.exceptions import RequestException


def validate_host(host):
    pattern = r'https://[a-zA-Z0-9][a-zA-Z0-9-]*\.[a-zA-Z0-9]{2,}'
    match = re.fullmatch(pattern, host)
    return bool(match)


def validate_count(count):
    return isinstance(count, int)


def parse_args():
    """
    Парсит аргументы из терминала и возвращает hosts и count в удобном для работы виде
    """
    parser = argparse.ArgumentParser(
        description="Тестирование доступности серверов по HTTP."
    )
    parser.add_argument(
        "-H", "--hosts",
        required=True,
        help="Список URL через запятую без пробелов (например, https://ya.ru,https://google.com)"
    )
    parser.add_argument(
        "-C", "--count",
        default=1,
        help="Количество запросов на каждый хост (по умолчанию 1)"
    )
    args = parser.parse_args()

    hosts = [h.strip() for h in args.hosts.split(",") if h.strip()]
    if not hosts:
        parser.error("Список хостов не может быть пустым.")

    for host in hosts:
        if not validate_host(host):
            parser.error(f"Недопустимое имя хоста: {host}")

    if not validate_count(args.count):
        parser.error("Количество запросов должно быть целочисленным")

    if args.count <= 0:
        parser.error("Количество запросов должно быть положительным числом.")

    return hosts, args.count


def test_host(host, count):
    """
    Выполняет count запросов к указанному хосту и возвращает статистику
    """
    stats = {
        "success": 0,
        "failed": 0,
        "errors": 0,
        "times": []
    }

    for i in range(count):
        try:
            start = time.perf_counter()
            response = requests.get(host, timeout=10)
            elapsed = time.perf_counter() - start

            if response.status_code < 400:
                stats["success"] += 1
            else:
                stats["failed"] += 1

            stats["times"].append(elapsed)

        except RequestException as e:
            stats["errors"] += 1
            print(f"Ошибка при запросе к {host}: {e}", file=sys.stderr)

    return stats


def print_stats(host, stats):
    """
    Выводит статистику по одному хосту в человеко-читаемом формате
    """
    times = stats["times"]
    if times:
        min_time = min(times)
        max_time = max(times)
        avg_time = sum(times) / len(times)
    else:
        min_time = max_time = avg_time = 0.0

    print(f"Host: {host}")
    print(f"  Success:  {stats['success']}")
    print(f"  Failed:   {stats['failed']}")
    print(f"  Errors:   {stats['errors']}")
    print(f"  Min:      {min_time:.3f}s")
    print(f"  Max:      {max_time:.3f}s")
    print(f"  Avg:      {avg_time:.3f}s")
    print()


def main():
    hosts, count = parse_args()

    for host in hosts:
        stats = test_host(host, count)
        print_stats(host, stats)


if __name__ == "__main__":
    main()
