"""Backend regression tests for Estudio.Química.
Focus of iteration 7: open-answers/grade endpoint (new) + prior endpoints still working."""
import os
import pytest
import requests

BASE_URL = os.environ.get("REACT_APP_BACKEND_URL", "https://study-complete-7.preview.emergentagent.com").rstrip("/")
API = f"{BASE_URL}/api"


@pytest.fixture(scope="module")
def topics():
    r = requests.get(f"{API}/topics", timeout=30)
    assert r.status_code == 200
    data = r.json()
    assert isinstance(data, list) and len(data) > 0
    return data


@pytest.fixture(scope="module")
def open_exercise(topics):
    """Find first exercise with type == 'open'."""
    for t in topics:
        r = requests.get(f"{API}/topics/{t['id']}/exercises", timeout=30)
        if r.status_code != 200:
            continue
        for ex in r.json():
            if ex.get("type") == "open":
                return ex
    pytest.skip("No open exercise available")


# ---------- Health / basics ----------
class TestBasics:
    def test_topics_endpoint(self, topics):
        assert len(topics) >= 4
        assert all("id" in t and "title" in t and "module" in t for t in topics)

    def test_topic_exercises(self, topics):
        t = topics[0]
        r = requests.get(f"{API}/topics/{t['id']}/exercises", timeout=30)
        assert r.status_code == 200
        exs = r.json()
        assert isinstance(exs, list) and len(exs) > 0

    def test_progress_endpoint(self):
        sid = "TEST_session_iter7"
        r = requests.get(f"{API}/progress/{sid}", timeout=30)
        assert r.status_code == 200
        p = r.json()
        for k in ("total", "correct", "accuracy", "per_topic"):
            assert k in p


# ---------- NEW: open-answers/grade ----------
class TestOpenAnswersGrade:
    def test_grade_returns_structured_json(self, open_exercise):
        payload = {
            "exercise_id": open_exercise["id"],
            "answer_text": "A velocidade média é calculada dividindo a variação da concentração pela variação do tempo."
        }
        r = requests.post(f"{API}/open-answers/grade", json=payload, timeout=90)
        assert r.status_code == 200, f"Body: {r.text}"
        data = r.json()
        # Required keys per PRD
        for k in ("nota", "acertos", "faltou", "proximos_passos"):
            assert k in data, f"Missing key {k} in {data}"
        # nota must be a number 0-10
        nota = data["nota"]
        assert isinstance(nota, (int, float)) or (isinstance(nota, str) and nota.replace(".", "").isdigit())
        n = float(nota)
        assert 0 <= n <= 10

    def test_grade_missing_exercise(self):
        payload = {"exercise_id": "NON_EXISTENT_ID", "answer_text": "x"}
        r = requests.post(f"{API}/open-answers/grade", json=payload, timeout=30)
        assert r.status_code == 404


# ---------- Prior features regression ----------
class TestPriorFeatures:
    def test_summary_endpoint(self, topics):
        r = requests.get(f"{API}/topics/{topics[0]['id']}/summary", timeout=30)
        # 200 or 404 (no summary yet) both acceptable
        assert r.status_code in (200, 404)

    def test_submit_mcq_answer(self, topics):
        # Find MCQ
        for t in topics:
            exs = requests.get(f"{API}/topics/{t['id']}/exercises", timeout=30).json()
            for ex in exs:
                if ex.get("type") == "mcq":
                    payload = {
                        "session_id": "TEST_session_iter7",
                        "exercise_id": ex["id"],
                        "selected_index": 0,
                    }
                    r = requests.post(f"{API}/exercises/answer", json=payload, timeout=30)
                    assert r.status_code == 200
                    d = r.json()
                    assert "correct" in d
                    return
        pytest.skip("No MCQ exercise found")

    def test_save_open_answer(self, open_exercise):
        payload = {
            "session_id": "TEST_session_iter7",
            "exercise_id": open_exercise["id"],
            "answer_text": "TEST resposta",
        }
        r = requests.post(f"{API}/open-answers", json=payload, timeout=30)
        assert r.status_code == 200

    def test_revision_endpoint(self):
        r = requests.get(f"{API}/revision/questions", params={"session_id": "TEST_session_iter7", "limit": 5}, timeout=30)
        assert r.status_code == 200
        assert isinstance(r.json(), list)
