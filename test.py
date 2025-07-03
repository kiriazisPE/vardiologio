import streamlit as st
import pandas as pd
from collections import defaultdict
import datetime

# --- Config ---
st.set_page_config(page_title="Πρόγραμμα Βαρδιών", layout="centered")
st.title("📅 Δημιουργία Προγράμματος Βαρδιών")
st.caption("Εργαλείο κατανομής βαρδιών σύμφωνα με την ελληνική εργατική νομοθεσία")

# --- Constants ---
DAYS = ["Δευτέρα", "Τρίτη", "Τετάρτη", "Πέμπτη", "Παρασκευή", "Σάββατο", "Κυριακή"]
SHIFTS = ["Πρωί", "Απόγευμα", "Βράδυ"]
ROLES = ["Ταμείο", "Σερβιτόρος", "Μάγειρας", "Barista"]

# --- Initialize session ---
def init_session():
    if "employees" not in st.session_state:
        st.session_state.employees = []
    if "shift_requirements" not in st.session_state:
        st.session_state.shift_requirements = defaultdict(lambda: defaultdict(lambda: defaultdict(int)))
    if "active_shifts" not in st.session_state:
        st.session_state.active_shifts = SHIFTS.copy()
    if "edit_index" not in st.session_state:
        st.session_state.edit_index = None
    if "final_schedule_df" not in st.session_state:
        st.session_state.final_schedule_df = pd.DataFrame()

# --- Setup Parameters ---
def setup_parameters():
    with st.expander("⚙️ Ρυθμίσεις & Κανόνες Λειτουργίας", expanded=True):
        st.markdown("##### Επιλέξτε ποιες βάρδιες χρησιμοποιεί το κατάστημά σας")
        selected = st.multiselect("Βάρδιες ανά ημέρα", SHIFTS, default=SHIFTS[:2])
        st.session_state.active_shifts = selected

# --- Add or Edit employee ---
def add_employee():
    with st.expander("➕ Προσθήκη / Επεξεργασία Υπαλλήλου"):
        if st.session_state.edit_index is not None:
            employee = st.session_state.employees[st.session_state.edit_index]
            name = st.text_input("Όνομα Υπαλλήλου", value=employee["name"])
            roles = st.multiselect("Ρόλοι (πόστα) που μπορεί να καλύψει", ROLES, default=employee["roles"])
            days_off = st.slider("Ρεπό ανά εβδομάδα (βάσει νόμου: τουλάχιστον 1)", 1, 3, employee["days_off"])
        else:
            name = st.text_input("Όνομα Υπαλλήλου")
            roles = st.multiselect("Ρόλοι (πόστα) που μπορεί να καλύψει", ROLES, default=ROLES)
            days_off = st.slider("Ρεπό ανά εβδομάδα (βάσει νόμου: τουλάχιστον 1)", 1, 3, 2)

        availability = {}
        st.markdown("#### Διαθεσιμότητα ανά ημέρα")
        for day in DAYS:
            default = st.session_state.active_shifts if st.session_state.edit_index is None else employee["availability"].get(day, [])
            availability[day] = st.multiselect(f"{day}", st.session_state.active_shifts, default=default, key=f"{name}-{day}")

        if st.button("✅ Αποθήκευση Υπαλλήλου") and name:
            employee_data = {
                "name": name,
                "roles": roles,
                "days_off": days_off,
                "availability": availability,
                "absences": [],
                "last_night_shift": None
            }
            if st.session_state.edit_index is not None:
                st.session_state.employees[st.session_state.edit_index] = employee_data
                st.success(f"Ο υπάλληλος {name} ενημερώθηκε.")
                st.session_state.edit_index = None
            else:
                st.session_state.employees.append(employee_data)
                st.success(f"Ο υπάλληλος {name} προστέθηκε.")

# --- Define shift requirements ---
def define_requirements():
    with st.expander("📌 Ορισμός Αναγκών Βαρδιών"):
        for day in DAYS:
            with st.expander(f"📅 {day}"):
                for shift in st.session_state.active_shifts:
                    cols = st.columns(len(ROLES))
                    for idx, role in enumerate(ROLES):
                        key = f"{day}-{shift}-{role}"
                        val = cols[idx].number_input(f"{shift} - {role}", min_value=0, value=0, step=1, key=key)
                        st.session_state.shift_requirements[day][shift][role] = val

# --- Display employees with Edit/Delete ---
def show_employees():
    with st.expander("👥 Προβολή Υπαλλήλων", expanded=True):
        if st.session_state.employees:
            for idx, e in enumerate(st.session_state.employees):
                col1, col2, col3 = st.columns([3, 1, 1])
                with col1:
                    st.markdown(f"**{e['name']}** - {', '.join(e['roles'])} | Ρεπό: {e['days_off']}")
                with col2:
                    if st.button("✏️ Επεξεργασία", key=f"edit_{idx}"):
                        st.session_state.edit_index = idx
                with col3:
                    if st.button("🗑️ Διαγραφή", key=f"delete_{idx}"):
                         st.session_state.employees.pop(idx)
                         st.session_state.edit_index = None
                         st.experimental_rerun()
        else:
            st.info("Δεν έχουν προστεθεί υπάλληλοι.")
Traceback (most recent call last):

  File "/home/adminuser/venv/lib/python3.13/site-packages/streamlit/runtime/scriptrunner/script_runner.py", line 571, in _run_script

    code = self._script_cache.get_bytecode(script_path)

  File "/home/adminuser/venv/lib/python3.13/site-packages/streamlit/runtime/scriptrunner/script_cache.py", line 72, in get_bytecode

    filebody = magic.add_magic(filebody, script_path)

  File "/home/adminuser/venv/lib/python3.13/site-packages/streamlit/runtime/scriptrunner/magic.py", line 45, in add_magic

    tree = ast.parse(code, script_path, "exec")

  File "/usr/local/lib/python3.13/ast.py", line 50, in parse

    return compile(source, filename, mode, flags,

                   _feature_version=feature_version, optimize=optimize)

  File "/mount/src/vardiologio/test.py", line 245

    display_missing_shifts(missing_shifts)

IndentationError: unexpected indent

2025-07-03 08:09:26.594 Thread 'MainThread': missing ScriptRunContext! This warning can be ignored when running in bare mode.

2025-07-03 08:09:26.688 503 GET /script-health-check (127.0.0.1) 101.93ms

2025-07-03 08:09:31.660 Script compilation error

Traceback (most recent call last):

  File "/home/adminuser/venv/lib/python3.13/site-packages/streamlit/runtime/scriptrunner/script_runner.py", line 571, in _run_script

    code = self._script_cache.get_bytecode(script_path)

  File "/home/adminuser/venv/lib/python3.13/site-packages/streamlit/runtime/scriptrunner/script_cache.py", line 72, in get_bytecode

    filebody = magic.add_magic(filebody, script_path)

  File "/home/adminuser/venv/lib/python3.13/site-packages/streamlit/runtime/scriptrunner/magic.py", line 45, in add_magic

    tree = ast.parse(code, script_path, "exec")

  File "/usr/local/lib/python3.13/ast.py", line 50, in parse

    return compile(source, filename, mode, flags,

                   _feature_version=feature_version, optimize=optimize)

  File "/mount/src/vardiologio/test.py", line 245

    display_missing_shifts(missing_shifts)

IndentationError: unexpected indent

2025-07-03 08:09:31.663 Thread 'MainThread': missing ScriptRunContext! This warning can be ignored when running in bare mode.

2025-07-03 08:09:31.756 503 GET /script-health-check (127.0.0.1) 102.97ms

2025-07-03 08:09:36.651 Script compilation error

