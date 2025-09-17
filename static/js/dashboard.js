(function(){
  // Sorting for tables with .sortable
  document.querySelectorAll('table.sortable').forEach(table => {
    const ths = table.querySelectorAll('thead th');
    ths.forEach((th, idx) => {
      const type = th.getAttribute('data-sort') || 'string';
      th.addEventListener('click', () => {
        const current = th.classList.contains('asc') ? 'asc' : th.classList.contains('desc') ? 'desc' : null;
        ths.forEach(h => h.classList.remove('asc','desc'));
        const dir = current === 'asc' ? 'desc' : 'asc';
        th.classList.add(dir);
        const rows = Array.from(table.tBodies[0].rows);
        const parse = (v) => type==='number' ? parseFloat(v) || 0 : v.toString().toLowerCase();
        rows.sort((a,b) => {
          const A = parse(a.cells[idx].textContent.trim());
          const B = parse(b.cells[idx].textContent.trim());
          return dir==='asc' ? (A>B?1:A<B?-1:0) : (A<B?1:A>B?-1:0);
        });
        rows.forEach(r => table.tBodies[0].appendChild(r));
      });
    });
  });

  // Search filter for managers
  const managerSearch = document.getElementById('managerSearch');
  if (managerSearch) {
    const table = document.getElementById('managersTable');
    const run = () => {
      const q = managerSearch.value.trim().toLowerCase();
      table.querySelectorAll('tbody tr').forEach(row => {
        const text = row.textContent.toLowerCase();
        row.style.display = text.includes(q) ? '' : 'none';
      });
    };
    managerSearch.addEventListener('input', window.tfDebounce(run, 120));
  }

  // Search filter for employees tasks
  const taskSearch = document.getElementById('taskSearch');
  if (taskSearch) {
    const table = document.getElementById('employeesTasksTable');
    const run = () => {
      const q = taskSearch.value.trim().toLowerCase();
      table.querySelectorAll('tbody tr').forEach(row => {
        const text = row.textContent.toLowerCase();
        row.style.display = text.includes(q) ? '' : 'none';
      });
    };
    taskSearch.addEventListener('input', window.tfDebounce(run, 120));
  }

  // Employee task status filter
  const statusFilter = document.getElementById('statusFilter');
  if (statusFilter) {
    const table = document.getElementById('myTasksTable');
    const run = () => {
      const v = statusFilter.value;
      table.querySelectorAll('tbody tr').forEach(row => {
        const st = row.getAttribute('data-status');
        row.style.display = (v==='all' || v===st) ? '' : 'none';
      });
    };
    statusFilter.addEventListener('change', run);
    run();
  }
})();
