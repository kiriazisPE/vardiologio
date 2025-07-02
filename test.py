import streamlit as st
import pandas as pd
from collections import defaultdict
import datetime

# --- Config ---
st.set_page_config(page_title="Πρόγραμμα Βαρδιών", layout="centered")
st.title("📅 Δημιουργία Προγράμματος Βαρδιών")
st.caption("Απλοποιημένο εργαλείο κατανομής βαρδιών για καταστήματα εστίασης")

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

# --- Add employee ---
def add_employee():
    with st.expander("➕ Προσθήκη Νέου Υπαλλήλου"):
        cols = st.columns(2)
        name = cols[0].text_input("Όνομα Υπαλλήλου")
        days_off = cols[1].slider("Ρεπό ανά εβδομάδα", 0, 3, 2)
        roles = st.multiselect("Πόστα που μπορεί να καλύψει", ROLES, default=ROLES)

        st.markdown("**Διαθεσιμότητα ανά ημέρα**")
        availability = {}
        for day in DAYS:
            availability[day] = st.multiselect(f"{day}", SHIFTS, default=SHIFTS, key=f"{name}-{day}")

        if st.button("💾 Καταχώρηση Υπαλλήλου") and name:
            st.session_state.employees.append({
                "name": name,
                "roles": roles,
                "days_off": days_off,
                "availability": availability,
                "absences": []
            })
            st.success(f"Ο υπάλληλος {name} προστέθηκε.")

# --- Define shift requirements ---
def define_requirements():
    st.subheader("🔧 Ορισμός Αναγκών Βαρδιών")
    for day in DAYS:
        with st.expander(f"📅 {day}"):
            for shift in SHIFTS:
                cols = st.columns(len(ROLES))
                for idx, role in enumerate(ROLES):
                    key = f"{day}-{shift}-{role}"
                    val = cols[idx].number_input(f"{shift} - {role}", min_value=0, value=0, step=1, key=key)
                    st.session_state.shift_requirements[day][shift][role] = val

# --- Display employees ---
def show_employees():
    with st.expander("👥 Λίστα Υπαλλήλων", expanded=True):
        if st.session_state.employees:
            df = pd.DataFrame([{
                "Όνομα": e["name"],
                "Πόστα": ", ".join(e["roles"]),
                "Ρεπό/εβδ": e["days_off"]
            } for e in st.session_state.employees])
            st.dataframe(df, use_container_width=True)
        else:
            st.info("Δεν υπάρχουν ακόμη υπάλληλοι.")

# --- Schedule creation ---
def create_schedule():
    schedule = defaultdict(lambda: defaultdict(lambda: defaultdict(list)))
    employee_work_days = defaultdict(int)

    while True:
        completed = True
        for day in DAYS:
            for shift in SHIFTS:
                for role in ROLES:
                    required = st.session_state.shift_requirements[day][shift][role]
                    assigned_count = sum([1 for names in schedule[day][shift].values() if role in names])

                    if assigned_count < required:
                        for e in st.session_state.employees:
                            name = e["name"]
                            if shift not in e["availability"].get(day, []):
                                continue
                            if role not in e["roles"]:
                                continue
                            if employee_work_days[name] >= 7 - e["days_off"]:
                                continue
                            if name not in schedule[day][shift]:
                                schedule[day][shift][name] = []
                            if role not in schedule[day][shift][name]:
                                schedule[day][shift][name].append(role)
                            employee_work_days[name] += 1
                            break
                    assigned_count = sum([1 for names in schedule[day][shift].values() if role in names])
                    if assigned_count < required:
                        completed = False
        if completed:
            break
    return schedule

# --- Display schedule ---
def display_schedule(schedule):
    rows = []
    for day in DAYS:
        for shift in SHIFTS:
            for name, roles in schedule[day][shift].items():
                rows.append({"Ημέρα": day, "Βάρδια": shift, "Όνομα": name, "Πόστα": ", ".join(roles)})
    df = pd.DataFrame(rows)
    st.subheader("📆 Τελικό Πρόγραμμα Βαρδιών")
    st.dataframe(df, use_container_width=True)

# --- Main ---
def main():
    init_session()
    st.markdown("---")
    add_employee()
    st.markdown("---")
    define_requirements()
    st.markdown("---")
    show_employees()

    if st.button("🚀 Δημιουργία Προγράμματος", use_container_width=True):
        schedule = create_schedule()
        st.success("✅ Το πρόγραμμα δημιουργήθηκε!")
        display_schedule(schedule)

main()
