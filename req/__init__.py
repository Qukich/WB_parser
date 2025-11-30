import os
import time
from typing import Any, Dict, List, Tuple
import requests
from dotenv import load_dotenv

from work_excel.utils import _basket_code

load_dotenv()

SEARCH_URL = os.getenv("SEARCH_URL")
CARD_URL = os.getenv("CARD_URL")
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0 Win64 x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36",
    "Access-Control-Allow-Credentials": "true",
    "Access-Control-Allow-Headers": "Authorization,Accept,Origin,DNT,User-Agent,Content-Type,Wb-AppType,Wb-AppVersion,Xwbuid,Site-Locale,X-Clientinfo,Storage-Type,Data-Version,Model-Version,__wbl, x-captcha-id",
    "Access-Control-Allow-Methods": "GET,OPTIONS",
    "Access-control-Allow-Origin": "https://www.wildberries.ru",
    "Content-Encoding": "gzip",
    "Content-Type": "application/json charset=utf-8"
}

cookies = {
    "wbx-validation-key": os.getenv("WBX_VALIDATION_KEY"),
    "x_wbaas_token": os.getenv("WBX_TOKEN"),
}

authorization = os.getenv("WB_AUTH_TOKEN")


def send_get_req_catalog(query: str, page: int) -> requests.Response:
    params = {
        "appType": 1,
        "curr": "rub",
        "dest": -1257786,
        "query": query,
        "page": page,
        "resultset": "catalog",
        "Authorization": authorization
    }

    return requests.get(SEARCH_URL, params=params, headers=HEADERS, cookies=cookies, timeout=10)


def get_search_first_page(query: str) -> list[Any] | tuple[Any, Any]:
    r = send_get_req_catalog(query, 1)
    # если слишком часто дергали API — сервер может вернуть 429
    if r.status_code == 429:
        print("?? Wildberries вернул 429 Too Many Requests.")
        print(
            " Это лимит на стороне сайта. Подождите 15–30 минут "
            "и запустите скрипт снова."
        )
        return []
    r.raise_for_status()
    data = r.json()
    products = data.get("products", [])
    if not products:
        print("Запрос не прошел, пробуем ещё раз через 15 секунд.")
        time.sleep(15)
        r = send_get_req_catalog(query, 1)
        r.raise_for_status()
        data = r.json()
        products = data.get("products", [])
    return products, data.get("total")


def get_search_page(query: str, page: int) -> list[Any]:
    r = send_get_req_catalog(query, page)
    # если слишком часто дергали API — сервер может вернуть 429
    if r.status_code == 429:
        print("?? Wildberries вернул 429 Too Many Requests.")
        print(
            " Это лимит на стороне сайта. Подождите 15–30 минут "
            "и запустите скрипт снова."
        )
        return []
    r.raise_for_status()
    data = r.json()
    return data.get("products", [])


def get_cards(ids: List[int], batch_size: int = 100) -> tuple[
    dict[int, dict[str, Any]], dict[str, str], dict[str, str | None]]:
    """
    Получить подробные карточки товаров.
    ids из поисковой выдачи.
    """
    cards: Dict[int, Dict[str, Any]] = {}
    for i in range(0, len(ids), batch_size):
        batch = ids[i: i + batch_size]
        params = {
            "appType": 1,
            "curr": "rub",
            "dest": -1257786,
            "nm": ";".join(str(x) for x in batch),
            "Authorization": authorization
        }

        r = requests.get(CARD_URL, params=params, headers=HEADERS, cookies=cookies, timeout=15)
        if r.status_code == 429:
            print("?? Wildberries вернул 429 на карточки. Ждём 15 секунд и пробуем ещё раз.")
            time.sleep(15)
            r = requests.get(CARD_URL, params=params, headers=HEADERS, cookies=cookies, timeout=15)
        r.raise_for_status()
        data = r.json()
        for p in data.get("products", []):
            pid = p.get("id")
            if pid:
                cards[pid] = p
        time.sleep(1.0)  # маленькая пауза из уважения к API
    return cards, HEADERS, cookies
