from fastapi import APIRouter, Depends, HTTPException, Request, Form
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session
from app.schemas import UserCreate, UserResponse
from app.models import User, RoleEnum
from app.auth import hash_password
from app.dependencies import get_db, admin_required
from fastapi.templating import Jinja2Templates
from sqlalchemy import text
from fastapi.responses import HTMLResponse, RedirectResponse













# Use relative path from main.py
templates = Jinja2Templates(directory="templates")
router = APIRouter(prefix="/admin", tags=["Admin"])















# ---------------- Admin Dashboard (HTML) ----------------

@router.get("/dashboard", response_class=HTMLResponse)
def admin_dashboard(request: Request, db: Session = Depends(get_db), current_user: User = Depends(admin_required)):
    total_managers = db.query(User).filter(User.role == RoleEnum.manager).count()
    total_employees = db.query(User).filter(User.role == RoleEnum.employee).count()
    total_tasks = db.execute(text("SELECT COUNT(*) FROM tasks")).scalar()  # raw SQL example
    recent_managers = db.query(User).filter(User.role == RoleEnum.manager).order_by(User.created_at.desc()).limit(5).all()
    # compute team sizes using ORM (users reference their creator via created_by_id)
    for m in recent_managers:
        try:
            cnt = db.query(User).filter(User.created_by_id == m.id).count()
        except Exception:
            cnt = 0
        setattr(m, "team_size", int(cnt or 0))
    # Simple empty activity placeholder until activity tracking exists

    return templates.TemplateResponse(
        "admin/dashboard.html",
        {
            "request": request,
            "total_managers": total_managers,
            "total_employees": total_employees,
            "total_tasks": total_tasks,
            "recent_managers": recent_managers,
            "user": current_user
        }
    )
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    

# ---------------- List Managers (HTML) ----------------
@router.get("/managers/html", response_class=HTMLResponse)
def list_managers_html(request: Request, db: Session = Depends(get_db), current_user: User = Depends(admin_required)):
    managers = db.query(User).filter(User.role == RoleEnum.manager).all()

    for m in managers:
        try:
            cnt = db.query(User).filter(User.created_by_id == m.id).count()
        except Exception:
            cnt = 0
        setattr(m, "team_size", int(cnt or 0))

    return templates.TemplateResponse(
        "admin/managers.html",
        {"request": request, "managers": managers, "user": current_user}
    )




















# ---------------- View Manager Details (HTML) ----------------
@router.get("/manager/{manager_id}/html", response_class=HTMLResponse)
def view_manager_html(manager_id: int, request: Request, db: Session = Depends(get_db), current_user: User = Depends(admin_required)):
    from app.models import Task, User

    # 1. Fetch manager
    manager = db.query(User).filter(User.id == manager_id, User.role == RoleEnum.manager).first()
    if not manager:
        raise HTTPException(status_code=404, detail="Manager not found")

    # 2. Fetch employees created by this manager
    employees = db.query(User).filter(User.created_by_id == manager.id).order_by(User.created_at.desc()).all()

    # 3. Fetch tasks assigned by this manager
    tasks = db.query(Task).filter(Task.assigned_by_id == manager.id).order_by(Task.created_at.desc()).all()

    # Add assigned_to_name so template can show employee names easily
    for t in tasks:
        employee = db.query(User).filter(User.id == t.assigned_to_id).first()
        t.assigned_to_name = employee.name if employee else "Unassigned"

    return templates.TemplateResponse(
        "admin/manager_detail.html",
        {
            "request": request,
            "manager": manager,
            "employees": employees,
            "tasks": tasks,
            "user": current_user,
            "activity": []  # you can remove this if not using activity anymore
        }
    )

    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
