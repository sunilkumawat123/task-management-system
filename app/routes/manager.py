from fastapi import APIRouter, Depends, HTTPException, Request, Form
from sqlalchemy.orm import Session, joinedload
from sqlalchemy import func
from datetime import date, datetime
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates

from app.dependencies import get_db, manager_required
from app.models import User, RoleEnum, Task, TaskStatusEnum
from app.schemas import UserCreate, UserResponse, TaskCreate, TaskResponse
from app.auth import hash_password

try:
    from app.utils import send_email
except Exception:
    def send_email(to: str, subject: str, body: str):
        return None

router = APIRouter(prefix="/manager", tags=["Manager"])
templates = Jinja2Templates(directory="templates")  # Use top-level templates directory

# -------------------- API Routes --------------------

@router.post("/create_employee", response_model=UserResponse)
def create_employee(user: UserCreate, db: Session = Depends(get_db), current_user: User = Depends(manager_required)):
    if user.role != RoleEnum.employee:
        raise HTTPException(status_code=400, detail="Role must be employee")
    existing = db.query(User).filter((User.username==user.username)|(User.email==user.email)).first()
    if existing:
        raise HTTPException(status_code=400, detail="Username or email already exists")
    db_user = User(
        name=user.name,
        username=user.username,
        email=user.email,
        password_hash=hash_password(user.password),
        role=RoleEnum.employee,
        created_by_id=current_user.id
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

@router.post("/assign_task", response_model=TaskResponse)
def assign_task(task: TaskCreate, db: Session = Depends(get_db), current_user: User = Depends(manager_required)):
    employee = db.query(User).filter(User.id==task.assigned_to_id, User.created_by_id==current_user.id).first()
    if not employee:
        raise HTTPException(status_code=404, detail="Employee not found")
    db_task = Task(
        title=task.title,
        description=task.description,
        assigned_to_id=employee.id,
        assigned_by_id=current_user.id,
    )
    db.add(db_task)
    db.commit()
    db.refresh(db_task)
    send_email(employee.email, "New Task Assigned", f"You have been assigned a task: {db_task.title}")
    return db_task

@router.put("/reassign_task/{task_id}", response_model=TaskResponse)
def reassign_task(task_id: int, new_employee_id: int, db: Session = Depends(get_db), current_user: User = Depends(manager_required)):
    task = db.query(Task).filter(Task.id==task_id, Task.assigned_by_id==current_user.id).first()
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    new_employee = db.query(User).filter(User.id==new_employee_id, User.created_by_id==current_user.id).first()
    if not new_employee:
        raise HTTPException(status_code=404, detail="New employee not found")
    previous = task.assigned_to_id
    task.assigned_to_id = new_employee.id
    db.commit()
    db.refresh(task)
    # record reassign event for API call
    try:
        from app.models import TaskReassign
        re = TaskReassign(
            task_id=task.id,
            previous_assignee_id=previous,
            new_assignee_id=new_employee.id,
            reassigned_by_id=current_user.id,
            reason=None
        )
        db.add(re)
        db.commit()
    except Exception:
        db.rollback()
    send_email(new_employee.email, "Task Reassigned", f"You have been assigned a task: {task.title}")
    return task

@router.get("/employees_tasks")
def view_employees_tasks(db: Session = Depends(get_db), current_user: User = Depends(manager_required)):
    employees = db.query(User).filter(User.created_by_id==current_user.id).all()
    result = []
    for emp in employees:
        tasks = db.query(Task).filter(Task.assigned_to_id==emp.id).all()
        result.append({"employee": emp, "tasks": tasks})
    return result

# -------------------- HTML Routes --------------------

@router.get("/dashboard", response_class=HTMLResponse)
def manager_dashboard(request: Request, db: Session = Depends(get_db), current_user: User = Depends(manager_required)):
    # Team and task counts
    total_employees = db.query(User).filter(User.created_by_id == current_user.id).count()
    total_tasks = db.query(Task).filter(Task.assigned_by_id == current_user.id).count()
    open_tasks = db.query(Task).filter(Task.assigned_by_id == current_user.id, Task.status != TaskStatusEnum.completed).count()

    # Due today: approximate by tasks created today (no deadline field present)
    today = date.today()
    try:
        due_today = db.query(Task).filter(func.date(Task.created_at) == today, Task.assigned_by_id == current_user.id).count()
    except Exception:
        # Some DBs don't support func.date; fallback to 0
        due_today = 0

    # On-time rate: completed / total assigned by this manager
    completed = db.query(Task).filter(Task.assigned_by_id == current_user.id, Task.status == TaskStatusEnum.completed).count()
    ontime_rate = int((completed / total_tasks) * 100) if total_tasks else 100

    stats = {
        "team_size": int(total_employees or 0),
        "open_tasks": int(open_tasks or 0),
        "due_today": int(due_today or 0),
        "ontime_rate": int(ontime_rate),
    }

    # Recent tasks assigned by this manager
    tasks = db.query(Task).options(joinedload(Task.assigned_to)).filter(Task.assigned_by_id == current_user.id).order_by(Task.created_at.desc()).limit(10).all()

    # Simple alerts: too many open tasks or employees without tasks
    alerts = []
    if open_tasks > 10:
        alerts.append({"level": "warning", "message": f"{open_tasks} open tasks need attention"})

    # find employees without any tasks (small teams acceptable to loop)
    employees = db.query(User).filter(User.created_by_id == current_user.id).all()
    no_task_emps = []
    for emp in employees:
        emp_tasks = db.query(Task).filter(Task.assigned_to_id == emp.id).count()
        if emp_tasks == 0:
            no_task_emps.append(emp.name)
    if no_task_emps:
        alerts.append({"level": "info", "message": f"Employees with no tasks: {', '.join(no_task_emps[:5])}{'...' if len(no_task_emps)>5 else ''}"})

    return templates.TemplateResponse(
        "manager/dashboard.html",
        {"request": request, "stats": stats, "tasks": tasks, "alerts": alerts, "user": current_user}
    )

# HTML forms & redirects all paths prefixed properly
@router.get("/create_employee/html", response_class=HTMLResponse)
def create_employee_form(request: Request, current_user: User = Depends(manager_required)):
    return templates.TemplateResponse("manager/create_employee.html", {"request": request, "user": current_user})

@router.post("/create_employee/html")
def create_employee_html(request: Request, name: str = Form(...), username: str = Form(...), email: str = Form(...), password: str = Form(...), db: Session = Depends(get_db), current_user: User = Depends(manager_required)):
    existing = db.query(User).filter((User.username==username)|(User.email==email)).first()
    if existing:
        return templates.TemplateResponse("manager/create_employee.html", {"request": request, "error": "Username or email already exists", "user": current_user})
    db_user = User(name=name, username=username, email=email, password_hash=hash_password(password), role=RoleEnum.employee, created_by_id=current_user.id)
    db.add(db_user)
    db.commit()
    return RedirectResponse(url="/manager/dashboard", status_code=303)

# Assign Task HTML
@router.get("/assign_task/html", response_class=HTMLResponse)
def assign_task_form(request: Request, db: Session = Depends(get_db), current_user: User = Depends(manager_required)):
    employees = db.query(User).filter(User.created_by_id==current_user.id).all()
    return templates.TemplateResponse("manager/assign_task.html", {"request": request, "employees": employees, "user": current_user})

@router.post("/assign_task/html")
def assign_task_html(request: Request, employee_id: int = Form(...), title: str = Form(...), description: str = Form(...), db: Session = Depends(get_db), current_user: User = Depends(manager_required)):
    employee = db.query(User).filter(User.id==employee_id, User.created_by_id==current_user.id).first()
    if not employee:
        return templates.TemplateResponse("manager/assign_task.html", {"request": request, "error": "Employee not found", "user": current_user})
    db_task = Task(title=title, description=description, assigned_to_id=employee.id, assigned_by_id=current_user.id)
    db.add(db_task)
    db.commit()
    send_email(employee.email, "New Task Assigned", f"You have been assigned a task: {title}")
    return RedirectResponse(url="/manager/employees_tasks/html", status_code=303)

@router.get("/reassign_task/html", response_class=HTMLResponse)
def reassign_task_form(request: Request, db: Session = Depends(get_db), current_user: User = Depends(manager_required)):
    tasks = db.query(Task).filter(Task.assigned_by_id==current_user.id).all()
    employees = db.query(User).filter(User.created_by_id==current_user.id).all()
    return templates.TemplateResponse("manager/reassign_task.html", {"request": request, "tasks": tasks, "employees": employees, "user": current_user})

@router.post("/reassign_task/html")
def reassign_task_html(request: Request, task_id: int = Form(...), employee_id: int = Form(...), note: str = Form(None), db: Session = Depends(get_db), current_user: User = Depends(manager_required)):
    task = db.query(Task).filter(Task.id==task_id, Task.assigned_by_id==current_user.id).first()
    if not task:
        return templates.TemplateResponse("manager/reassign_task.html", {"request": request, "error": "Task not found", "user": current_user})
    employee = db.query(User).filter(User.id==employee_id, User.created_by_id==current_user.id).first()
    if not employee:
        return templates.TemplateResponse("manager/reassign_task.html", {"request": request, "error": "Employee not found", "user": current_user})
    previous = task.assigned_to_id
    task.assigned_to_id = employee.id
    db.commit()
    # record reassign event
    try:
        from app.models import TaskReassign
        re = TaskReassign(
            task_id=task.id,
            previous_assignee_id=previous,
            new_assignee_id=employee.id,
            reassigned_by_id=current_user.id,
            reason=(note or None)
        )
        db.add(re)
        db.commit()
    except Exception:
        # non-critical: proceed even if reassign history can't be written
        db.rollback()
    send_email(employee.email, "Task Reassigned", f"You have been assigned a task: {task.title}")
    return RedirectResponse(url="/manager/employees_tasks/html", status_code=303)

@router.get("/task/{task_id}/delete")
def delete_task(task_id: int, db: Session = Depends(get_db), current_user: User = Depends(manager_required)):
    task = db.query(Task).filter(Task.id==task_id, Task.assigned_by_id==current_user.id).first()
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    db.delete(task)
    db.commit()
    return RedirectResponse(url="/manager/employees_tasks/html", status_code=303)

@router.get("/employees_tasks/html", response_class=HTMLResponse)
def employees_tasks_html(request: Request, db: Session = Depends(get_db), current_user: User = Depends(manager_required)):
    employees = db.query(User).filter(User.created_by_id==current_user.id).all()
    tasks_list = []
    for emp in employees:
        tasks = db.query(Task).filter(Task.assigned_to_id==emp.id).all()
        tasks_list.extend(tasks)
    return templates.TemplateResponse("manager/employees_tasks.html", {"request": request, "tasks": tasks_list, "user": current_user})


# Manager: list employees under this manager
@router.get("/employees/html", response_class=HTMLResponse)
def manager_employees_html(request: Request, db: Session = Depends(get_db), current_user: User = Depends(manager_required)):
    employees = db.query(User).filter(User.created_by_id == current_user.id).order_by(User.created_at.desc()).all()
    return templates.TemplateResponse("manager/employees.html", {"request": request, "employees": employees, "user": current_user})


# Manager: delete an employee (only if they belong to manager's team)
@router.get("/employee/{employee_id}/delete")
def manager_delete_employee(employee_id: int, db: Session = Depends(get_db), current_user: User = Depends(manager_required)):
    emp = db.query(User).filter(User.id == employee_id, User.created_by_id == current_user.id).first()
    if not emp:
        raise HTTPException(status_code=404, detail="Employee not found")
    # unassign tasks assigned to this employee
    tasks = db.query(Task).filter(Task.assigned_to_id == emp.id).all()
    for t in tasks:
        t.assigned_to_id = None
    db.delete(emp)
    db.commit()
    return RedirectResponse(url="/manager/employees/html", status_code=303)


@router.get("/reassign_history/html", response_class=HTMLResponse)
def manager_reassign_history_html(request: Request, db: Session = Depends(get_db), current_user: User = Depends(manager_required)):
    try:
        from app.models import TaskReassign, Task, User
        reassigns = db.query(TaskReassign).filter(TaskReassign.reassigned_by_id == current_user.id).order_by(TaskReassign.timestamp.desc()).limit(200).all()
    except Exception:
        reassigns = []

    display = []
    for r in reassigns:
        task = db.query(Task).filter(Task.id == r.task_id).first()
        prev = db.query(User).filter(User.id == r.previous_assignee_id).first()
        new = db.query(User).filter(User.id == r.new_assignee_id).first()
        display.append({"reassign": r, "task": task, "previous": prev, "new": new})

    return templates.TemplateResponse("manager/reassign_history.html", {"request": request, "items": display, "user": current_user})
