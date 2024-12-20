import streamlit as st
import sqlite3
import hashlib
import random
import string

def setup_controller_db():
    conn = sqlite3.connect('controller_node.db')
    c = conn.cursor()
    c.execute('''
        CREATE TABLE IF NOT EXISTS profiles (
            identifier TEXT PRIMARY KEY,
            name TEXT,
            phone_number TEXT,
            shareable_address TEXT,
            family_info TEXT,
            migration_history TEXT,
            education_info TEXT,
            profession_info TEXT,
            medical_info TEXT,
            govt_info TEXT,
            criminal_info TEXT
        )
    ''')
    conn.commit()
    return conn, c

def generate_identifier_and_address(name, phone_number):
    random.seed()
    identifier = ''.join(random.choices(string.ascii_letters + string.digits, k=16))
    shareable_address = hashlib.sha256(f"{name}{phone_number}{identifier}".encode()).hexdigest()
    return identifier, shareable_address

def main():
    st.title("Profile Builder and Identifier Generator")

    conn, c = setup_controller_db()

    st.header("Step 1: Personal Information")
    name = st.text_input("Name")
    phone_number = st.text_input("Phone Number")

    st.header("Step 2: Family Information")
    family_info = {
        "father_name": st.text_input("Father's Name"),
        "mother_name": st.text_input("Mother's Name"),
        "father_phone": st.text_input("Father's Phone"),
        "mother_phone": st.text_input("Mother's Phone"),
    }

    st.header("Step 3: Migration History")
    migration_history = {
        "place_of_birth": st.text_input("Place of Birth"),
        "permanent_address": st.text_input("Permanent Address"),
        "current_address": st.text_input("Current Address"),
        "previous_address": st.text_input("Previous Address"),
        "place_of_work": st.text_input("Place of Work"),
    }

    st.header("Step 4: Education")
    education_info = {
        "degree": st.text_input("Degree"),
        "grade": st.text_input("Grade"),
    }

    st.header("Step 5: Professional Experience")
    profession_info = {
        "company": st.text_input("Company Name"),
        "position": st.text_input("Position"),
    }

    st.header("Step 6: Medical Information")
    medical_info = {
        "disease": st.text_input("Disease"),
        "medications": st.text_input("Medications"),
    }

    st.header("Step 7: Government Info")
    govt_info = {
        "tin_number": st.text_input("TIN Number"),
        "drivers_license": st.text_input("Driver's License"),
        "voter_id": st.text_input("Voter ID"),
    }

    st.header("Step 8: Criminal Information")
    criminal_info = {
        "crime": st.text_input("Crime Committed"),
        "case_status": st.text_input("Case Status"),
        "arresting_officer": st.text_input("Arresting Officer"),
    }

    if st.button("Generate Identifier and Shareable Address"):
        if name and phone_number:
            identifier, shareable_address = generate_identifier_and_address(name, phone_number)

            c.execute('''
                INSERT INTO profiles (
                    identifier, name, phone_number, shareable_address, family_info, 
                    migration_history, education_info, profession_info, medical_info, 
                    govt_info, criminal_info
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                identifier, name, phone_number, shareable_address,
                str(family_info), str(migration_history), str(education_info),
                str(profession_info), str(medical_info), str(govt_info), str(criminal_info)
            ))
            conn.commit()

            st.success("Profile created successfully!")
            st.write(f"Identifier: {identifier}")
            st.write(f"Shareable Address: {shareable_address}")
        else:
            st.error("Please fill out the required fields.")

if __name__ == "__main__":
    main()
