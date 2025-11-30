from datetime import date, datetime, timedelta

# Default weights (tweakable)
WEIGHTS = {
    "urgency_overdue": 100,
    "urgency_soon": 50,
    "importance": 5,       # multiplied by importance value
    "quick_win": 10,
    "dependency_blocker": 15,
    "effort_penalty": 1,   # used where higher effort reduces score
}

def parse_date(s):
    """Parse YYYY-MM-DD to date object. Raise ValueError on bad format."""
    return datetime.strptime(s, "%Y-%m-%d").date()

def has_circular_dependency(start_id, tasks_map, visited=None, stack=None):
    """
    Detect cycle using DFS.
    tasks_map: dict id->task dict
    """
    if visited is None:
        visited = set()
    if stack is None:
        stack = set()

    def dfs(node):
        if node in stack:
            return True
        if node in visited:
            return False
        visited.add(node)
        stack.add(node)
        node_task = tasks_map.get(node)
        if not node_task:
            stack.remove(node)
            return False
        for dep in node_task.get("dependencies", []):
            if dfs(dep):
                return True
        stack.remove(node)
        return False

    return dfs(start_id)

def detect_blockers(task_id, tasks):
    """Return tasks that are blocked by task_id (i.e., others depend on it)."""
    return [t for t in tasks if task_id in t.get("dependencies", [])]

def calculate_task_score(task, all_tasks=None, strategy="smart"):
    """
    task: dict with keys: id, title, due_date (YYYY-MM-DD), estimated_hours, importance, dependencies
    all_tasks: list of task dicts (for dependency checks)
    strategy: "smart", "fastest", "impact", "deadline"
    Returns: (score:int, explanation:list[str], flags:dict)
    """
    explanation = []
    flags = {}
    score = 0

    # Safe defaults
    importance = int(task.get("importance", 5) or 5)
    estimated = int(task.get("estimated_hours", 1) or 1)
    deps = task.get("dependencies", []) or []

    # Parse date safely
    try:
        due = parse_date(task.get("due_date"))
    except Exception:
        # Invalid date -> deprioritize but mention
        explanation.append("Invalid due date; treated as far future")
        # Set a far future date
        due = date.today() + timedelta(days=365 * 5)

    today = date.today()
    days_until_due = (due - today).days

    # Urgency scoring
    if days_until_due < 0:
        score += WEIGHTS["urgency_overdue"]
        explanation.append(f"Overdue by {-days_until_due} days")
        flags["overdue"] = True
    elif days_until_due <= 3:
        score += WEIGHTS["urgency_soon"]
        explanation.append(f"Due in {days_until_due} days")
        flags["due_soon"] = True
    else:
        # small urgency factor for closer deadlines
        score += max(0, (30 - days_until_due) // 3)

    # Importance
    score += importance * WEIGHTS["importance"]
    explanation.append(f"Importance {importance}/10")

    # Effort / Quick wins
    if estimated <= 2:
        score += WEIGHTS["quick_win"]
        explanation.append("Quick win (low effort)")
    else:
        # penalty for high effort (lower the score slightly)
        score -= (estimated - 2) * WEIGHTS["effort_penalty"]

    # Dependencies — tasks that block others
    if all_tasks:
        blockers = detect_blockers(task.get("id"), all_tasks)
        if blockers:
            score += WEIGHTS["dependency_blocker"]
            explanation.append(f"Blocks {len(blockers)} task(s)")

    # Circular dependency detection
    if all_tasks:
        tasks_map = {t["id"]: t for t in all_tasks}
        if has_circular_dependency(task.get("id"), tasks_map):
            score -= 50
            explanation.append("Circular dependency detected")
            flags["circular"] = True

    # Strategy overrides (user toggle)
    if strategy == "fastest":
        # heavily boost low effort
        score += max(0, (5 - estimated)) * 8
        explanation.append("Strategy: Fastest Wins")
    elif strategy == "impact":
        score += importance * 8
        explanation.append("Strategy: High Impact")
    elif strategy == "deadline":
        # amplify urgency
        if days_until_due < 0:
            score += 50
        else:
            score += max(0, (30 - days_until_due))
        explanation.append("Strategy: Deadline Driven")
    else:
        explanation.append("Strategy: Smart Balance")

    # clamp score to a sensible range
    score = int(score)
    return score, explanation, flags
