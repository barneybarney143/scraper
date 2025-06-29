import csv
import argparse
import requests


API_URL = "https://www.vinted.hu/api/v2/catalog/items"


def search_item(query: str, max_price: float) -> bool:
    """Return True if at least one listing is below or equal to max_price."""
    params = {
        "search_text": query,
        "price_to": max_price,
        "per_page": 1,
        "currency": "HUF",
    }
    try:
        resp = requests.get(API_URL, params=params, timeout=10)
        resp.raise_for_status()
        data = resp.json()
    except Exception:
        return False
    return bool(data.get("items"))


def process_csv(path: str) -> list[tuple[str, float, bool]]:
    results = []
    with open(path, newline="", encoding="utf-8") as f:
        reader = csv.reader(f)
        for row in reader:
            if not row:
                continue
            name, price = row[0], float(row[1])
            available = search_item(name, price)
            results.append((name, price, available))
    return results


def main() -> None:
    parser = argparse.ArgumentParser(description="Check Vinted prices for items")
    parser.add_argument("csv", help="CSV file with 'item,price' rows")
    args = parser.parse_args()
    for name, price, available in process_csv(args.csv):
        msg = "van" if available else "nincs"
        print(f"{name} - {price} Ft alatt {msg}")


if __name__ == "__main__":
    main()
