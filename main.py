import os

from dotenv import load_dotenv

from req import get_search_first_page, get_cards, get_search_page
from work_excel.utils import merge
from work_excel import save_excels, save_excels_first

load_dotenv()

QUERY = os.getenv("QUERY")


# ----------------------------- main -----------------------------
def main():
    print(f"Запрос: {QUERY!r}")
    search_items, total_items = get_search_first_page(QUERY)
    total_page = int(total_items / 100)
    print(f"Найдено в поиске (1 страница): {len(search_items)} товаров")
    ids = [p["id"] for p in search_items if "id" in p]
    cards, headers, cookies = get_cards(ids)
    print(f"Получено карточек: {len(cards)}")
    rows = merge(search_items, cards, headers, cookies)
    save_excels_first(rows)
    for i in range(2, total_page + 1):
        search_items = get_search_page(QUERY, i)
        print(f"Найдено в поиске ({i} страница): {len(search_items)} товаров")
        ids = [p["id"] for p in search_items if "id" in p]
        cards, headers, cookies = get_cards(ids)
        print(f"Получено карточек: {len(cards)}")
        rows = merge(search_items, cards, headers, cookies)
        save_excels(rows)

    if rows:
        print("\nГотово.")
        print("Полный каталог: wb_coats_full.xlsx")
        print("Отфильтрованный каталог: wb_coats_filtered.xlsx")


if __name__ == "__main__":
    main()