Traceback (most recent call last):

  File "/home/adminuser/venv/lib/python3.13/site-packages/streamlit/runtime/scriptrunner/script_runner.py", line 571, in _run_script

    code = self._script_cache.get_bytecode(script_path)

  File "/home/adminuser/venv/lib/python3.13/site-packages/streamlit/runtime/scriptrunner/script_cache.py", line 72, in get_bytecode

    filebody = magic.add_magic(filebody, script_path)

  File "/home/adminuser/venv/lib/python3.13/site-packages/streamlit/runtime/scriptrunner/magic.py", line 45, in add_magic

    tree = ast.parse(code, script_path, "exec")

  File "/usr/local/lib/python3.13/ast.py", line 50, in parse

    return compile(source, filename, mode, flags,

                   _feature_version=feature_version, optimize=optimize)

  File "/mount/src/vardiologio/test.py", line 245

    display_missing_shifts(missing_shifts)

IndentationError: unexpected indent

2025-07-03 08:09:36.653 Thread 'MainThread': missing ScriptRunContext! This warning can be ignored when running in bare mode.

2025-07-03 08:09:36.748 503 GET /script-health-check (127.0.0.1) 103.04ms

2025-07-03 08:09:41.613 Script compilation error

Traceback (most recent call last):

  File "/home/adminuser/venv/lib/python3.13/site-packages/streamlit/runtime/scriptrunner/script_runner.py", line 571, in _run_script

    code = self._script_cache.get_bytecode(script_path)

  File "/home/adminuser/venv/lib/python3.13/site-packages/streamlit/runtime/scriptrunner/script_cache.py", line 72, in get_bytecode

    filebody = magic.add_magic(filebody, script_path)

  File "/home/adminuser/venv/lib/python3.13/site-packages/streamlit/runtime/scriptrunner/magic.py", line 45, in add_magic

    tree = ast.parse(code, script_path, "exec")

  File "/usr/local/lib/python3.13/ast.py", line 50, in parse

    return compile(source, filename, mode, flags,

                   _feature_version=feature_version, optimize=optimize)

  File "/mount/src/vardiologio/test.py", line 245

    display_missing_shifts(missing_shifts)

IndentationError: unexpected indent

2025-07-03 08:09:41.616 Thread 'MainThread': missing ScriptRunContext! This warning can be ignored when running in bare mode.

2025-07-03 08:09:41.709 503 GET /script-health-check (127.0.0.1) 102.35ms

2025-07-03 08:09:46.661 Script compilation error

Traceback (most recent call last):

  File "/home/adminuser/venv/lib/python3.13/site-packages/streamlit/runtime/scriptrunner/script_runner.py", line 571, in _run_script

    code = self._script_cache.get_bytecode(script_path)

  File "/home/adminuser/venv/lib/python3.13/site-packages/streamlit/runtime/scriptrunner/script_cache.py", line 72, in get_bytecode

    filebody = magic.add_magic(filebody, script_path)

  File "/home/adminuser/venv/lib/python3.13/site-packages/streamlit/runtime/scriptrunner/magic.py", line 45, in add_magic

    tree = ast.parse(code, script_path, "exec")

  File "/usr/local/lib/python3.13/ast.py", line 50, in parse

    return compile(source, filename, mode, flags,

                   _feature_version=feature_version, optimize=optimize)

  File "/mount/src/vardiologio/test.py", line 245

    display_missing_shifts(missing_shifts)

IndentationError: unexpected indent

2025-07-03 08:09:46.664 Thread 'MainThread': missing ScriptRunContext! This warning can be ignored when running in bare mode.

2025-07-03 08:09:46.757 503 GET /script-health-check (127.0.0.1) 102.64ms

2025-07-03 08:09:51.669 Script compilation error

Traceback (most recent call last):

  File "/home/adminuser/venv/lib/python3.13/site-packages/streamlit/runtime/scriptrunner/script_runner.py", line 571, in _run_script

    code = self._script_cache.get_bytecode(script_path)

  File "/home/adminuser/venv/lib/python3.13/site-packages/streamlit/runtime/scriptrunner/script_cache.py", line 72, in get_bytecode

    filebody = magic.add_magic(filebody, script_path)

  File "/home/adminuser/venv/lib/python3.13/site-packages/streamlit/runtime/scriptrunner/magic.py", line 45, in add_magic

    tree = ast.parse(code, script_path, "exec")

  File "/usr/local/lib/python3.13/ast.py", line 50, in parse

    return compile(source, filename, mode, flags,

                   _feature_version=feature_version, optimize=optimize)

  File "/mount/src/vardiologio/test.py", line 245

    display_missing_shifts(missing_shifts)

IndentationError: unexpected indent

2025-07-03 08:09:51.671 Thread 'MainThread': missing ScriptRunContext! This warning can be ignored when running in bare mode.

2025-07-03 08:09:51.762 503 GET /script-health-check (127.0.0.1) 102.51ms

2025-07-03 08:09:56.642 Script compilation error

Traceback (most recent call last):

  File "/home/adminuser/venv/lib/python3.13/site-packages/streamlit/runtime/scriptrunner/script_runner.py", line 571, in _run_script

    code = self._script_cache.get_bytecode(script_path)

  File "/home/adminuser/venv/lib/python3.13/site-packages/streamlit/runtime/scriptrunner/script_cache.py", line 72, in get_bytecode

    filebody = magic.add_magic(filebody, script_path)

  File "/home/adminuser/venv/lib/python3.13/site-packages/streamlit/runtime/scriptrunner/magic.py", line 45, in add_magic

    tree = ast.parse(code, script_path, "exec")

  File "/usr/local/lib/python3.13/ast.py", line 50, in parse

    return compile(source, filename, mode, flags,

                   _feature_version=feature_version, optimize=optimize)

  File "/mount/src/vardiologio/test.py", line 245

    display_missing_shifts(missing_shifts)

IndentationError: unexpected indent

2025-07-03 08:09:56.644 Thread 'MainThread': missing ScriptRunContext! This warning can be ignored when running in bare mode.

2025-07-03 08:09:56.737 503 GET /script-health-check (127.0.0.1) 104.42ms

2025-07-03 08:10:01.655 Script compilation error

Traceback (most recent call last):

  File "/home/adminuser/venv/lib/python3.13/site-packages/streamlit/runtime/scriptrunner/script_runner.py", line 571, in _run_script

    code = self._script_cache.get_bytecode(script_path)

  File "/home/adminuser/venv/lib/python3.13/site-packages/streamlit/runtime/scriptrunner/script_cache.py", line 72, in get_bytecode

    filebody = magic.add_magic(filebody, script_path)

  File "/home/adminuser/venv/lib/python3.13/site-packages/streamlit/runtime/scriptrunner/magic.py", line 45, in add_magic

    tree = ast.parse(code, script_path, "exec")

  File "/usr/local/lib/python3.13/ast.py", line 50, in parse

    return compile(source, filename, mode, flags,

                   _feature_version=feature_version, optimize=optimize)

  File "/mount/src/vardiologio/test.py", line 245

    display_missing_shifts(missing_shifts)

IndentationError: unexpected indent

2025-07-03 08:10:01.657 Thread 'MainThread': missing ScriptRunContext! This warning can be ignored when running in bare mode.

2025-07-03 08:10:01.750 503 GET /script-health-check (127.0.0.1) 102.17ms

2025-07-03 08:10:06.705 Script compilation error

Traceback (most recent call last):

  File "/home/adminuser/venv/lib/python3.13/site-packages/streamlit/runtime/scriptrunner/script_runner.py", line 571, in _run_script

    code = self._script_cache.get_bytecode(script_path)

  File "/home/adminuser/venv/lib/python3.13/site-packages/streamlit/runtime/scriptrunner/script_cache.py", line 72, in get_bytecode

    filebody = magic.add_magic(filebody, script_path)

  File "/home/adminuser/venv/lib/python3.13/site-packages/streamlit/runtime/scriptrunner/magic.py", line 45, in add_magic

    tree = ast.parse(code, script_path, "exec")

  File "/usr/local/lib/python3.13/ast.py", line 50, in parse

    return compile(source, filename, mode, flags,

                   _feature_version=feature_version, optimize=optimize)

  File "/mount/src/vardiologio/test.py", line 245

    display_missing_shifts(missing_shifts)

IndentationError: unexpected indent

