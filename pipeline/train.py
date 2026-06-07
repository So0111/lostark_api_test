# pipeline/train.py
import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.naive_bayes import GaussianNB
from sklearn.model_selection import TimeSeriesSplit
from sklearn.preprocessing import StandardScaler
from pipeline.load import load_materials
from pipeline.feature import make_features
from pipeline.label import make_labels

FEATURE_COLS = ["daily_avg", "daily_std", "daily_entropy", "ma3", "ma7", "pct_change"]
FEATURE_COLS_NO_ENTROPY = [c for c in FEATURE_COLS if c != "daily_entropy"]

MODELS = {
    "RandomForest": RandomForestClassifier(
        n_estimators=100, class_weight="balanced", random_state=42
    ),
    "LogisticRegression": LogisticRegression(
        class_weight="balanced", max_iter=3000, solver="saga", random_state=42
    ),
    "GaussianNB": GaussianNB(),
}


def train_evaluate(df: pd.DataFrame, feature_cols: list) -> dict:
    from sklearn.preprocessing import StandardScaler
    from sklearn.metrics import f1_score

    X = df[feature_cols].values
    y = df["label"].values

    scaler = StandardScaler()
    X = scaler.fit_transform(X)

    tscv = TimeSeriesSplit(n_splits=5)
    results = {}

    for name, model in MODELS.items():
        from sklearn.metrics import f1_score

        f1_scores = []

        for train_idx, test_idx in tscv.split(X):
            X_train, X_test = X[train_idx], X[test_idx]
            y_train, y_test = y[train_idx], y[test_idx]
            model.fit(X_train, y_train)
            y_pred = model.predict(X_test)
            f1_scores.append(f1_score(y_test, y_pred, average="macro", zero_division=0))

        results[name] = round(sum(f1_scores) / len(f1_scores), 4)

    return results


if __name__ == "__main__":
    mat = load_materials()
    mat_feat = make_features(mat, ["item_name"])

    thresholds = [2.0, 3.0, 5.0, 7.0, 10.0]
    print("=== Threshold 실험 (엔트로피 포함) ===")
    print(f"{'threshold':>10} {'RF':>8} {'LR':>8} {'NB':>8} {'유지%':>8}")

    for t in thresholds:
        mat_labeled = make_labels(mat_feat, threshold=t)
        stay_pct = round((mat_labeled["label"] == "유지").mean() * 100, 1)
        r = train_evaluate(mat_labeled, FEATURE_COLS)
        print(
            f"{t:>10} {r['RandomForest']:>8} {r['LogisticRegression']:>8} {r['GaussianNB']:>8} {stay_pct:>7}%"
        )

    print("\n=== Threshold 실험 (엔트로피 제외) ===")
    print(f"{'threshold':>10} {'RF':>8} {'LR':>8} {'NB':>8}")

    for t in thresholds:
        mat_labeled = make_labels(mat_feat, threshold=t)
        r = train_evaluate(mat_labeled, FEATURE_COLS_NO_ENTROPY)
        print(
            f"{t:>10} {r['RandomForest']:>8} {r['LogisticRegression']:>8} {r['GaussianNB']:>8}"
        )