@router.get("/tasks/html", response_class=HTMLResponse)
def view_all_tasks_html(request: Request, db: Session = Depends(get_db), current_user: User = Depends(admin_required)):
    from app.models import Task, User
    tasks = db.query(Task).order_by(Task.created_at.desc()).all()

    for t in tasks:
        try:
            manager = db.query(User).filter(User.id == t.assigned_by_id).first()
            employee = db.query(User).filter(User.id == t.assigned_to_id).first()
        except Exception:
            manager = None
            employee = None
        setattr(t, "manager_name", manager.name if manager else "Unknown")
        setattr(t, "assigned_to_name", employee.name if employee else "Unassigned")

    return templates.TemplateResponse(
        "admin/all_tasks.html",
        {"request": request, "tasks": tasks, "user": current_user}
    )
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    # ---------------- View Manager Details (HTML) ----------------
@router.get("/manager/{manager_id}/html", response_class=HTMLResponse)
def view_manager_html(manager_id: int, request: Request, db: Session = Depends(get_db), current_user: User = Depends(admin_required)):
    from app.models import Task, User
    manager = db.query(User).filter(User.id == manager_id, User.role == RoleEnum.manager).first()
    if not manager:
        raise HTTPException(status_code=404, detail="Manager not found")

    # Load employees
    employees = db.query(User).filter(User.created_by_id == manager.id).order_by(User.created_at.desc()).all()

    # Load tasks assigned by this manager
    tasks = db.query(Task).filter(Task.assigned_by_id == manager.id).order_by(Task.created_at.desc()).all()
    for t in tasks:
        employee = db.query(User).filter(User.id == t.assigned_to_id).first()
        setattr(t, "assigned_to_name", employee.name if employee else "Unassigned")

    activity = []

    return templates.TemplateResponse(
        "admin/manager_detail.html",
        {
            "request": request,
            "manager": manager,
            "employees": employees,
            "tasks": tasks,
            "user": current_user,
            "activity": activity
        }
        
        
    )
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    



# ---------------- Task Reassign History (HTML) ----------------
@router.get("/reassign_history/html", response_class=HTMLResponse)
def reassign_history_html(request: Request, db: Session = Depends(get_db), current_user: User = Depends(admin_required)):
    # list recent reassign events with related user and task info
    try:
        from app.models import TaskReassign, Task, User
        reassigns = db.query(TaskReassign).order_by(TaskReassign.timestamp.desc()).limit(200).all()
    except Exception:
        reassigns = []

    # eager load relevant display fields manually to keep template simple
    display = []
    for r in reassigns:
        task = db.query(Task).filter(Task.id == r.task_id).first()
        prev = db.query(User).filter(User.id == r.previous_assignee_id).first()
        new = db.query(User).filter(User.id == r.new_assignee_id).first()
        by = db.query(User).filter(User.id == r.reassigned_by_id).first()
        display.append({
            "reassign": r,
            "task": task,
            "previous": prev,
            "new": new,
            "by": by
        })

    return templates.TemplateResponse(
        "admin/reassign_history.html",
        {"request": request, "items": display, "user": current_user}
    )



























# ---------------- Create Manager (HTML Form) ----------------
@router.get("/create_manager/html", response_class=HTMLResponse)
def create_manager_form(request: Request, current_user: User = Depends(admin_required)):
    return templates.TemplateResponse(
        "admin/create_manager.html",
        {"request": request, "user": current_user}
    )

@router.post("/create_manager/html")
def create_manager_html(request: Request, name: str = Form(...), username: str = Form(...),
                        email: str = Form(...), password: str = Form(...),
                        db: Session = Depends(get_db), current_user: User = Depends(admin_required)):
    existing = db.query(User).filter((User.username == username) | (User.email == email)).first()
    if existing:
        return templates.TemplateResponse(
            "admin/create_manager.html",
            {"request": request, "error": "Username or email already exists", "user": current_user,
             "name": name, "username": username, "email": email}
        )

    db_user = User(
        name=name,
        username=username,
        email=email,
        password_hash=hash_password(password),
        role=RoleEnum.manager,
        created_by_id=current_user.id
    )
    try:
        db.add(db_user)
        db.commit()
        db.refresh(db_user)
    except IntegrityError:
        db.rollback()
        return templates.TemplateResponse(
            "admin/create_manager.html",
            {"request": request, "error": "Username or email already exists", "user": current_user,
             "name": name, "username": username, "email": email},
        )
    return RedirectResponse(url="/admin/managers/html", status_code=303)



















# ---------------- Delete Manager ----------------

@router.get("/manager/{manager_id}/delete")
def delete_manager(manager_id: int, db: Session = Depends(get_db), current_user: User = Depends(admin_required)):
    manager = db.query(User).filter(User.id == manager_id, User.role == RoleEnum.manager).first()
    if not manager:
        raise HTTPException(status_code=404, detail="Manager not found")
    db.delete(manager)
    db.commit()
    return RedirectResponse(url="/admin/managers/html", status_code=303)