2025-07-03 08:10:06.707 Thread 'MainThread': missing ScriptRunContext! This warning can be ignored when running in bare mode.

2025-07-03 08:10:06.800 503 GET /script-health-check (127.0.0.1) 102.06ms

2025-07-03 08:10:11.678 Script compilation error

Traceback (most recent call last):

  File "/home/adminuser/venv/lib/python3.13/site-packages/streamlit/runtime/scriptrunner/script_runner.py", line 571, in _run_script

    code = self._script_cache.get_bytecode(script_path)

  File "/home/adminuser/venv/lib/python3.13/site-packages/streamlit/runtime/scriptrunner/script_cache.py", line 72, in get_bytecode

    filebody = magic.add_magic(filebody, script_path)

  File "/home/adminuser/venv/lib/python3.13/site-packages/streamlit/runtime/scriptrunner/magic.py", line 45, in add_magic

    tree = ast.parse(code, script_path, "exec")

  File "/usr/local/lib/python3.13/ast.py", line 50, in parse

    return compile(source, filename, mode, flags,

                   _feature_version=feature_version, optimize=optimize)

  File "/mount/src/vardiologio/test.py", line 245

    display_missing_shifts(missing_shifts)

IndentationError: unexpected indent

2025-07-03 08:10:11.681 Thread 'MainThread': missing ScriptRunContext! This warning can be ignored when running in bare mode.

2025-07-03 08:10:11.772 503 GET /script-health-check (127.0.0.1) 102.72ms

2025-07-03 08:10:16.807 Script compilation error

Traceback (most recent call last):

  File "/home/adminuser/venv/lib/python3.13/site-packages/streamlit/runtime/scriptrunner/script_runner.py", line 571, in _run_script

    code = self._script_cache.get_bytecode(script_path)

  File "/home/adminuser/venv/lib/python3.13/site-packages/streamlit/runtime/scriptrunner/script_cache.py", line 72, in get_bytecode

    filebody = magic.add_magic(filebody, script_path)

  File "/home/adminuser/venv/lib/python3.13/site-packages/streamlit/runtime/scriptrunner/magic.py", line 45, in add_magic

    tree = ast.parse(code, script_path, "exec")

  File "/usr/local/lib/python3.13/ast.py", line 50, in parse

    return compile(source, filename, mode, flags,

                   _feature_version=feature_version, optimize=optimize)

  File "/mount/src/vardiologio/test.py", line 245

    display_missing_shifts(missing_shifts)

IndentationError: unexpected indent

2025-07-03 08:10:16.809 Thread 'MainThread': missing ScriptRunContext! This warning can be ignored when running in bare mode.

2025-07-03 08:10:16.901 503 GET /script-health-check (127.0.0.1) 102.85ms

2025-07-03 08:10:21.652 Script compilation error

Traceback (most recent call last):

  File "/home/adminuser/venv/lib/python3.13/site-packages/streamlit/runtime/scriptrunner/script_runner.py", line 571, in _run_script

    code = self._script_cache.get_bytecode(script_path)

  File "/home/adminuser/venv/lib/python3.13/site-packages/streamlit/runtime/scriptrunner/script_cache.py", line 72, in get_bytecode

    filebody = magic.add_magic(filebody, script_path)

  File "/home/adminuser/venv/lib/python3.13/site-packages/streamlit/runtime/scriptrunner/magic.py", line 45, in add_magic

    tree = ast.parse(code, script_path, "exec")

  File "/usr/local/lib/python3.13/ast.py", line 50, in parse

    return compile(source, filename, mode, flags,

                   _feature_version=feature_version, optimize=optimize)

  File "/mount/src/vardiologio/test.py", line 245

    display_missing_shifts(missing_shifts)

IndentationError: unexpected indent

2025-07-03 08:10:21.655 Thread 'MainThread': missing ScriptRunContext! This warning can be ignored when running in bare mode.

2025-07-03 08:10:21.748 503 GET /script-health-check (127.0.0.1) 102.33ms

2025-07-03 08:10:26.666 Script compilation error

Traceback (most recent call last):

  File "/home/adminuser/venv/lib/python3.13/site-packages/streamlit/runtime/scriptrunner/script_runner.py", line 571, in _run_script

    code = self._script_cache.get_bytecode(script_path)

  File "/home/adminuser/venv/lib/python3.13/site-packages/streamlit/runtime/scriptrunner/script_cache.py", line 72, in get_bytecode

    filebody = magic.add_magic(filebody, script_path)

  File "/home/adminuser/venv/lib/python3.13/site-packages/streamlit/runtime/scriptrunner/magic.py", line 45, in add_magic

    tree = ast.parse(code, script_path, "exec")

  File "/usr/local/lib/python3.13/ast.py", line 50, in parse

    return compile(source, filename, mode, flags,

                   _feature_version=feature_version, optimize=optimize)

  File "/mount/src/vardiologio/test.py", line 245

    display_missing_shifts(missing_shifts)

IndentationError: unexpected indent

2025-07-03 08:10:26.669 Thread 'MainThread': missing ScriptRunContext! This warning can be ignored when running in bare mode.

2025-07-03 08:10:26.759 503 GET /script-health-check (127.0.0.1) 102.23ms

2025-07-03 08:10:31.688 Script compilation error

Traceback (most recent call last):

  File "/home/adminuser/venv/lib/python3.13/site-packages/streamlit/runtime/scriptrunner/script_runner.py", line 571, in _run_script

    code = self._script_cache.get_bytecode(script_path)

  File "/home/adminuser/venv/lib/python3.13/site-packages/streamlit/runtime/scriptrunner/script_cache.py", line 72, in get_bytecode

    filebody = magic.add_magic(filebody, script_path)

  File "/home/adminuser/venv/lib/python3.13/site-packages/streamlit/runtime/scriptrunner/magic.py", line 45, in add_magic

    tree = ast.parse(code, script_path, "exec")

  File "/usr/local/lib/python3.13/ast.py", line 50, in parse

    return compile(source, filename, mode, flags,

                   _feature_version=feature_version, optimize=optimize)

  File "/mount/src/vardiologio/test.py", line 245

    display_missing_shifts(missing_shifts)

IndentationError: unexpected indent

2025-07-03 08:10:31.690 Thread 'MainThread': missing ScriptRunContext! This warning can be ignored when running in bare mode.

2025-07-03 08:10:31.783 503 GET /script-health-check (127.0.0.1) 101.86ms

2025-07-03 08:10:36.640 Script compilation error

Traceback (most recent call last):

  File "/home/adminuser/venv/lib/python3.13/site-packages/streamlit/runtime/scriptrunner/script_runner.py", line 571, in _run_script

    code = self._script_cache.get_bytecode(script_path)

  File "/home/adminuser/venv/lib/python3.13/site-packages/streamlit/runtime/scriptrunner/script_cache.py", line 72, in get_bytecode

    filebody = magic.add_magic(filebody, script_path)

  File "/home/adminuser/venv/lib/python3.13/site-packages/streamlit/runtime/scriptrunner/magic.py", line 45, in add_magic

    tree = ast.parse(code, script_path, "exec")

  File "/usr/local/lib/python3.13/ast.py", line 50, in parse

    return compile(source, filename, mode, flags,

                   _feature_version=feature_version, optimize=optimize)

  File "/mount/src/vardiologio/test.py", line 245

    display_missing_shifts(missing_shifts)

IndentationError: unexpected indent

2025-07-03 08:10:36.642 Thread 'MainThread': missing ScriptRunContext! This warning can be ignored when running in bare mode.

2025-07-03 08:10:36.735 503 GET /script-health-check (127.0.0.1) 101.92ms

2025-07-03 08:10:41.654 Script compilation error

