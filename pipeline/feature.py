# pipeline/feature.py
import pandas as pd
import numpy as np
from scipy.stats import entropy as scipy_entropy
from pipeline.load import load_materials, load_gems


def calc_entropy(prices: pd.Series) -> float:
    if len(prices) < 2:
        return 0.0
    # 가격을 히스토그램으로 변환 후 확률분포 계산
    counts, _ = np.histogram(prices, bins=5)
    counts = counts[counts > 0]
    probs = counts / counts.sum()
    return scipy_entropy(probs)


def make_features(df: pd.DataFrame, group_cols: list) -> pd.DataFrame:
    result = []

    for keys, group in df.groupby(group_cols):
        group = group.copy().sort_values("collected_at_kst").reset_index(drop=True)

        # 일별 집계
        group["date"] = group["collected_at_kst"].dt.date
        daily = (
            group.groupby("date")["current_min_price"]
            .agg(
                daily_avg="mean",
                daily_std="std",
                daily_entropy=lambda x: calc_entropy(x),
            )
            .reset_index()
        )

        # 이동평균
        daily["ma3"] = daily["daily_avg"].rolling(3).mean()
        daily["ma7"] = daily["daily_avg"].rolling(7).mean()

        # 전일 대비 변동률
        daily["pct_change"] = daily["daily_avg"].pct_change() * 100

        # 그룹 키 추가
        if isinstance(keys, tuple):
            for col, val in zip(group_cols, keys):
                daily[col] = val
        else:
            daily[group_cols[0]] = keys

        result.append(daily)

    return pd.concat(result).dropna().reset_index(drop=True)


if __name__ == "__main__":
    mat = load_materials()
    gem = load_gems()

    mat_feat = make_features(mat, ["item_name"])
    gem_feat = make_features(gem, ["gem_type", "gem_level"])

    print("=== 재료 피처 ===")
    print(mat_feat.head())
    print(f"총 {len(mat_feat)}행")
    print(f"컬럼: {list(mat_feat.columns)}")

    print("\n=== 보석 피처 ===")
    print(gem_feat.head())
    print(f"총 {len(gem_feat)}행")
