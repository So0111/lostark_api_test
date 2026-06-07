# pipeline/01_load.py
import sqlite3
import pandas as pd
from pathlib import Path

DB_PATH = Path(__file__).parent.parent / "lostark_prices.db"


def load_materials() -> pd.DataFrame:
    conn = sqlite3.connect(DB_PATH)
    df = pd.read_sql(
        """
        SELECT
            item_id,
            item_name,
            current_min_price,
            datetime(collected_at, '+9 hours') as collected_at_kst
        FROM material_prices
        WHERE DATE(collected_at) >= '2026-04-17'
        ORDER BY item_name, collected_at
    """,
        conn,
    )
    conn.close()
    df["collected_at_kst"] = pd.to_datetime(df["collected_at_kst"])
    return df


def load_gems() -> pd.DataFrame:
    conn = sqlite3.connect(DB_PATH)
    df = pd.read_sql(
        """
        SELECT
            gem_type,
            gem_level,
            current_min_price,
            datetime(collected_at, '+9 hours') as collected_at_kst
        FROM gem_prices
        WHERE DATE(collected_at) >= '2026-04-17'
        ORDER BY gem_type, gem_level, collected_at
    """,
        conn,
    )
    conn.close()
    df["collected_at_kst"] = pd.to_datetime(df["collected_at_kst"])
    return df


if __name__ == "__main__":
    mat = load_materials()
    gem = load_gems()
    print("=== 재료 ===")
    print(mat.head())
    print(f"총 {len(mat)}행, 아이템 {mat['item_name'].nunique()}종")
    print("\n=== 보석 ===")
    print(gem.head())
    print(f"총 {len(gem)}행")