Traceback (most recent call last):

  File "/home/adminuser/venv/lib/python3.13/site-packages/streamlit/runtime/scriptrunner/script_runner.py", line 571, in _run_script

    code = self._script_cache.get_bytecode(script_path)

  File "/home/adminuser/venv/lib/python3.13/site-packages/streamlit/runtime/scriptrunner/script_cache.py", line 72, in get_bytecode

    filebody = magic.add_magic(filebody, script_path)

  File "/home/adminuser/venv/lib/python3.13/site-packages/streamlit/runtime/scriptrunner/magic.py", line 45, in add_magic

    tree = ast.parse(code, script_path, "exec")

  File "/usr/local/lib/python3.13/ast.py", line 50, in parse

    return compile(source, filename, mode, flags,

                   _feature_version=feature_version, optimize=optimize)

  File "/mount/src/vardiologio/test.py", line 245

    display_missing_shifts(missing_shifts)

IndentationError: unexpected indent

2025-07-03 08:10:41.656 Thread 'MainThread': missing ScriptRunContext! This warning can be ignored when running in bare mode.

2025-07-03 08:10:41.750 503 GET /script-health-check (127.0.0.1) 102.76ms

2025-07-03 08:10:46.664 Script compilation error

Traceback (most recent call last):

  File "/home/adminuser/venv/lib/python3.13/site-packages/streamlit/runtime/scriptrunner/script_runner.py", line 571, in _run_script

    code = self._script_cache.get_bytecode(script_path)

  File "/home/adminuser/venv/lib/python3.13/site-packages/streamlit/runtime/scriptrunner/script_cache.py", line 72, in get_bytecode

    filebody = magic.add_magic(filebody, script_path)

  File "/home/adminuser/venv/lib/python3.13/site-packages/streamlit/runtime/scriptrunner/magic.py", line 45, in add_magic

    tree = ast.parse(code, script_path, "exec")

  File "/usr/local/lib/python3.13/ast.py", line 50, in parse

    return compile(source, filename, mode, flags,

                   _feature_version=feature_version, optimize=optimize)

  File "/mount/src/vardiologio/test.py", line 245

    display_missing_shifts(missing_shifts)

IndentationError: unexpected indent

2025-07-03 08:10:46.666 Thread 'MainThread': missing ScriptRunContext! This warning can be ignored when running in bare mode.

2025-07-03 08:10:46.759 503 GET /script-health-check (127.0.0.1) 102.73ms

2025-07-03 08:10:51.666 Script compilation error

Traceback (most recent call last):

  File "/home/adminuser/venv/lib/python3.13/site-packages/streamlit/runtime/scriptrunner/script_runner.py", line 571, in _run_script

    code = self._script_cache.get_bytecode(script_path)

  File "/home/adminuser/venv/lib/python3.13/site-packages/streamlit/runtime/scriptrunner/script_cache.py", line 72, in get_bytecode

    filebody = magic.add_magic(filebody, script_path)

  File "/home/adminuser/venv/lib/python3.13/site-packages/streamlit/runtime/scriptrunner/magic.py", line 45, in add_magic

    tree = ast.parse(code, script_path, "exec")

  File "/usr/local/lib/python3.13/ast.py", line 50, in parse

    return compile(source, filename, mode, flags,

                   _feature_version=feature_version, optimize=optimize)

  File "/mount/src/vardiologio/test.py", line 245

    display_missing_shifts(missing_shifts)

IndentationError: unexpected indent

2025-07-03 08:10:51.670 Thread 'MainThread': missing ScriptRunContext! This warning can be ignored when running in bare mode.

2025-07-03 08:10:51.759 503 GET /script-health-check (127.0.0.1) 102.29ms

2025-07-03 08:10:56.654 Script compilation error

Traceback (most recent call last):

  File "/home/adminuser/venv/lib/python3.13/site-packages/streamlit/runtime/scriptrunner/script_runner.py", line 571, in _run_script

    code = self._script_cache.get_bytecode(script_path)

  File "/home/adminuser/venv/lib/python3.13/site-packages/streamlit/runtime/scriptrunner/script_cache.py", line 72, in get_bytecode

    filebody = magic.add_magic(filebody, script_path)

  File "/home/adminuser/venv/lib/python3.13/site-packages/streamlit/runtime/scriptrunner/magic.py", line 45, in add_magic

    tree = ast.parse(code, script_path, "exec")

  File "/usr/local/lib/python3.13/ast.py", line 50, in parse

    return compile(source, filename, mode, flags,

                   _feature_version=feature_version, optimize=optimize)

  File "/mount/src/vardiologio/test.py", line 245

    display_missing_shifts(missing_shifts)

IndentationError: unexpected indent

2025-07-03 08:10:56.656 Thread 'MainThread': missing ScriptRunContext! This warning can be ignored when running in bare mode.

2025-07-03 08:10:56.750 503 GET /script-health-check (127.0.0.1) 101.98ms

2025-07-03 08:11:01.664 Script compilation error

Traceback (most recent call last):

  File "/home/adminuser/venv/lib/python3.13/site-packages/streamlit/runtime/scriptrunner/script_runner.py", line 571, in _run_script

    code = self._script_cache.get_bytecode(script_path)

  File "/home/adminuser/venv/lib/python3.13/site-packages/streamlit/runtime/scriptrunner/script_cache.py", line 72, in get_bytecode

    filebody = magic.add_magic(filebody, script_path)

  File "/home/adminuser/venv/lib/python3.13/site-packages/streamlit/runtime/scriptrunner/magic.py", line 45, in add_magic

    tree = ast.parse(code, script_path, "exec")

  File "/usr/local/lib/python3.13/ast.py", line 50, in parse

    return compile(source, filename, mode, flags,

                   _feature_version=feature_version, optimize=optimize)

  File "/mount/src/vardiologio/test.py", line 245

    display_missing_shifts(missing_shifts)

IndentationError: unexpected indent

2025-07-03 08:11:01.666 Thread 'MainThread': missing ScriptRunContext! This warning can be ignored when running in bare mode.

2025-07-03 08:11:01.761 503 GET /script-health-check (127.0.0.1) 102.95ms

2025-07-03 08:11:06.609 Script compilation error

Traceback (most recent call last):

  File "/home/adminuser/venv/lib/python3.13/site-packages/streamlit/runtime/scriptrunner/script_runner.py", line 571, in _run_script

    code = self._script_cache.get_bytecode(script_path)

  File "/home/adminuser/venv/lib/python3.13/site-packages/streamlit/runtime/scriptrunner/script_cache.py", line 72, in get_bytecode

    filebody = magic.add_magic(filebody, script_path)

  File "/home/adminuser/venv/lib/python3.13/site-packages/streamlit/runtime/scriptrunner/magic.py", line 45, in add_magic

    tree = ast.parse(code, script_path, "exec")

  File "/usr/local/lib/python3.13/ast.py", line 50, in parse

    return compile(source, filename, mode, flags,

                   _feature_version=feature_version, optimize=optimize)

  File "/mount/src/vardiologio/test.py", line 245

    display_missing_shifts(missing_shifts)

IndentationError: unexpected indent

2025-07-03 08:11:06.611 Thread 'MainThread': missing ScriptRunContext! This warning can be ignored when running in bare mode.

2025-07-03 08:11:06.706 503 GET /script-health-check (127.0.0.1) 102.85ms

2025-07-03 08:11:11.662 Script compilation error

Traceback (most recent call last):

  File "/home/adminuser/venv/lib/python3.13/site-packages/streamlit/runtime/scriptrunner/script_runner.py", line 571, in _run_script

    code = self._script_cache.get_bytecode(script_path)

  File "/home/adminuser/venv/lib/python3.13/site-packages/streamlit/runtime/scriptrunner/script_cache.py", line 72, in get_bytecode

    filebody = magic.add_magic(filebody, script_path)

  File "/home/adminuser/venv/lib/python3.13/site-packages/streamlit/runtime/scriptrunner/magic.py", line 45, in add_magic

    tree = ast.parse(code, script_path, "exec")

  File "/usr/local/lib/python3.13/ast.py", line 50, in parse

    return compile(source, filename, mode, flags,

                   _feature_version=feature_version, optimize=optimize)

  File "/mount/src/vardiologio/test.py", line 245

    display_missing_shifts(missing_shifts)

