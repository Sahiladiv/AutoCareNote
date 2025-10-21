import streamlit as st
from graph import graph
from export_utils import export_pdf, export_docx
from datetime import date
from db_utils import add_patient, get_patients, search_patient, get_visits, add_visit

# --- Session State Setup ---
if "patients" not in st.session_state:
    st.session_state.patients = []
if "page" not in st.session_state:
    st.session_state.page = "Generate SOAP"

# --- Sidebar Navigation ---
st.sidebar.title("Medical Assistant-AI")
st.sidebar.markdown("### Navigate the app")


# --- Top Right Buttons ---
# --- Top Right Buttons --- #
top_col1, top_col2, top_col3 = st.columns([6, 1.5, 1.5])

with top_col2:
    if st.button("Add New Patient", use_container_width=True):
        st.session_state.page = "Add New Patient"

with top_col3:
    if st.button("Search Patient", use_container_width=True):
        st.session_state.page = "Search Patient"



# --- Left Panel ---- #
if st.sidebar.button("Generate SOAP"):
    st.session_state.page = "Generate SOAP"

if st.sidebar.button("Patient History"):
    st.session_state.page = "Patient History"



try:
    patients_list = get_patients()
    if patients_list:
        patient_labels = [f"{p['first_name']} {p['last_name']} (ID: {p['id']})" for p in patients_list]
        selected_label = st.sidebar.selectbox("Select Patient", patient_labels)
        selected_patient = next(p for p in patients_list if f"{p['first_name']} {p['last_name']} (ID: {p['id']})" == selected_label)
        st.sidebar.markdown(f"**Selected:** {selected_patient['first_name']} {selected_patient['last_name']} (ID: {selected_patient['id']})")
        st.session_state.selected_patient = selected_patient  # store for reuse
    else:
        st.sidebar.warning("No patients in DB.")
except Exception as e:
    st.sidebar.error(f"DB Error: {e}")

# --- Page: Generate SOAP ---
if st.session_state.page == "Generate SOAP":
    st.title("Generate SOAP Note")
    transcript = st.text_area("Paste Transcript", height=200)

    if st.button("Generate"):
        if transcript.strip():
            result = graph.invoke({"transcript": transcript})
            soap, summary = result["soap"], result["summary"]

            st.subheader("SOAP Note")
            st.code(soap)

            st.subheader("Patient Summary")
            st.write(summary)

            export_pdf(soap, summary, "output.pdf")
            export_docx(soap, summary, "output.docx")

            with open("output.pdf", "rb") as f:
                st.download_button("Download PDF", f, "output.pdf")
            with open("output.docx", "rb") as f:
                st.download_button("Download DOCX", f, "output.docx")

            # Save visit to DB
            if "selected_patient" in st.session_state:
                add_visit(st.session_state.selected_patient["id"],
                          st.session_state.selected_patient["first_name"],
                          st.session_state.selected_patient["last_name"], 
                          soap, summary)
                st.success("Visit saved to patient history.")


# --- Page: Add New Patient ---
elif st.session_state.page == "Add New Patient":
    st.title("Add New Patient")

    with st.form("add_patient_form", clear_on_submit=True):
        col1, col2 = st.columns(2)
        with col1:
            first_name = st.text_input("First Name")
            phone_number = st.text_input("Phone Number")
            date_of_birth = st.date_input("Date of Birth", value=date(1990, 1, 1))
            address = st.text_area("Address", height=100)
        with col2:
            last_name = st.text_input("Last Name")
            email = st.text_input("Email")
            gender = st.selectbox("Gender", ["Male", "Female", "Other"])
            allergies = st.text_area("Allergies (if any)", height=100)

        submitted = st.form_submit_button("Add Patient")

        if submitted:
            if first_name and last_name:
                patient_id = add_patient(first_name, last_name, phone_number, email, date_of_birth, gender, address, allergies)
                st.success(f"✅ Patient '{first_name} {last_name}' added successfully! (ID: {patient_id})")
            else:
                st.warning("⚠️ Please enter at least First and Last Name.")


# --- Page: Patient History ---
elif st.session_state.page == "Patient History":
    st.title("Patient History")

    # Ensure a patient is selected
    if "selected_patient" in st.session_state and st.session_state.selected_patient:
        selected_patient = st.session_state.selected_patient
        patient_visits = get_visits(selected_patient["id"])

        if patient_visits:
            st.subheader(f"Visit history for {selected_patient['first_name']} (ID: {selected_patient['id']})")

            # Prepare data for the table
            table_data = []
            for visit in patient_visits:
                table_data.append({
                    "Visit Date": visit["visit_date"].strftime("%Y-%m-%d"),
                    "SOAP Note (truncated)": visit["soap_note"][:150] + "..." if len(visit["soap_note"]) > 150 else visit["soap_note"],
                    "Summary (truncated)": visit["summary"][:150] + "..." if len(visit["summary"]) > 150 else visit["summary"],
                    "Created At": visit["created_at"].strftime("%Y-%m-%d %H:%M:%S")
                })

            # Display as dataframe
            st.dataframe(table_data, use_container_width=True)

        else:
            st.info("No visit history yet for this patient.")
    else:
        st.warning("Please select a patient from the dropdown on the sidebar.")


# --- Page: Search Patient ---
elif st.session_state.page == "Search Patient":
    st.title("Search Patient")

    search_term = st.text_input("Search by name or ID")
    if search_term:
        results = [p for p in st.session_state.patients if search_term.lower() in p["name"].lower() or search_term in p["id"]]
        if results:
            for p in results:
                st.markdown(f"**{p['name']}** (ID: {p['id']}) — Visits: {len(p['visits'])}")
        else:
            st.warning("No matching patients found.")
