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
        if (
            st.session_state.edit_index is not None
            and 0 <= st.session_state.edit_index < len(st.session_state.employees)
        ):
            employee = st.session_state.employees[st.session_state.edit_index]
            name = st.text_input("Όνομα Υπαλλήλου", value=employee["name"])
            roles = st.multiselect("Ρόλοι (πόστα) που μπορεί να καλύψει", ROLES, default=employee["roles"])
            days_off = st.slider("Ρεπό ανά εβδομάδα (βάσει νόμου: τουλάχιστον 1)", 1, 3, employee["days_off"])
        else:
            st.session_state.edit_index = None  # reset index αν είναι άκυρο
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
