from typing import Any, Dict, List

import requests


def extract_sizes(card: Dict[str, Any]) -> str:
    """Размеры товара через запятую."""
    sizes = []
    for s in card.get("sizes", []):
        name = s.get("name") or s.get("origName")
        if name:
            sizes.append(str(name))
    return ",".join(sizes)


def extract_stock(card: Dict[str, Any]) -> int:
    """Остатки по товару (число)."""
    if "totalQuantity" in card:
        try:
            return int(card.get("totalQuantity") or 0)
        except (TypeError, ValueError):
            return 0
    total = 0
    for size in card.get("sizes", []):
        for stock in size.get("stocks", []):
            qty = stock.get("qty")
            if isinstance(qty, (int, float)):
                total += qty
    return int(total)


def build_image_links(product_id: int, pics: int) -> str:
    """Сформировать ссылки на картинки товара через запятую."""
    if not pics or pics <= 0:
        return ""
    basket = _basket_code(product_id)
    vol = product_id // 100000
    part = product_id // 1000
    urls = []
    for i in range(1, pics + 1):
        url = (
            f"https://basket-{basket}.wbbasket.ru/vol{vol}/part{part}/{product_id}/images/big/{i}.webp"
        )
        urls.append(url)
    return ",".join(urls)


def _basket_code(product_id: int) -> str:
    """Подбор корзины для формирования ссылок на изображения."""
    # в идеале по этой ссылке доставать актуальную информацию по баскетам
    # checkBuskUrl = "https://cdn.wbbasket.ru/api/v3/upstreams"
    short = product_id // 100000
    ranges = [
        (143, "01"),
        (287, "02"),
        (431, "03"),
        (719, "04"),
        (1007, "05"),
        (1061, "06"),
        (1115, "07"),
        (1169, "08"),
        (1313, "09"),
        (1601, "10"),
        (1655, "11"),
        (1919, "12"),
        (2045, "13"),
        (2189, "14"),
        (2405, "15"),
        (2621, "16"),
        (2837, "17"),
        (3053, "18"),
        (3269, "19"),
        (3485, "20"),
        (3701, "21"),
        (3917, "22"),
        (4133, "23"),
        (4349, "24"),
        (4565, "25"),
        (4877, "26"),
        (5189, "27"),
        (5501, "28"),
        (5813, "29"),
        (6125, "30"),
        (6437, "31"),
        (6749, "32"),
        (7061, "33"),
        (7373, "34"),
        (7685, "35"),
        (7997, "36"),
        (8309, "37"),
    ]

    for upper, code in ranges:
        if short <= upper:
            return code


def extract_characteristics(product_id: int, HEADERS: any, cookies: any) -> tuple[
    Any, list[tuple[Any, Any] | tuple[str, Any]], Any]:
    country = ""
    basket = _basket_code(product_id)
    vol = product_id // 100000
    part = product_id // 1000

    url = (
        f"https://basket-{basket}.wbbasket.ru/vol{vol}/part{part}/{product_id}/info/ru/card.json"
    )

    r = requests.get(url, headers=HEADERS, cookies=cookies, timeout=15)
    data = r.json()
    characteristics = []
    description = data.get("description")
    if data.get("options") is not None:
        for val in data.get("options"):
            name = val.get("name")
            value = val.get("value")
            if name == "Страна производства":
                country = value
            characteristics.append((name, value))
    else:
        characteristics.append(("Характеристика", description))

    return description, characteristics, country


def merge(search_items: List[Dict[str, Any]],
          cards: Dict[int, Dict[str, Any]],
          headers: any, cookies: any) -> List[Dict[str, Any]]:
    """Собрать финальный список словарей для выгрузки в Excel."""
    rows: List[Dict[str, Any]] = []
    for item in search_items:
        pid = item.get("id")
        if not pid:
            continue
        card = cards.get(pid, {})
        url = f"https://www.wildberries.ru/catalog/{pid}/detail.aspx"
        article = pid
        name = card.get("name") or item.get("name") or ""
        base_price_u = ""
        product_price_u = ""
        i = 0
        while base_price_u == "":
            if card.get("sizes")[i].get("price") is not None:
                base_price_u = card.get("sizes")[i].get("price").get("basic")
                product_price_u = card.get("sizes")[i].get("price").get("product")
            i += 1

        base_price = int(base_price_u) / 100 if base_price_u else 0
        product_price = int(product_price_u) / 100 if product_price_u else 0
        description, characteristics, country = extract_characteristics(pid, headers, cookies)
        pics = card.get("pics") or item.get("pics") or 0
        image_links = build_image_links(pid, pics)
        seller_name = (
                card.get("supplier")
                or card.get("supplierName")
                or item.get("supplier")
                or ""
        )
        seller_id = card.get("supplierId") or item.get("supplierId")
        seller_url = f"https://www.wildberries.ru/seller/{seller_id}" if seller_id else ""
        sizes = extract_sizes(card)
        stock = extract_stock(card)
        rating = (
                card.get("supplierRating")
                or card.get("rating")
                or item.get("rating")
                or 0
        )
        rating = float(rating) if rating not in (None, "") else 0.0
        feedbacks = item.get("feedbacks") or card.get("feedbacks") or 0
        rows.append(
            {
                "Ссылка на товар": url,
                "Артикул": article,
                "Название": name,
                "Базовая цена товара": base_price,
                "Цена товара": product_price,
                "Описание": description,
                "Ссылки на изображения": image_links,
                "Все характеристики": characteristics,
                "Название селлера": seller_name,
                "Ссылка на селлера": seller_url,
                "Размеры товара": sizes,
                "Остатки по товару": stock,
                "Рейтинг": rating,
                "Количество отзывов": feedbacks,
                "Страна производства": country
            }
        )
    return rows
