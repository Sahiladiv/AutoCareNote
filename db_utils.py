import mysql.connector
import streamlit as st

# --- Setup connection ---
def get_connection():
    return mysql.connector.connect(
        host="localhost",     # update with your MySQL host
        user="root",          # update with your MySQL username
        password="root",  # update with your MySQL password
        database="practice_pilot_mvp"
    )

# --- Insert Patient ---
def add_patient(first_name, last_name, phone, email, dob, gender, address, allergies):
    conn = get_connection()
    cursor = conn.cursor()
    query = """
        INSERT INTO patients (first_name, last_name, phone_number, email, date_of_birth, gender, address, allergies)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
    """
    cursor.execute(query, (first_name, last_name, phone, email, dob, gender, address, allergies))
    conn.commit()
    conn.close()
    return cursor.lastrowid

# --- Get Patients ---
def get_patients():
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM patients")
    rows = cursor.fetchall()
    conn.close()
    return rows

# --- Search Patient ---
def search_patient(term):
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)
    query = "SELECT * FROM patients WHERE first_name LIKE %s OR last_name LIKE %s OR phone_number LIKE %s OR email LIKE %s"
    cursor.execute(query, (f"%{term}%", f"%{term}%", f"%{term}%", f"%{term}%"))
    rows = cursor.fetchall()
    conn.close()
    return rows

# --- Get Patient Visits ---
def get_visits(patient_id):
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)
    query = "SELECT * FROM patient_visit WHERE patient_id = %s ORDER BY created_at DESC"
    cursor.execute(query, (patient_id,))
    rows = cursor.fetchall()
    conn.close()
    return rows

# --- Add Visit ---
def add_visit(patient_id, first_name, last_name, soap, summary):
    conn = get_connection()
    cursor = conn.cursor()
    from datetime import date
    current_date = date.today()
    patient_name = first_name  + " " + last_name
    query = "INSERT INTO patient_visit (patient_id, patient_name, visit_date, soap_note, summary) VALUES (%s, %s, %s, %s, %s)"
    cursor.execute(query, (patient_id, patient_name, current_date, soap, summary))
    conn.commit()
    conn.close()