IndentationError: unexpected indent

2025-07-03 08:11:11.664 Thread 'MainThread': missing ScriptRunContext! This warning can be ignored when running in bare mode.

2025-07-03 08:11:11.757 503 GET /script-health-check (127.0.0.1) 102.17ms

2025-07-03 08:11:16.633 Script compilation error

Traceback (most recent call last):

  File "/home/adminuser/venv/lib/python3.13/site-packages/streamlit/runtime/scriptrunner/script_runner.py", line 571, in _run_script

    code = self._script_cache.get_bytecode(script_path)

  File "/home/adminuser/venv/lib/python3.13/site-packages/streamlit/runtime/scriptrunner/script_cache.py", line 72, in get_bytecode

    filebody = magic.add_magic(filebody, script_path)

  File "/home/adminuser/venv/lib/python3.13/site-packages/streamlit/runtime/scriptrunner/magic.py", line 45, in add_magic

    tree = ast.parse(code, script_path, "exec")

  File "/usr/local/lib/python3.13/ast.py", line 50, in parse

    return compile(source, filename, mode, flags,

                   _feature_version=feature_version, optimize=optimize)

  File "/mount/src/vardiologio/test.py", line 245

    display_missing_shifts(missing_shifts)

IndentationError: unexpected indent

2025-07-03 08:11:16.635 Thread 'MainThread': missing ScriptRunContext! This warning can be ignored when running in bare mode.

2025-07-03 08:11:16.729 503 GET /script-health-check (127.0.0.1) 102.29ms

2025-07-03 08:11:21.717 Script compilation error

Traceback (most recent call last):

  File "/home/adminuser/venv/lib/python3.13/site-packages/streamlit/runtime/scriptrunner/script_runner.py", line 571, in _run_script

    code = self._script_cache.get_bytecode(script_path)

  File "/home/adminuser/venv/lib/python3.13/site-packages/streamlit/runtime/scriptrunner/script_cache.py", line 72, in get_bytecode

    filebody = magic.add_magic(filebody, script_path)

  File "/home/adminuser/venv/lib/python3.13/site-packages/streamlit/runtime/scriptrunner/magic.py", line 45, in add_magic

    tree = ast.parse(code, script_path, "exec")

  File "/usr/local/lib/python3.13/ast.py", line 50, in parse

    return compile(source, filename, mode, flags,

                   _feature_version=feature_version, optimize=optimize)

  File "/mount/src/vardiologio/test.py", line 245

    display_missing_shifts(missing_shifts)

IndentationError: unexpected indent

2025-07-03 08:11:21.720 Thread 'MainThread': missing ScriptRunContext! This warning can be ignored when running in bare mode.

2025-07-03 08:11:21.814 503 GET /script-health-check (127.0.0.1) 105.85ms

2025-07-03 08:11:26.624 Script compilation error

Traceback (most recent call last):

  File "/home/adminuser/venv/lib/python3.13/site-packages/streamlit/runtime/scriptrunner/script_runner.py", line 571, in _run_script

    code = self._script_cache.get_bytecode(script_path)

  File "/home/adminuser/venv/lib/python3.13/site-packages/streamlit/runtime/scriptrunner/script_cache.py", line 72, in get_bytecode

    filebody = magic.add_magic(filebody, script_path)

  File "/home/adminuser/venv/lib/python3.13/site-packages/streamlit/runtime/scriptrunner/magic.py", line 45, in add_magic

    tree = ast.parse(code, script_path, "exec")

  File "/usr/local/lib/python3.13/ast.py", line 50, in parse

    return compile(source, filename, mode, flags,

                   _feature_version=feature_version, optimize=optimize)

  File "/mount/src/vardiologio/test.py", line 245

    display_missing_shifts(missing_shifts)

IndentationError: unexpected indent

2025-07-03 08:11:26.626 Thread 'MainThread': missing ScriptRunContext! This warning can be ignored when running in bare mode.

2025-07-03 08:11:26.718 503 GET /script-health-check (127.0.0.1) 102.07ms

2025-07-03 08:11:31.630 Script compilation error

Traceback (most recent call last):

  File "/home/adminuser/venv/lib/python3.13/site-packages/streamlit/runtime/scriptrunner/script_runner.py", line 571, in _run_script

    code = self._script_cache.get_bytecode(script_path)

  File "/home/adminuser/venv/lib/python3.13/site-packages/streamlit/runtime/scriptrunner/script_cache.py", line 72, in get_bytecode

    filebody = magic.add_magic(filebody, script_path)

  File "/home/adminuser/venv/lib/python3.13/site-packages/streamlit/runtime/scriptrunner/magic.py", line 45, in add_magic

    tree = ast.parse(code, script_path, "exec")

  File "/usr/local/lib/python3.13/ast.py", line 50, in parse

    return compile(source, filename, mode, flags,

                   _feature_version=feature_version, optimize=optimize)

  File "/mount/src/vardiologio/test.py", line 245

    display_missing_shifts(missing_shifts)

IndentationError: unexpected indent

2025-07-03 08:11:31.632 Thread 'MainThread': missing ScriptRunContext! This warning can be ignored when running in bare mode.

2025-07-03 08:11:31.726 503 GET /script-health-check (127.0.0.1) 102.62ms

2025-07-03 08:11:32.205 Script compilation error

Traceback (most recent call last):

  File "/home/adminuser/venv/lib/python3.13/site-packages/streamlit/runtime/scriptrunner/script_runner.py", line 571, in _run_script

    code = self._script_cache.get_bytecode(script_path)

  File "/home/adminuser/venv/lib/python3.13/site-packages/streamlit/runtime/scriptrunner/script_cache.py", line 72, in get_bytecode

    filebody = magic.add_magic(filebody, script_path)

  File "/home/adminuser/venv/lib/python3.13/site-packages/streamlit/runtime/scriptrunner/magic.py", line 45, in add_magic

    tree = ast.parse(code, script_path, "exec")

  File "/usr/local/lib/python3.13/ast.py", line 50, in parse

    return compile(source, filename, mode, flags,

                   _feature_version=feature_version, optimize=optimize)

  File "/mount/src/vardiologio/test.py", line 245

    display_missing_shifts(missing_shifts)

IndentationError: unexpected indent

2025-07-03 08:11:32.210 Thread 'MainThread': missing ScriptRunContext! This warning can be ignored when running in bare mode.

2025-07-03 08:11:36.633 Script compilation error

Traceback (most recent call last):

  File "/home/adminuser/venv/lib/python3.13/site-packages/streamlit/runtime/scriptrunner/script_runner.py", line 571, in _run_script

    code = self._script_cache.get_bytecode(script_path)

  File "/home/adminuser/venv/lib/python3.13/site-packages/streamlit/runtime/scriptrunner/script_cache.py", line 72, in get_bytecode

    filebody = magic.add_magic(filebody, script_path)

  File "/home/adminuser/venv/lib/python3.13/site-packages/streamlit/runtime/scriptrunner/magic.py", line 45, in add_magic

    tree = ast.parse(code, script_path, "exec")

  File "/usr/local/lib/python3.13/ast.py", line 50, in parse

    return compile(source, filename, mode, flags,

                   _feature_version=feature_version, optimize=optimize)

  File "/mount/src/vardiologio/test.py", line 245

    display_missing_shifts(missing_shifts)

IndentationError: unexpected indent

2025-07-03 08:11:36.635 Thread 'MainThread': missing ScriptRunContext! This warning can be ignored when running in bare mode.

2025-07-03 08:11:36.728 503 GET /script-health-check (127.0.0.1) 102.20ms

2025-07-03 08:11:41.647 Script compilation error

