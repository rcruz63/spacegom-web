# Hiring System Endpoints will be added after missions
# Given complexity, creating in separate step-by-step process

HIRE ENDPOINTS NOTES:
1. GET /api/games/{id}/hire/available-positions - Simple filter by tech_level
2. POST /api/games/{id}/hire/start - Complex: create task, calculate days, enqueue
3. GET /api/games/{id}/personnel/{employee_id}/tasks - List queue
4. PUT /api/games/{id}/tasks/{task_id}/reorder - Reorder pending
5. DELETE /api/games/{id}/tasks/{task_id} - Delete pending
6. POST /api/games/{id}/time/advance - Advance to next event

Due to complexity and token usage, implementing in phases.
