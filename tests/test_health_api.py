import json
from datetime import date


class TestHealthLogCreate:
    def test_create_valid_log(self, client):
        response = client.post(
            "/health",
            data=json.dumps(
                {
                    "mood_score": 4,
                    "sleep_hours": 7.5,
                    "symptom": "頭痛",
                    "note": "テスト",
                    "date": "2024-01-01",  # ← 文字列固定に変更
                }
            ),
            content_type="application/json",
        )
        assert response.status_code == 201
        data = json.loads(response.data)
        assert data["mood_score"] == 4
        assert data["sleep_hours"] == 7.5

    def test_missing_mood_score(self, client):
        response = client.post(
            "/health",
            data=json.dumps({"sleep_hours": 7.5}),
            content_type="application/json",
        )
        assert response.status_code == 400

    def test_mood_score_too_high(self, client):
        response = client.post(
            "/health",
            data=json.dumps({"mood_score": 6}),
            content_type="application/json",
        )
        assert response.status_code == 400

    def test_mood_score_too_low(self, client):
        response = client.post(
            "/health",
            data=json.dumps({"mood_score": 0}),
            content_type="application/json",
        )
        assert response.status_code == 400


class TestHealthLogRead:
    def test_empty_list(self, client):
        response = client.get("/health")
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data == []

    def test_get_all_logs(self, client, sample_health_log):
        response = client.get("/health")
        assert response.status_code == 200
        data = json.loads(response.data)
        assert len(data) == 1
        assert data[0]["mood_score"] == 4

    def test_get_by_id(self, client, sample_health_log):
        # sample_health_log はIDを返す
        response = client.get(f"/health/{sample_health_log}")
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data["mood_score"] == 4

    def test_not_found(self, client):
        response = client.get("/health/9999")
        assert response.status_code == 404


class TestHealthLogUpdate:
    def test_update_mood_score(self, client, sample_health_log):
        response = client.put(
            f"/health/{sample_health_log}",
            data=json.dumps({"mood_score": 2}),
            content_type="application/json",
        )
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data["mood_score"] == 2

    def test_update_invalid_mood_score(self, client, sample_health_log):
        response = client.put(
            f"/health/{sample_health_log}",
            data=json.dumps({"mood_score": 10}),
            content_type="application/json",
        )
        assert response.status_code == 400


class TestHealthLogDelete:
    def test_delete_log(self, client, sample_health_log):
        response = client.delete(f"/health/{sample_health_log}")
        assert response.status_code == 200
        # 削除後は404
        response = client.get(f"/health/{sample_health_log}")
        assert response.status_code == 404

    def test_delete_not_found(self, client):
        response = client.delete("/health/9999")
        assert response.status_code == 404