Traceback (most recent call last):

  File "/home/adminuser/venv/lib/python3.13/site-packages/streamlit/runtime/scriptrunner/script_runner.py", line 571, in _run_script

    code = self._script_cache.get_bytecode(script_path)

  File "/home/adminuser/venv/lib/python3.13/site-packages/streamlit/runtime/scriptrunner/script_cache.py", line 72, in get_bytecode

    filebody = magic.add_magic(filebody, script_path)

  File "/home/adminuser/venv/lib/python3.13/site-packages/streamlit/runtime/scriptrunner/magic.py", line 45, in add_magic

    tree = ast.parse(code, script_path, "exec")

  File "/usr/local/lib/python3.13/ast.py", line 50, in parse

    return compile(source, filename, mode, flags,

                   _feature_version=feature_version, optimize=optimize)

  File "/mount/src/vardiologio/test.py", line 245

    display_missing_shifts(missing_shifts)

IndentationError: unexpected indent

2025-07-03 08:11:41.649 Thread 'MainThread': missing ScriptRunContext! This warning can be ignored when running in bare mode.

2025-07-03 08:11:41.743 503 GET /script-health-check (127.0.0.1) 102.24ms

2025-07-03 08:11:46.659 Script compilation error

Traceback (most recent call last):

  File "/home/adminuser/venv/lib/python3.13/site-packages/streamlit/runtime/scriptrunner/script_runner.py", line 571, in _run_script

    code = self._script_cache.get_bytecode(script_path)

  File "/home/adminuser/venv/lib/python3.13/site-packages/streamlit/runtime/scriptrunner/script_cache.py", line 72, in get_bytecode

    filebody = magic.add_magic(filebody, script_path)

  File "/home/adminuser/venv/lib/python3.13/site-packages/streamlit/runtime/scriptrunner/magic.py", line 45, in add_magic

    tree = ast.parse(code, script_path, "exec")

  File "/usr/local/lib/python3.13/ast.py", line 50, in parse

    return compile(source, filename, mode, flags,

                   _feature_version=feature_version, optimize=optimize)

  File "/mount/src/vardiologio/test.py", line 245

    display_missing_shifts(missing_shifts)

IndentationError: unexpected indent

2025-07-03 08:11:46.661 Thread 'MainThread': missing ScriptRunContext! This warning can be ignored when running in bare mode.

2025-07-03 08:11:46.755 503 GET /script-health-check (127.0.0.1) 101.94ms

2025-07-03 08:11:51.631 Script compilation error

Traceback (most recent call last):

  File "/home/adminuser/venv/lib/python3.13/site-packages/streamlit/runtime/scriptrunner/script_runner.py", line 571, in _run_script

    code = self._script_cache.get_bytecode(script_path)

  File "/home/adminuser/venv/lib/python3.13/site-packages/streamlit/runtime/scriptrunner/script_cache.py", line 72, in get_bytecode

    filebody = magic.add_magic(filebody, script_path)

  File "/home/adminuser/venv/lib/python3.13/site-packages/streamlit/runtime/scriptrunner/magic.py", line 45, in add_magic

    tree = ast.parse(code, script_path, "exec")

  File "/usr/local/lib/python3.13/ast.py", line 50, in parse

    return compile(source, filename, mode, flags,

                   _feature_version=feature_version, optimize=optimize)

  File "/mount/src/vardiologio/test.py", line 245

    display_missing_shifts(missing_shifts)

IndentationError: unexpected indent

2025-07-03 08:11:51.633 Thread 'MainThread': missing ScriptRunContext! This warning can be ignored when running in bare mode.

2025-07-03 08:11:51.726 503 GET /script-health-check (127.0.0.1) 102.12ms

2025-07-03 08:11:56.725 Script compilation error

Traceback (most recent call last):

  File "/home/adminuser/venv/lib/python3.13/site-packages/streamlit/runtime/scriptrunner/script_runner.py", line 571, in _run_script

    code = self._script_cache.get_bytecode(script_path)

  File "/home/adminuser/venv/lib/python3.13/site-packages/streamlit/runtime/scriptrunner/script_cache.py", line 72, in get_bytecode

    filebody = magic.add_magic(filebody, script_path)

  File "/home/adminuser/venv/lib/python3.13/site-packages/streamlit/runtime/scriptrunner/magic.py", line 45, in add_magic

    tree = ast.parse(code, script_path, "exec")

  File "/usr/local/lib/python3.13/ast.py", line 50, in parse

    return compile(source, filename, mode, flags,

                   _feature_version=feature_version, optimize=optimize)

  File "/mount/src/vardiologio/test.py", line 245

    display_missing_shifts(missing_shifts)

IndentationError: unexpected indent

2025-07-03 08:11:56.729 Thread 'MainThread': missing ScriptRunContext! This warning can be ignored when running in bare mode.

2025-07-03 08:11:56.818 503 GET /script-health-check (127.0.0.1) 103.30ms

2025-07-03 08:12:01.600 Script compilation error

Traceback (most recent call last):

  File "/home/adminuser/venv/lib/python3.13/site-packages/streamlit/runtime/scriptrunner/script_runner.py", line 571, in _run_script

    code = self._script_cache.get_bytecode(script_path)

  File "/home/adminuser/venv/lib/python3.13/site-packages/streamlit/runtime/scriptrunner/script_cache.py", line 72, in get_bytecode

    filebody = magic.add_magic(filebody, script_path)

  File "/home/adminuser/venv/lib/python3.13/site-packages/streamlit/runtime/scriptrunner/magic.py", line 45, in add_magic

    tree = ast.parse(code, script_path, "exec")

  File "/usr/local/lib/python3.13/ast.py", line 50, in parse

    return compile(source, filename, mode, flags,

                   _feature_version=feature_version, optimize=optimize)

  File "/mount/src/vardiologio/test.py", line 245

    display_missing_shifts(missing_shifts)

IndentationError: unexpected indent

2025-07-03 08:12:01.602 Thread 'MainThread': missing ScriptRunContext! This warning can be ignored when running in bare mode.

2025-07-03 08:12:01.694 503 GET /script-health-check (127.0.0.1) 103.22ms

2025-07-03 08:12:06.691 Script compilation error

Traceback (most recent call last):

  File "/home/adminuser/venv/lib/python3.13/site-packages/streamlit/runtime/scriptrunner/script_runner.py", line 571, in _run_script

    code = self._script_cache.get_bytecode(script_path)

  File "/home/adminuser/venv/lib/python3.13/site-packages/streamlit/runtime/scriptrunner/script_cache.py", line 72, in get_bytecode

    filebody = magic.add_magic(filebody, script_path)

  File "/home/adminuser/venv/lib/python3.13/site-packages/streamlit/runtime/scriptrunner/magic.py", line 45, in add_magic

    tree = ast.parse(code, script_path, "exec")

  File "/usr/local/lib/python3.13/ast.py", line 50, in parse

    return compile(source, filename, mode, flags,

                   _feature_version=feature_version, optimize=optimize)

  File "/mount/src/vardiologio/test.py", line 245

    display_missing_shifts(missing_shifts)

IndentationError: unexpected indent

2025-07-03 08:12:06.693 Thread 'MainThread': missing ScriptRunContext! This warning can be ignored when running in bare mode.

2025-07-03 08:12:06.786 503 GET /script-health-check (127.0.0.1) 103.11ms

2025-07-03 08:12:11.666 Script compilation error

Traceback (most recent call last):

  File "/home/adminuser/venv/lib/python3.13/site-packages/streamlit/runtime/scriptrunner/script_runner.py", line 571, in _run_script

    code = self._script_cache.get_bytecode(script_path)

  File "/home/adminuser/venv/lib/python3.13/site-packages/streamlit/runtime/scriptrunner/script_cache.py", line 72, in get_bytecode

    filebody = magic.add_magic(filebody, script_path)

  File "/home/adminuser/venv/lib/python3.13/site-packages/streamlit/runtime/scriptrunner/magic.py", line 45, in add_magic

    tree = ast.parse(code, script_path, "exec")

  File "/usr/local/lib/python3.13/ast.py", line 50, in parse

    return compile(source, filename, mode, flags,

                   _feature_version=feature_version, optimize=optimize)

  File "/mount/src/vardiologio/test.py", line 245

    display_missing_shifts(missing_shifts)

IndentationError: unexpected indent

