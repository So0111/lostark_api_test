import requests
import sqlite3
import os
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()

API_KEY = os.environ.get("LOSTARK_API_KEY")
BASE_URL = "https://developer-lostark.game.onstove.com"
DB_PATH = "lostark_prices.db"

headers = {
    "accept": "application/json",
    "Content-Type": "application/json",
    "authorization": f"bearer {API_KEY}",
}


def get_all_items(category_code: int):
    """페이지네이션으로 카테고리 전체 수집"""
    all_items = []
    page = 1
    while True:
        r = requests.post(
            f"{BASE_URL}/markets/items",
            headers=headers,
            json={
                "CategoryCode": category_code,
                "PageNo": page,
                "Sort": "PRICE",
                "SortCondition": "ASC",
            },
        )
        if r.status_code != 200:
            print(f"API 오류 {r.status_code}")
            break
        data = r.json()
        items = data.get("Items", [])
        if not items:
            break
        all_items.extend(items)
        total = data.get("TotalCount", 0)
        if page * len(items) >= total:
            break
        page += 1
    return all_items


def load_material_meta(conn):
    """item_meta에서 강화재료 목록 → 이름 기준으로 불러오기"""
    cursor = conn.cursor()
    cursor.execute("""
        SELECT item_name, item_id, category_code, category_name, item_grade
        FROM item_meta
        WHERE item_type = 'MATERIAL'
    """)
    # {item_name: (item_id, category_code, category_name, item_grade)}
    return {row[0]: row[1:] for row in cursor.fetchall()}


def save_material_prices(conn, items: list, meta: dict, collected_at: str):
    """아이템 이름 기준으로 매칭해서 저장"""
    cursor = conn.cursor()
    saved = 0

    for item in items:
        item_name = item.get("Name")

        # 이름 기준 매칭
        if item_name not in meta:
            continue

        item_id, category_code, category_name, item_grade = meta[item_name]

        cursor.execute(
            """
            INSERT INTO material_prices
            (category_code, category_name, item_id, item_name, item_grade,
             current_min_price, yesterday_avg_price, trade_count, collected_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
            (
                category_code,
                category_name,
                item.get("Id"),  # API에서 받은 실제 ID로 저장
                item_name,
                item_grade,
                item.get("CurrentMinPrice"),
                item.get("YDayAvgPrice"),
                item.get("TradeCount"),
                collected_at,
            ),
        )
        saved += 1

    conn.commit()
    return saved


def main():
    collected_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print(f"=== 강화재료 수집 시작: {collected_at} ===\n")

    conn = sqlite3.connect(DB_PATH)
    meta = load_material_meta(conn)
    print(f"수집 대상: {len(meta)}개 아이템\n")

    total_saved = 0

    for category_code in [50010, 50020]:
        print(f"[{category_code}] 수집 중...")
        items = get_all_items(category_code)
        print(f"[{category_code}] API 응답: {len(items)}개")

        saved = save_material_prices(conn, items, meta, collected_at)
        total_saved += saved
        print(f"[{category_code}] 저장 완료: {saved}개\n")

    conn.close()
    print(f"총 {total_saved}개 저장 완료 ({collected_at})")

    verify(collected_at)


def verify(collected_at: str):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute(
        """
        SELECT item_name, current_min_price, yesterday_avg_price
        FROM material_prices
        WHERE collected_at = ?
        ORDER BY category_code, current_min_price
    """,
        (collected_at,),
    )
    rows = cursor.fetchall()
    print(f"\n=== 저장 데이터 확인 ({len(rows)}개) ===")
    for row in rows:
        print(f"  {row[0]:35s} | 현재가: {row[1]:>8,} | 전일평균: {row[2]:>8.1f}")
    conn.close()


if __name__ == "__main__":
    main()
