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

# T4 보석 수집 대상 (6~10레벨)
# 실제 아이템 이름 형식: "6레벨 겁화의 보석", "6레벨 작열의 보석"
GEM_TARGETS = [
    ("겁화", 6),
    ("겁화", 7),
    ("겁화", 8),
    ("겁화", 9),
    ("겁화", 10),
    ("작열", 6),
    ("작열", 7),
    ("작열", 8),
    ("작열", 9),
    ("작열", 10),
]


def get_gem_price(gem_type: str, gem_level: int):
    """
    경매장 API로 보석 조회
    실제 아이템 이름: "6레벨 겁화의 보석"
    """
    url = f"{BASE_URL}/auctions/items"
    item_name = f"{gem_level}레벨 {gem_type}의 보석"

    body = {
        "CategoryCode": 210000,
        "ItemTier": 4,
        "ItemName": item_name,
        "Sort": "BUY_PRICE",
        "SortCondition": "ASC",
        "PageNo": 1,
        "SkillOptions": [],
        "EtcOptions": [],
    }

    response = requests.post(url, headers=headers, json=body)

    if response.status_code == 200:
        return response.json()
    else:
        print(f"  오류 {response.status_code}: {response.text}")
        return None


def save_gem_price(conn, gem_type: str, gem_level: int, data: dict, collected_at: str):
    """
    보석 가격 저장 - 즉시구매가 기준 최저가
    """
    if data is None:
        return 0

    cursor = conn.cursor()
    items = data.get("Items") or []

    if not items:
        return 0

    # 즉시구매가 있는 매물만 필터링
    buy_prices = []
    for item in items:
        auction = item.get("AuctionInfo") or {}
        bp = auction.get("BuyPrice")
        if bp:
            buy_prices.append(bp)

    if not buy_prices:
        return 0

    min_price = min(buy_prices)

    cursor.execute(
        """
        INSERT INTO gem_prices
        (gem_type, gem_level, item_id, current_min_price, yesterday_avg_price, trade_count, collected_at)
        VALUES (?, ?, NULL, ?, NULL, ?, ?)
    """,
        (gem_type, gem_level, min_price, len(buy_prices), collected_at),
    )

    conn.commit()
    return 1


def main():
    collected_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print(f"=== 보석 수집 시작: {collected_at} ===\n")

    conn = sqlite3.connect(DB_PATH)
    total_saved = 0

    for gem_type, gem_level in GEM_TARGETS:
        item_name = f"{gem_level}레벨 {gem_type}의 보석"
        print(f"[{item_name}] 조회 중...")

        data = get_gem_price(gem_type, gem_level)
        saved = save_gem_price(conn, gem_type, gem_level, data, collected_at)
        total_saved += saved

        if data:
            items = data.get("Items") or []
            buy_prices = [
                item.get("AuctionInfo", {}).get("BuyPrice")
                for item in items
                if (item.get("AuctionInfo") or {}).get("BuyPrice")
            ]
            if buy_prices:
                print(
                    f"  → 최저가: {min(buy_prices):,} | 즉시구매 매물: {len(buy_prices)}개"
                )
            else:
                print(f"  → 즉시구매가 있는 매물 없음 (총 {len(items)}개)")
        else:
            print(f"  → API 오류")

    conn.close()
    print(f"\n총 {total_saved}개 저장 완료 ({collected_at})")

    verify(collected_at)


def verify(collected_at: str):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute(
        """
        SELECT gem_type, gem_level, current_min_price, trade_count
        FROM gem_prices
        WHERE collected_at = ?
        ORDER BY gem_type, gem_level
    """,
        (collected_at,),
    )
    rows = cursor.fetchall()
    print(f"\n=== 보석 저장 데이터 확인 ({len(rows)}개) ===")
    for row in rows:
        print(
            f"  T4 {row[0]} {row[1]}레벨 | 최저가: {row[2]:>10,} | 즉시구매 매물: {row[3]}개"
        )
    conn.close()


if __name__ == "__main__":
    main()
