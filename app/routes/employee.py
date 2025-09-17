from fastapi import APIRouter, Depends, HTTPException, Request, Form
from sqlalchemy.orm import Session
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates

from app.dependencies import get_db, employee_required
from app.models import Task, TaskHistory, TaskStatusEnum, User
from app.schemas import TaskResponse, TaskUpdate

router = APIRouter(prefix="/employee", tags=["Employee"])
templates = Jinja2Templates(directory="templates")  # Use top-level templates directory

# -------------------- API Routes --------------------


# -------------------- HTML Routes --------------------

@router.get("/dashboard", response_class=HTMLResponse)
def tasks_html(request: Request, db: Session = Depends(get_db), current_user: User = Depends(employee_required)):
    tasks = db.query(Task).filter(Task.assigned_to_id == current_user.id).all()
    return templates.TemplateResponse(
        "employee/tasks.html",
        {"request": request, "tasks": tasks, "user": current_user}
    )

@router.get("/update_task/html/{task_id}", response_class=HTMLResponse)
def update_task_form(task_id: int, request: Request, db: Session = Depends(get_db), current_user: User = Depends(employee_required)):
    task = db.query(Task).filter(Task.id == task_id, Task.assigned_to_id == current_user.id).first()
    if not task:
        return RedirectResponse(url="/employee/tasks/html")
    return templates.TemplateResponse(
        "employee/update_task.html",
        {"request": request, "task": task, "user": current_user}
    )
    
    
    
    
    

@router.post("/update_task/html/{task_id}")
def update_task_html(
    task_id: int,
    request: Request,
    status: TaskStatusEnum = Form(...),
    hours_spent: float = Form(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(employee_required)
):
    task = db.query(Task).filter(Task.id == task_id, Task.assigned_to_id == current_user.id).first()
    if not task:
        return RedirectResponse(url="/employee/dashboard")

    # ✅ Store old values for history
    old_status = task.status
    old_hours = task.hours_spent or 0.0

    # ✅ Add hours instead of overwriting
    if hours_spent is not None:
        task.hours_spent = old_hours + hours_spent

    # ✅ Update status
    task.status = status

    # ✅ Save to history
    history = TaskHistory(
        task_id=task.id,
        updated_by_id=current_user.id,
        status_before=old_status,
        status_after=status,
        hours_spent=hours_spent or 0.0  # just log hours added this time
    )

    db.add(history)
    db.commit()
    return RedirectResponse(url="/employee/dashboard", status_code=303)

@router.get("/task_history/html", response_class=HTMLResponse)
def task_history_html(request: Request, db: Session = Depends(get_db), current_user: User = Depends(employee_required)):
    histories = db.query(TaskHistory).filter(TaskHistory.updated_by_id == current_user.id).all()
    return templates.TemplateResponse(
        "employee/task_history.html",
        {"request": request, "histories": histories, "user": current_user}
    )
