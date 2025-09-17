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

@router.get("/tasks", response_model=list[TaskResponse])
def view_tasks(db: Session = Depends(get_db), current_user: User = Depends(employee_required)):
    tasks = db.query(Task).filter(Task.assigned_to_id == current_user.id).all()
    return tasks

@router.put("/update_task/{task_id}", response_model=TaskResponse)
def update_task(task_id: int, update: TaskUpdate, db: Session = Depends(get_db), current_user: User = Depends(employee_required)):
    task = db.query(Task).filter(Task.id == task_id, Task.assigned_to_id == current_user.id).first()
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    history = TaskHistory(
        task_id=task.id,
        updated_by_id=current_user.id,
        status_before=task.status,
        status_after=update.status,
        hours_spent=update.hours_spent or task.hours_spent
    )
    task.status = update.status
    if update.hours_spent is not None:
        task.hours_spent = update.hours_spent
    db.add(history)
    db.commit()
    db.refresh(task)
    return task

# -------------------- HTML Routes --------------------

@router.get("/tasks/html", response_class=HTMLResponse)
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
        return RedirectResponse(url="/employee/tasks/html")
    
    history = TaskHistory(
        task_id=task.id,
        updated_by_id=current_user.id,
        status_before=task.status,
        status_after=status,
        hours_spent=hours_spent or task.hours_spent
    )
    task.status = status
    if hours_spent is not None:
        task.hours_spent = hours_spent
    db.add(history)
    db.commit()
    return RedirectResponse(url="/employee/tasks/html", status_code=303)

@router.get("/task_history/html", response_class=HTMLResponse)
def task_history_html(request: Request, db: Session = Depends(get_db), current_user: User = Depends(employee_required)):
    histories = db.query(TaskHistory).filter(TaskHistory.updated_by_id == current_user.id).all()
    return templates.TemplateResponse(
        "employee/task_history.html",
        {"request": request, "histories": histories, "user": current_user}
    )
