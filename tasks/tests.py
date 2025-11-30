from django.test import TestCase
from .scoring import calculate_task_score

class ScoringTests(TestCase):
    def test_overdue_boost(self):
        task = {"id":1, "title":"old", "due_date":"2000-01-01", "estimated_hours":2, "importance":5, "dependencies":[]}
        score, explanation, flags = calculate_task_score(task, [task], "smart")
        self.assertTrue(score > 80)
        self.assertIn("Overdue", " ".join(explanation) or "")

    def test_quick_win(self):
        task = {"id":2, "title":"quick", "due_date":"2030-01-01", "estimated_hours":1, "importance":5, "dependencies":[]}
        score, explanation, flags = calculate_task_score(task, [task], "smart")
        self.assertTrue(score >= 5*5 + 10)  # importance*weight + quick win

    def test_dependency_blocker(self):
        t1 = {"id":1, "title":"A", "due_date":"2030-01-01", "estimated_hours":3, "importance":5, "dependencies":[]}
        t2 = {"id":2, "title":"B", "due_date":"2030-01-02", "estimated_hours":2, "importance":5, "dependencies":[1]}
        score, explanation, flags = calculate_task_score(t1, [t1, t2], "smart")
        self.assertTrue(any("Blocks" in e for e in explanation))
