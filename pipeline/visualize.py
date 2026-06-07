# pipeline/visualize.py
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import pandas as pd
from pipeline.load import load_materials, load_gems
from pipeline.feature import make_features

plt.rcParams["font.family"] = "Malgun Gothic"
plt.rcParams["axes.unicode_minus"] = False


def plot_material_features(df: pd.DataFrame, items: list = None):
    if items is None:
        items = [
            "운명의 파괴석",
            "운명의 파괴석 결정",
            "운명의 수호석 결정",
            "운명의 파편 주머니(대)",
        ]

    fig, axes = plt.subplots(4, 1, figsize=(14, 16))
    colors = ["tab:red", "tab:orange", "tab:blue", "tab:green"]

    for item, color in zip(items, colors):
        g = df[df["item_name"] == item].copy()
        g["date"] = pd.to_datetime(g["date"])

        # 가격 + 이동평균
        axes[0].plot(g["date"], g["daily_avg"], label=item, color=color, linewidth=1.5)
        axes[0].plot(
            g["date"], g["ma3"], color=color, linestyle="--", linewidth=1, alpha=0.6
        )
        axes[0].plot(
            g["date"], g["ma7"], color=color, linestyle=":", linewidth=1, alpha=0.4
        )

        # pct_change
        axes[1].plot(
            g["date"],
            g["pct_change"],
            label=item,
            color=color,
            linewidth=1.5,
            marker="o",
            markersize=3,
        )

        # entropy
        axes[2].plot(
            g["date"], g["daily_entropy"], label=item, color=color, linewidth=1.5
        )

        # daily_std
        axes[3].plot(g["date"], g["daily_std"], label=item, color=color, linewidth=1.5)

    titles = [
        "가격 추이 (실선=avg, 점선=ma3, 점점선=ma7)",
        "전일 대비 변동률 (%)",
        "Shannon Entropy",
        "일별 표준편차",
    ]
    ylabels = ["최저가", "%", "entropy", "std"]

    for ax, title, ylabel in zip(axes, titles, ylabels):
        ax.set_title(title, fontsize=11)
        ax.set_ylabel(ylabel)
        ax.legend(fontsize=8)
        ax.xaxis.set_major_formatter(mdates.DateFormatter("%m/%d"))
        ax.xaxis.set_major_locator(mdates.DayLocator(interval=3))
        ax.grid(True, alpha=0.3)
        ax.axhline(0, color="black", linewidth=0.5, alpha=0.5)

    plt.suptitle("재료 피처 시각화", fontsize=13, fontweight="bold")
    plt.tight_layout()
    plt.savefig("material_features.png", dpi=150, bbox_inches="tight")
    plt.show()


def plot_gem_features(df: pd.DataFrame, gem_type: str = "겁화"):
    g = df[df["gem_type"] == gem_type].copy()
    g["date"] = pd.to_datetime(g["date"])
    levels = sorted(g["gem_level"].unique())
    colors = ["tab:blue", "tab:orange", "tab:red", "tab:purple", "tab:green"]

    fig, axes = plt.subplots(3, 1, figsize=(14, 12))

    for level, color in zip(levels, colors):
        lg = g[g["gem_level"] == level]

        axes[0].plot(
            lg["date"],
            lg["daily_avg"],
            label=f"{level}레벨",
            color=color,
            linewidth=1.5,
        )
        axes[1].plot(
            lg["date"],
            lg["pct_change"],
            label=f"{level}레벨",
            color=color,
            linewidth=1.5,
            marker="o",
            markersize=3,
        )
        axes[2].plot(
            lg["date"],
            lg["daily_entropy"],
            label=f"{level}레벨",
            color=color,
            linewidth=1.5,
        )

    titles = ["가격 추이", "전일 대비 변동률 (%)", "Shannon Entropy"]
    ylabels = ["최저가", "%", "entropy"]

    for ax, title, ylabel in zip(axes, titles, ylabels):
        ax.set_title(f"{gem_type} {title}", fontsize=11)
        ax.set_ylabel(ylabel)
        ax.legend(fontsize=8)
        ax.xaxis.set_major_formatter(mdates.DateFormatter("%m/%d"))
        ax.xaxis.set_major_locator(mdates.DayLocator(interval=3))
        ax.grid(True, alpha=0.3)
        ax.axhline(0, color="black", linewidth=0.5, alpha=0.5)

    plt.suptitle(f"보석({gem_type}) 피처 시각화", fontsize=13, fontweight="bold")
    plt.tight_layout()
    plt.savefig(f"gem_{gem_type}_features.png", dpi=150, bbox_inches="tight")
    plt.show()


if __name__ == "__main__":
    mat = load_materials()
    gem = load_gems()

    mat_feat = make_features(mat, ["item_name"])
    gem_feat = make_features(gem, ["gem_type", "gem_level"])

    plot_material_features(mat_feat)
    plot_gem_features(gem_feat, "겁화")
    plot_gem_features(gem_feat, "작열")
