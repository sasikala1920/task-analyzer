# Smart Task Analyzer

## Setup Instructions
1. Clone repository
2. Create virtual environment
3. Install dependencies: pip install -r requirements.txt
4. Run server: python manage.py runserver
5. Open frontend/index.html

## Algorithm Explanation
The algorithm combines urgency, importance, effort, and dependency impact. Overdue tasks are heavily boosted. High importance increases priority. Low effort tasks get quick-win bonuses. Tasks blocking others get dependency priority.

Strategies allow user-controlled reweighting for fastest completion, highest impact, strict deadlines, or smart balance.

## Edge Case Handling
- Past due dates get highest urgency
- Missing importance defaults to 5
- Low effort tasks prioritized
- Circular dependencies detected by reference checks

## Time Breakdown
- Backend: 2 hrs
- Frontend: 1.25 hrs
- Testing & Docs: 45 mins

## Unit Tests
3 scoring tests included.

## Future Improvements
- Holiday-aware dates
- Dependency graph visualization
- Learning-based suggestion tuning
