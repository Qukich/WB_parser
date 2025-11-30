from typing import Any, Dict, List
import pandas as pd


def save_excels_first(rows: List[Dict[str, Any]],
                      full_name: str = "wb_coats_full.xlsx",
                      filtered_name: str = "wb_coats_filtered.xlsx"):
    """Сохранить полный файл и отфильтрованный."""
    if not rows:
        print(
            "\n? Данных нет. Либо WB ничего не вернул по запросу,"
            " либо сработало ограничение по частоте запросов."
        )
        print("Файлы Excel не созданы.")
        return
    df = pd.DataFrame(rows)
    df.to_excel(full_name, index=False)
    filtered = df[
        (df["Рейтинг"] >= 4.5)
        & (df["Цена товара"] <= 10000)
        & (df["Страна производства"].str.lower() == "россия")
        ]
    filtered.to_excel(filtered_name, index=False)


def save_excels(rows: List[Dict[str, Any]],
                full_name: str = "wb_coats_full.xlsx",
                filtered_name: str = "wb_coats_filtered.xlsx"):
    """Сохранить полный файл и отфильтрованный."""
    if not rows:
        print(
            "\n? Данных нет. Либо WB ничего не вернул по запросу,"
            " либо сработало ограничение по частоте запросов."
        )
        return
    df_new = pd.DataFrame(rows)
    filtered_new = df_new[
        (df_new["Рейтинг"] >= 4.5)
        & (df_new["Цена товара"] <= 10000)
        & (df_new["Страна производства"].str.lower() == "россия")
        ]

    df = pd.read_excel(full_name)
    df_new = pd.concat([df, df_new], ignore_index=True)
    df_new.to_excel(full_name, index=False)

    filtered = pd.read_excel(filtered_name)
    filtered_new = pd.concat([filtered, filtered_new], ignore_index=True)
    filtered_new.to_excel(filtered_name, index=False)
