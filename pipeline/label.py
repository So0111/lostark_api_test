# pipeline/label.py
import pandas as pd
from pipeline.feature import make_features
from pipeline.load import load_materials, load_gems

THRESHOLD = 5.0  # ±5% 기준


def make_labels(df: pd.DataFrame, threshold: float = 5.0) -> pd.DataFrame:
    df = df.copy()

    def label_fn(pct):
        if pct > threshold:
            return "상승"
        elif pct < -threshold:
            return "하락"
        else:
            return "유지"

    # 다음날 pct_change를 라벨로 (오늘 피처 → 내일 방향 예측)
    df["next_pct"] = df.groupby(
        [c for c in df.columns if c in ["item_name", "gem_type", "gem_level"]]
    )["pct_change"].shift(-1)

    df["label"] = df["next_pct"].apply(lambda x: label_fn(x) if pd.notna(x) else None)

    return df.dropna(subset=["label"]).reset_index(drop=True)


if __name__ == "__main__":
    mat = load_materials()
    mat_feat = make_features(mat, ["item_name"])
    mat_labeled = make_labels(mat_feat)

    print("=== 라벨 분포 (재료) ===")
    print(mat_labeled["label"].value_counts())
    print(f"\n총 {len(mat_labeled)}행")
