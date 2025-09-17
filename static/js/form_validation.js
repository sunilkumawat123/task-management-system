(function(){
  function setError(input, message){
    input.setAttribute('aria-invalid', 'true');
    let hint = input.nextElementSibling;
    if (!hint || !hint.classList.contains('field-error')) {
      hint = document.createElement('p');
      hint.className = 'field-error';
      hint.style.color = '#fb7185';
      hint.style.margin = '6px 0 0';
      input.insertAdjacentElement('afterend', hint);
    }
    hint.textContent = message;
  }
  function clearError(input){
    input.removeAttribute('aria-invalid');
    const hint = input.nextElementSibling;
    if (hint && hint.classList.contains('field-error')) hint.remove();
  }

  function validateEmail(v){
    return /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(v);
  }

  function hook(formId, validators){
    const form = document.getElementById(formId);
    if (!form) return;
    form.addEventListener('submit', (e) => {
      let ok = true;
      validators.forEach(({ id, test, msg }) => {
        const el = form.querySelector('#'+id);
        if (!el) return;
        if (!test(el.value.trim(), el)) { ok = false; setError(el, msg); } else { clearError(el); }
      });
      if (!ok) e.preventDefault();
    });
  }

  // Login
  hook('loginForm', [
    { id:'email', test:(v)=>validateEmail(v), msg:'Enter a valid email address' },
    { id:'password', test:(v)=>v.length>=8, msg:'Password must be at least 8 characters' },
  ]);

  // Create Manager
  hook('createManagerForm', [
    { id:'name', test:(v)=>v.length>1, msg:'Enter a full name' },
    { id:'email', test:(v)=>validateEmail(v), msg:'Enter a valid email' },
    { id:'password', test:(v)=>v.length>=8, msg:'Password must be at least 8 characters' },
    { id:'confirm_password', test:(v, el)=> v.length>=8 && v===el.form.querySelector('#password').value, msg:'Passwords must match' },
  ]);

  // Create Employee
  hook('createEmployeeForm', [
    { id:'name', test:(v)=>v.length>1, msg:'Enter a full name' },
    { id:'email', test:(v)=>validateEmail(v), msg:'Enter a valid email' },
    { id:'role', test:(v)=>v.length>1, msg:'Enter a role' },
  ]);

  // Assign Task
  hook('assignTaskForm', [
    { id:'employee_id', test:(v)=>!!v, msg:'Select an employee' },
    { id:'title', test:(v)=>v.length>2, msg:'Enter a title' },
    { id:'description', test:(v)=>v.length>10, msg:'Add a detailed description' },
    { id:'due_date', test:(v)=>!!v, msg:'Pick a due date' },
    { id:'priority', test:(v)=>!!v, msg:'Select priority' },
  ]);

  // Reassign Task
  hook('reassignTaskForm', [
    { id:'task_id', test:(v)=>!!v, msg:'Select a task' },
    { id:'new_employee_id', test:(v)=>!!v, msg:'Select a new assignee' },
  ]);

  // Update Task
  hook('updateTaskForm', [
    { id:'title', test:(v)=>v.length>2, msg:'Enter a title' },
    { id:'description', test:(v)=>v.length>5, msg:'Enter a description' },
    { id:'status', test:(v)=>!!v, msg:'Select status' },
    { id:'due_date', test:(v)=>!!v, msg:'Pick a due date' },
  ]);
})();