2025-07-03 08:12:11.669 Thread 'MainThread': missing ScriptRunContext! This warning can be ignored when running in bare mode.

2025-07-03 08:12:11.762 503 GET /script-health-check (127.0.0.1) 102.06ms

2025-07-03 08:12:16.737 Script compilation error

Traceback (most recent call last):

  File "/home/adminuser/venv/lib/python3.13/site-packages/streamlit/runtime/scriptrunner/script_runner.py", line 571, in _run_script

    code = self._script_cache.get_bytecode(script_path)

  File "/home/adminuser/venv/lib/python3.13/site-packages/streamlit/runtime/scriptrunner/script_cache.py", line 72, in get_bytecode

    filebody = magic.add_magic(filebody, script_path)

  File "/home/adminuser/venv/lib/python3.13/site-packages/streamlit/runtime/scriptrunner/magic.py", line 45, in add_magic

    tree = ast.parse(code, script_path, "exec")

  File "/usr/local/lib/python3.13/ast.py", line 50, in parse

    return compile(source, filename, mode, flags,

                   _feature_version=feature_version, optimize=optimize)

  File "/mount/src/vardiologio/test.py", line 245

    display_missing_shifts(missing_shifts)

IndentationError: unexpected indent

2025-07-03 08:12:16.739 Thread 'MainThread': missing ScriptRunContext! This warning can be ignored when running in bare mode.

2025-07-03 08:12:16.831 503 GET /script-health-check (127.0.0.1) 102.47ms

2025-07-03 08:12:21.664 Script compilation error

Traceback (most recent call last):

  File "/home/adminuser/venv/lib/python3.13/site-packages/streamlit/runtime/scriptrunner/script_runner.py", line 571, in _run_script

    code = self._script_cache.get_bytecode(script_path)

  File "/home/adminuser/venv/lib/python3.13/site-packages/streamlit/runtime/scriptrunner/script_cache.py", line 72, in get_bytecode

    filebody = magic.add_magic(filebody, script_path)

  File "/home/adminuser/venv/lib/python3.13/site-packages/streamlit/runtime/scriptrunner/magic.py", line 45, in add_magic

    tree = ast.parse(code, script_path, "exec")

  File "/usr/local/lib/python3.13/ast.py", line 50, in parse

    return compile(source, filename, mode, flags,

                   _feature_version=feature_version, optimize=optimize)

  File "/mount/src/vardiologio/test.py", line 245

    display_missing_shifts(missing_shifts)

IndentationError: unexpected indent

2025-07-03 08:12:21.666 Thread 'MainThread': missing ScriptRunContext! This warning can be ignored when running in bare mode.

2025-07-03 08:12:21.760 503 GET /script-health-check (127.0.0.1) 102.78ms

2025-07-03 08:12:26.653 Script compilation error

Traceback (most recent call last):

  File "/home/adminuser/venv/lib/python3.13/site-packages/streamlit/runtime/scriptrunner/script_runner.py", line 571, in _run_script

    code = self._script_cache.get_bytecode(script_path)

  File "/home/adminuser/venv/lib/python3.13/site-packages/streamlit/runtime/scriptrunner/script_cache.py", line 72, in get_bytecode

    filebody = magic.add_magic(filebody, script_path)

  File "/home/adminuser/venv/lib/python3.13/site-packages/streamlit/runtime/scriptrunner/magic.py", line 45, in add_magic

    tree = ast.parse(code, script_path, "exec")

  File "/usr/local/lib/python3.13/ast.py", line 50, in parse

    return compile(source, filename, mode, flags,

                   _feature_version=feature_version, optimize=optimize)

  File "/mount/src/vardiologio/test.py", line 245

    display_missing_shifts(missing_shifts)

IndentationError: unexpected indent

2025-07-03 08:12:26.654 Thread 'MainThread': missing ScriptRunContext! This warning can be ignored when running in bare mode.

2025-07-03 08:12:26.748 503 GET /script-health-check (127.0.0.1) 101.60ms

2025-07-03 08:12:31.721 Script compilation error

Traceback (most recent call last):

  File "/home/adminuser/venv/lib/python3.13/site-packages/streamlit/runtime/scriptrunner/script_runner.py", line 571, in _run_script

    code = self._script_cache.get_bytecode(script_path)

  File "/home/adminuser/venv/lib/python3.13/site-packages/streamlit/runtime/scriptrunner/script_cache.py", line 72, in get_bytecode

    filebody = magic.add_magic(filebody, script_path)

  File "/home/adminuser/venv/lib/python3.13/site-packages/streamlit/runtime/scriptrunner/magic.py", line 45, in add_magic

    tree = ast.parse(code, script_path, "exec")

  File "/usr/local/lib/python3.13/ast.py", line 50, in parse

    return compile(source, filename, mode, flags,

                   _feature_version=feature_version, optimize=optimize)

  File "/mount/src/vardiologio/test.py", line 245

    display_missing_shifts(missing_shifts)

IndentationError: unexpected indent

2025-07-03 08:12:31.724 Thread 'MainThread': missing ScriptRunContext! This warning can be ignored when running in bare mode.

2025-07-03 08:12:31.816 503 GET /script-health-check (127.0.0.1) 102.14ms

[08:12:35] 🐙 Pulling code changes from Github...

2025-07-03 08:12:36.231 Received event for non-watched path: /mount/src/vardiologio/test.py

[08:12:36] 📦 Processing dependencies...

[08:12:36] 📦 Processed dependencies!

[08:12:39] 🔄 Updated app!

2025-07-03 08:12:48.590 Uncaught app execution

Traceback (most recent call last):

  File "/home/adminuser/venv/lib/python3.13/site-packages/streamlit/runtime/scriptrunner/exec_code.py", line 128, in exec_func_with_error_handling

    result = func()

  File "/home/adminuser/venv/lib/python3.13/site-packages/streamlit/runtime/scriptrunner/script_runner.py", line 669, in code_to_exec

    exec(code, module.__dict__)  # noqa: S102

    ~~~~^^^^^^^^^^^^^^^^^^^^^^^

  File "/mount/src/vardiologio/test.py", line 249, in <module>

    main()

    ~~~~^^

  File "/mount/src/vardiologio/test.py", line 189, in main

    show_employees()

    ~~~~~~~~~~~~~~^^

  File "/mount/src/vardiologio/test.py", line 98, in show_employees

    st.experimental_rerun()

    ^^^^^^^^^^^^^^^^^^^^^

AttributeError: module 'streamlit' has no attribute 'experimental_rerun'. Did you mean: 'experimental_user'?

2025-07-03 08:12:49.811 Uncaught app execution

Traceback (most recent call last):

  File "/home/adminuser/venv/lib/python3.13/site-packages/streamlit/runtime/scriptrunner/exec_code.py", line 128, in exec_func_with_error_handling

    result = func()

  File "/home/adminuser/venv/lib/python3.13/site-packages/streamlit/runtime/scriptrunner/script_runner.py", line 669, in code_to_exec

    exec(code, module.__dict__)  # noqa: S102

    ~~~~^^^^^^^^^^^^^^^^^^^^^^^

  File "/mount/src/vardiologio/test.py", line 249, in <module>

    main()

    ~~~~^^

  File "/mount/src/vardiologio/test.py", line 189, in main

    show_employees()

    ~~~~~~~~~~~~~~^^

  File "/mount/src/vardiologio/test.py", line 98, in show_employees

    st.experimental_rerun()

    ^^^^^^^^^^^^^^^^^^^^^

AttributeError: module 'streamlit' has no attribute 'experimental_rerun'. Did you mean: 'experimental_user'?

[08:15:35] 🐙 Pulling code changes from Github...

2025-07-03 08:15:35.938 Uncaught app execution

