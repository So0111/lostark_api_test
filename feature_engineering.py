import sqlite3
import pandas as pd

DB_PATH = "lostark_prices.db"

conn = sqlite3.connect(DB_PATH)
df = pd.read_sql(
    """
    SELECT 
        item_name,
        DATE(collected_at) as date,
        AVG(current_min_price) as avg_price
    FROM material_prices
    GROUP BY item_name, DATE(collected_at)
    ORDER BY item_name, date
""",
    conn,
)
conn.close()

print(df.head(10))
print(f"\n총 {len(df)}행")


# 아이템별로 피처 계산
def make_features(df):
    result = []

    for item_name, group in df.groupby("item_name"):
        group = group.copy().reset_index(drop=True)

        # 전일 대비 변동률
        group["pct_change"] = group["avg_price"].pct_change() * 100

        # 3일 이동평균
        group["ma3"] = group["avg_price"].rolling(3).mean()

        # 라벨 생성
        def make_label(pct):
            if pct > 5:
                return "상승"
            elif pct < -5:
                return "하락"
            else:
                return "유지"

        group["label"] = group["pct_change"].apply(
            lambda x: make_label(x) if pd.notna(x) else None
        )

        result.append(group)

    return pd.concat(result).dropna()


df_features = make_features(df)
print(df_features.head(10))
print(f"\n총 {len(df_features)}행")
print(f"\n라벨 분포:\n{df_features['label'].value_counts()}")
