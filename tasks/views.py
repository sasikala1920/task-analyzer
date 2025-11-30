import json
from django.http import JsonResponse, HttpResponseBadRequest
from django.views.decorators.csrf import csrf_exempt
from .scoring import calculate_task_score

@csrf_exempt
def analyze_tasks(request):
    """
    POST /api/tasks/analyze/
    Accepts JSON array of tasks. Returns same array with score, explanation, flags.
    Supports query param ?strategy=fastest|impact|deadline|smart
    """
    if request.method != "POST":
        return HttpResponseBadRequest("Use POST")

    try:
        tasks = json.loads(request.body.decode("utf-8"))
        if not isinstance(tasks, list):
            return HttpResponseBadRequest("Expected a JSON array of tasks")
    except Exception:
        return HttpResponseBadRequest("Invalid JSON")

    strategy = request.GET.get("strategy", "smart")
    # ensure each task has an id (if not provided, create temp ids)
    for i, t in enumerate(tasks):
        if "id" not in t:
            t["id"] = i + 1

    # compute scores
    for t in tasks:
        score, explanation, flags = calculate_task_score(t, tasks, strategy)
        t["score"] = score
        t["explanation"] = explanation
        t["flags"] = flags

    sorted_tasks = sorted(tasks, key=lambda x: x["score"], reverse=True)
    return JsonResponse(sorted_tasks, safe=False)

@csrf_exempt
def suggest_tasks(request):
    """
    POST /api/tasks/suggest/
    Accepts JSON array of tasks and returns top 3 with textual explanations.
    (Using POST for ease: client can send bulk tasks)
    """
    if request.method != "POST":
        return HttpResponseBadRequest("Use POST")

    try:
        tasks = json.loads(request.body.decode("utf-8"))
        if not isinstance(tasks, list):
            return HttpResponseBadRequest("Expected a JSON array of tasks")
    except Exception:
        return HttpResponseBadRequest("Invalid JSON")

    # score them (use smart strategy)
    for i, t in enumerate(tasks):
        if "id" not in t:
            t["id"] = i + 1

    for t in tasks:
        score, explanation, flags = calculate_task_score(t, tasks, "smart")
        t["score"] = score
        t["explanation"] = explanation
        t["flags"] = flags

    sorted_tasks = sorted(tasks, key=lambda x: x["score"], reverse=True)
    top3 = sorted_tasks[:3]
    # Build textual explanations
    output = []
    for t in top3:
        reason = "; ".join(t["explanation"])
        output.append({
            "id": t["id"],
            "title": t.get("title"),
            "due_date": t.get("due_date"),
            "estimated_hours": t.get("estimated_hours"),
            "importance": t.get("importance"),
            "score": t["score"],
            "reason": reason,
            "flags": t.get("flags", {})
        })
    return JsonResponse(output, safe=False)
