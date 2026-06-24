from datetime import date, timedelta

import pandas as pd
import pytest

from services.analysis import (
    classify_strength,
    compute_correlations,
    compute_trend,
    summarize,
)


@pytest.fixture
def sample_df():
    base = date(2024, 1, 1)
    records = []
    for i in range(10):
        records.append(
            {
                "date": base + timedelta(days=i),
                "mood_score": (i % 5) + 1,
                "sleep_hours": 6.0 + (i % 3),
                "temperature": 10.0 + i,
                "humidity": 50 + (i % 20),
                "pressure": 1010.0 + (i % 5),
                "pressure_change": float(i % 3 - 1),  # ← 追加
            }
        )
    df = pd.DataFrame(records)
    df["date"] = pd.to_datetime(df["date"])
    return df.sort_values("date")


class TestClassifyStrength:
    def test_strong_positive(self):
        # 実際のコードは日本語を返す
        assert classify_strength(0.8) == "とても"
        assert classify_strength(-0.8) == "とても"

    def test_moderate(self):
        assert classify_strength(0.5) == "やや"
        assert classify_strength(-0.5) == "やや"

    def test_weak(self):
        assert classify_strength(0.2) == "少し"
        assert classify_strength(-0.2) == "少し"

    def test_boundary_07(self):
        assert classify_strength(0.7) == "とても"

    def test_boundary_04(self):
        assert classify_strength(0.4) == "やや"


class TestSummarize:
    """相関サマリー文のテスト"""

    def test_not_significant(self):
        result = summarize("mood_score", "pressure", 0.5, 0.2)
        assert "明確な関係は見られません" in result

    def test_positive_correlation(self):
        result = summarize("mood_score", "pressure", 0.6, 0.01)
        assert "良くなる傾向" in result
        assert "気圧" in result

    def test_negative_correlation(self):
        result = summarize("mood_score", "humidity", -0.6, 0.01)
        assert "悪くなる傾向" in result
        assert "湿度" in result


class TestComputeCorrelations:
    """相関計算のテスト"""

    def test_result_count(self, sample_df):
        # health_cols(2) × weather_cols(4) = 8件
        results = compute_correlations(sample_df)
        assert len(results) == 8

    def test_required_keys(self, sample_df):
        results = compute_correlations(sample_df)
        required_keys = {
            "health",
            "weather",
            "r",
            "p",
            "significant_05",
            "significant_10",
            "strength",
            "direction",
            "summary",
        }
        for result in results:
            assert required_keys.issubset(result.keys())

    def test_r_value_range(self, sample_df):
        results = compute_correlations(sample_df)
        for result in results:
            assert -1.0 <= result["r"] <= 1.0

    def test_constant_data_no_error(self):
        """全て同じ値のデータでもエラーにならないことを確認"""
        df = pd.DataFrame(
            {
                "date": pd.date_range("2024-01-01", periods=10),
                "mood_score": [3] * 10,
                "sleep_hours": [7.0] * 10,
                "temperature": list(range(10)),
                "humidity": list(range(10)),
                "pressure": list(range(10)),
            }
        )
        results = compute_correlations(df)
        assert isinstance(results, list)


class TestComputeTrend:
    """トレンド計算のテスト"""

    def test_required_keys(self, sample_df):
        trends = compute_trend(sample_df)
        required_keys = {
            "date",
            "mood_score",
            "mood_7d",
            "pressure",
            "pressure_7d",
            "temperature",
            "temperature_7d",
            "humidity",
            "humidity_7d",
        }
        for trend in trends:
            assert required_keys.issubset(trend.keys())

    def test_data_count(self, sample_df):
        trends = compute_trend(sample_df)
        assert len(trends) == len(sample_df)

    def test_mood_7d_is_none_before_7days(self, sample_df):
        """7日分揃わない場合はNoneまたはNaNになる"""
        import math

        trends = compute_trend(sample_df)
        for trend in trends[:6]:
            # NoneまたはNaNであることを確認
            assert trend["mood_7d"] is None or (isinstance(trend["mood_7d"], float) and math.isnan(trend["mood_7d"]))

    def test_mood_7d_calculated_after_7days(self, sample_df):
        """7日分揃った場合は数値が入る"""
        trends = compute_trend(sample_df)
        assert trends[6]["mood_7d"] is not None