Traceback (most recent call last):

  File "/home/adminuser/venv/lib/python3.13/site-packages/streamlit/runtime/scriptrunner/exec_code.py", line 128, in exec_func_with_error_handling

    result = func()

  File "/home/adminuser/venv/lib/python3.13/site-packages/streamlit/runtime/scriptrunner/script_runner.py", line 669, in code_to_exec

    exec(code, module.__dict__)  # noqa: S102

    ~~~~^^^^^^^^^^^^^^^^^^^^^^^

  File "/mount/src/vardiologio/test.py", line 250, in <module>

    main()

    ~~~~^^

  File "/mount/src/vardiologio/test.py", line 188, in main

    add_employee()

    ~~~~~~~~~~~~^^

  File "/mount/src/vardiologio/test.py", line 40, in add_employee

    employee = st.session_state.employees[st.session_state.edit_index]

               ~~~~~~~~~~~~~~~~~~~~~~~~~~^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

IndexError: list index out of range

[08:15:35] 📦 Processing dependencies...

[08:15:35] 📦 Processed dependencies!

[08:15:39] 🔄 Updated app!
# --- Schedule creation ---
def create_schedule():
    schedule = defaultdict(lambda: defaultdict(lambda: defaultdict(list)))
    missing_shifts = []
    work_streak = defaultdict(int)
    employee_work_days = defaultdict(int)
    employee_last_shift = defaultdict(lambda: {day: None for day in DAYS})

    while True:
        completed = True
        for i, day in enumerate(DAYS):
            for shift in st.session_state.active_shifts:
                for role in ROLES:
                    required = st.session_state.shift_requirements[day][shift][role]
                    assigned_count = sum([1 for names in schedule[day][shift].values() if role in names])

                    if assigned_count < required:
                        for e in st.session_state.employees:
                            name = e["name"]

                            if employee_work_days[name] >= 7 - e["days_off"]:
                                continue
                            if work_streak[name] >= 6:
                                continue
                            if shift not in e["availability"].get(day, []):
                                continue
                            if role not in e["roles"]:
                                continue
                            if shift == "Πρωί" and i > 0:
                                prev_day = DAYS[i - 1]
                                if employee_last_shift[name].get(prev_day) == "Βράδυ":
                                    continue

                            if name not in schedule[day][shift]:
                                schedule[day][shift][name] = []
                            if role not in schedule[day][shift][name]:
                                schedule[day][shift][name].append(role)
                                employee_work_days[name] += 1
                                work_streak[name] += 1
                                employee_last_shift[name][day] = shift
                                break

                    assigned_count = sum([1 for names in schedule[day][shift].values() if role in names])
                    if assigned_count < required:
                        completed = False
                        missing_shifts.append({"Ημέρα": day, "Βάρδια": shift, "Ρόλος": role, "Λείπουν": required - assigned_count})
        if completed:
            break
    return schedule, missing_shifts

# --- Display schedule ---
def display_schedule(schedule):
    rows = []
    for day in DAYS:
        for shift in st.session_state.active_shifts:
            for name, roles in schedule[day][shift].items():
                rows.append({"Ημέρα": day, "Βάρδια": shift, "Υπάλληλος": name, "Καθήκοντα": ", ".join(roles)})
    df = pd.DataFrame(rows)
    st.session_state.final_schedule_df = df
    st.markdown("### 📆 Πρόγραμμα Εβδομάδας")
    st.dataframe(df, use_container_width=True)

    # --- Export to CSV ---
    csv = df.to_csv(index=False).encode("utf-8")
    st.download_button("📥 Εξαγωγή σε CSV", data=csv, file_name="programma_vardion.csv", mime="text/csv")

    # --- Select Day Calendar-like Filter ---
    st.markdown("#### 🔎 Προβολή Ανά Ημέρα")
    selected_day = st.selectbox("Επιλέξτε Ημέρα", DAYS)
    day_df = df[df["Ημέρα"] == selected_day]
    st.dataframe(day_df, use_container_width=True)

# --- Display missing shift report ---
def display_missing_shifts(missing_shifts):
    if missing_shifts:
        df = pd.DataFrame(missing_shifts)
        st.markdown("### ⚠️ Μη Καλυμμένες Βάρδιες")
        st.dataframe(df, use_container_width=True)
    else:
        st.success("🎉 Όλες οι βάρδιες καλύφθηκαν επιτυχώς!")

# --- Main ---
def main():
    init_session()
    setup_parameters()
    add_employee()
    define_requirements()
    show_employees()

    if st.button("🧠 Δημιουργία Προγράμματος", use_container_width=True):
        schedule, missing_shifts = create_schedule()
        st.success("✅ Το πρόγραμμα δημιουργήθηκε!")
        display_schedule(schedule)
        display_missing_shifts(missing_shifts)

    # Αν δεν υπάρχει πρόγραμμα, βγάζουμε προειδοποίηση
    if st.session_state.final_schedule_df.empty:
        st.warning("⚠️ Δεν υπάρχει πρόγραμμα για προβολή. Δημιουργήστε πρώτα ένα.")
        return

    # --- Ημερομηνία βάσης εβδομάδας ---
    st.markdown("#### 🗓️ Ορισμός Ημερολογιακής Εβδομάδας")
    base_date = st.date_input("Επιλέξτε την ημερομηνία Δευτέρας της εβδομάδας", value=datetime.date(2025, 7, 1))
    day_dates = {day: base_date + datetime.timedelta(days=i) for i, day in enumerate(DAYS)}

    # --- Προβολή ανά ημέρα ---
    st.markdown("#### 🔎 Προβολή Ανά Ημέρα")
    selected_day = st.selectbox("Επιλέξτε Ημέρα", DAYS)
    day_df = st.session_state.final_schedule_df[st.session_state.final_schedule_df["Ημέρα"] == selected_day]
    st.dataframe(day_df, use_container_width=True)

    # --- Φιλτράρισμα ανά υπάλληλο ---
    st.markdown("#### 👤 Φιλτράρισμα Ανά Υπάλληλο")
    employees = st.session_state.final_schedule_df["Υπάλληλος"].unique().tolist()
    selected_employee = st.selectbox("Επιλέξτε Υπάλληλο", ["Όλοι"] + employees)
    if selected_employee != "Όλοι":
        emp_df = st.session_state.final_schedule_df[st.session_state.final_schedule_df["Υπάλληλος"] == selected_employee]
        st.dataframe(emp_df, use_container_width=True)

    # --- Ημερολογιακή Προβολή τύπου Google Calendar ---
    st.markdown("#### 🗓️ Ημερολογιακή Προβολή")
    df = st.session_state.final_schedule_df.copy()
    df["Ημερομηνία"] = df["Ημέρα"].map(day_dates)
    calendar_view = df.pivot_table(index="Βάρδια", columns="Ημερομηνία", values="Υπάλληλος", aggfunc=lambda x: ", ".join(x))
    st.dataframe(calendar_view.fillna(""), use_container_width=True)

    # --- Νόμιμος Έλεγχος Υπερβάσεων ---
    st.markdown("#### 🔔 Ειδοποιήσεις Παραβίασης Κανόνων")
    alerts = []
    work_hours = df.groupby("Υπάλληλος").size() * 8  # υποθέτουμε 8 ώρες/βάρδια
    for name, total_hours in work_hours.items():
        if total_hours > 48:
            alerts.append(f"⚠️ Ο υπάλληλος **{name}** ξεπερνά τις 48 ώρες/εβδομάδα (={total_hours} ώρες)")

    rest_violations = []
    for name in df["Υπάλληλος"].unique():
        emp_days = df[df["Υπάλληλος"] == name].sort_values("Ημερομηνία")
        previous_day = None
        for _, row in emp_days.iterrows():
            if previous_day and (row["Ημερομηνία"] - previous_day).days == 1:
                rest_violations.append(f"⚠️ Ο υπάλληλος **{name}** δουλεύει συνεχόμενες μέρες χωρίς ρεπό.")
            previous_day = row["Ημερομηνία"]

    if alerts or rest_violations:
        for alert in set(alerts + rest_violations):
            st.warning(alert)
    else:
        st.success("✅ Δεν εντοπίστηκαν παραβιάσεις στους βασικούς κανόνες ξεκούρασης και ωραρίου.")



main()
