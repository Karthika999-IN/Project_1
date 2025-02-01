import pymysql
import pandas as pd

# ✅ Corrected file path (use raw string r"" to prevent errors)
file_path = r"C:\Users\karthika\Desktop\healthcare\Healtcare-Dataset.xlsx - Sheet1.csv"

# ✅ Connect to MySQL (without specifying the database yet)
mydb = pymysql.connect(
    host="localhost",
    user="root",
    password="karthika"
)
mycursor = mydb.cursor()

# Step 1: Create Database if it doesn’t exist
mycursor.execute("CREATE DATABASE IF NOT EXISTS `karthika healthcare_data`")

# Step 2: Connect to the newly created database (without backticks around database name)
mydb = pymysql.connect(
    host="localhost",
    user="root",
    password="karthika",
    database="karthika healthcare_data"  # Database name without backticks
)
mycursor = mydb.cursor()

# Step 3: Create Table if it doesn’t exist
mycursor.execute("""
    CREATE TABLE IF NOT EXISTS patients (
        Patient_ID VARCHAR(255) PRIMARY KEY,
        Admit_Date DATE,
        Discharge_Date DATE,
        Diagnosis TEXT,
        Bed_Occupancy VARCHAR(255),
        Test TEXT,
        Doctor VARCHAR(255),
        Followup_Date DATE,
        Feedback TEXT,
        Billing_Amount DECIMAL(10,2),
        Health_Insurance_Amount DECIMAL(10,2)
    )
""")

# Step 4: Read the CSV file (handle missing values)
df = pd.read_csv(file_path, encoding="utf-8")

# Step 5: Convert Date Format (if needed)
date_columns = ["Admit_Date", "Discharge_Date", "Followup Date"]
for col in date_columns:
    df[col] = pd.to_datetime(df[col], errors="coerce").dt.strftime("%Y-%m-%d")

# Step 6: Replace NaN with None (for NULL in MySQL)
df = df.where(pd.notna(df), None)

# Step 7: Define the SQL query for inserting data
sql = """
    INSERT IGNORE INTO patients (Patient_ID, Admit_Date, Discharge_Date, Diagnosis, Bed_Occupancy, Test, Doctor, Followup_Date, Feedback, Billing_Amount, Health_Insurance_Amount)
    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
"""

# Step 8: Convert DataFrame to list of tuples and insert data in batch
values = [tuple(row) for row in df.values]
mycursor.executemany(sql, values)

# Step 9: Commit changes and close connection
mydb.commit()
print(mycursor.rowcount, "rows inserted successfully.")

# Close the cursor and connection
mycursor.close()
mydb.close()
import streamlit as st
import pymysql
import pandas as pd
import plotly.express as px

# Connect to MySQL
def get_data(query):
    connection = pymysql.connect(
        host='localhost',
        user='root',
        password='karthika',
        database='karthika healthcare_data'
    )
    df = pd.read_sql(query, connection)
    connection.close()
    return df

# Title
st.title('Healthcare Data Analysis Dashboard')

# Sidebar for user selections
st.sidebar.header('Filters')

# Query 1: Trends in Admission Over Time
st.header('Trends in Patient Admissions Over Time')
query = """
SELECT DATE_FORMAT(Admit_Date, '%Y-%m') AS Admission_Month, COUNT(Patient_ID) AS Admissions
FROM patients
GROUP BY Admission_Month
ORDER BY Admission_Month
"""
admission_data = get_data(query)
fig1 = px.line(admission_data, x='Admission_Month', y='Admissions', title='Monthly Admissions Trend')
st.plotly_chart(fig1)

# Query 2: Diagnosis Frequency Analysis
st.header('Top 5 Common Diagnoses')
query = """
SELECT Diagnosis, COUNT(Patient_ID) AS Diagnosis_Count
FROM patients
GROUP BY Diagnosis
ORDER BY Diagnosis_Count DESC
LIMIT 5
"""
diagnosis_data = get_data(query)
fig2 = px.bar(diagnosis_data, x='Diagnosis', y='Diagnosis_Count', title='Top 5 Most Common Diagnoses')
st.plotly_chart(fig2)

# Query 3: Bed Occupancy Analysis
st.header('Bed Occupancy Distribution')
query = """
SELECT Bed_Occupancy, COUNT(Patient_ID) AS Occupancy_Count
FROM patients
GROUP BY Bed_Occupancy
"""
bed_occupancy_data = get_data(query)
fig3 = px.pie(bed_occupancy_data, names='Bed_Occupancy', values='Occupancy_Count', title='Bed Occupancy Distribution')
st.plotly_chart(fig3)

# Query 4: Length of Stay Distribution
st.header('Length of Stay Distribution')
query = """
SELECT AVG(DATEDIFF(Discharge_Date, Admit_Date)) AS Avg_Length_Of_Stay, 
       MAX(DATEDIFF(Discharge_Date, Admit_Date)) AS Max_Length_Of_Stay
FROM patients
"""
length_of_stay_data = get_data(query)
st.write(length_of_stay_data)

# Query 5: Seasonal Admission Patterns
st.header('Seasonal Admission Patterns')
query = """
SELECT MONTH(Admit_Date) AS Admission_Month, COUNT(Patient_ID) AS Admissions
FROM patients
GROUP BY Admission_Month
ORDER BY Admission_Month
"""
seasonal_data = get_data(query)
fig4 = px.bar(seasonal_data, x='Admission_Month', y='Admissions', title='Seasonal Admission Patterns')
st.plotly_chart(fig4)

# Additional Queries as needed can be added in a similar way

# Query 6: Feedback Distribution
st.header('Feedback Distribution')
query6 = """
SELECT Feedback, COUNT(Patient_ID) AS Feedback_Count
FROM patients
GROUP BY Feedback
"""
feedback_data = get_data(query6)
fig6 = px.bar(feedback_data, x='Feedback', y='Feedback_Count', title='Feedback Distribution')
st.plotly_chart(fig6)

# Query 7: Billing Amount Analysis
st.header('Billing Amount Distribution')
query7 = """
SELECT SUM(Billing_Amount) AS Total_Billing_Amount, AVG(Billing_Amount) AS Average_Billing_Amount
FROM patients
"""
billing_data = get_data(query7)
st.write(billing_data)

# Query 8: Insurance Payment Analysis
st.header('Health Insurance Payment Distribution')
query8 = """
SELECT SUM(Health_Insurance_Amount) AS Total_Insurance_Payment, AVG(Health_Insurance_Amount) AS Average_Insurance_Payment
FROM patients
"""
insurance_data = get_data(query8)
st.write(insurance_data)

# Query 9: Doctor-Specific Admission Analysis
st.header('Admissions by Doctor')
query9 = """
SELECT Doctor, COUNT(Patient_ID) AS Doctor_Admissions
FROM patients
GROUP BY Doctor
ORDER BY Doctor_Admissions DESC
"""
doctor_data = get_data(query9)
fig9 = px.bar(doctor_data, x='Doctor', y='Doctor_Admissions', title='Admissions by Doctor')
st.plotly_chart(fig9)

# Query 10: Length of Stay by Diagnosis
st.header('Length of Stay by Diagnosis')
query10 = """
SELECT Diagnosis, AVG(DATEDIFF(Discharge_Date, Admit_Date)) AS Avg_Length_Of_Stay
FROM patients
GROUP BY Diagnosis
ORDER BY Avg_Length_Of_Stay DESC
"""
length_of_stay_diagnosis_data = get_data(query10)
fig10 = px.bar(length_of_stay_diagnosis_data, x='Diagnosis', y='Avg_Length_Of_Stay', title='Length of Stay by Diagnosis')
st.plotly_chart(fig10)

# Query 11: Follow-up Appointments Distribution
st.header('Follow-up Appointment Distribution')
query11 = """
SELECT COUNT(Patient_ID) AS Followup_Count
FROM patients
WHERE Followup_Date IS NOT NULL
"""
followup_data = get_data(query11)
st.write(followup_data)

# Query 12: Common Tests Ordered
st.header('Most Common Tests Ordered')
query12 = """
SELECT Test, COUNT(Patient_ID) AS Test_Count
FROM patients
GROUP BY Test
ORDER BY Test_Count DESC
LIMIT 5
"""
test_data = get_data(query12)
fig12 = px.bar(test_data, x='Test', y='Test_Count', title='Most Common Tests Ordered')
st.plotly_chart(fig12)

# Query 13: Viral Infections Trend
st.header('Viral Infections Trend')
query13 = """
SELECT DATE_FORMAT(Admit_Date, '%Y-%m') AS Admission_Month, COUNT(Patient_ID) AS Viral_Infections
FROM patients
WHERE Diagnosis = 'Viral Infection'
GROUP BY Admission_Month
ORDER BY Admission_Month
"""
viral_infections_data = get_data(query13)
fig13 = px.line(viral_infections_data, x='Admission_Month', y='Viral_Infections', title='Viral Infections Over Time')
st.plotly_chart(fig13)

# Query 14: Average Billing by Doctor
st.header('Average Billing by Doctor')
query14 = """
SELECT Doctor, AVG(Billing_Amount) AS Avg_Billing_Amount
FROM patients
GROUP BY Doctor
ORDER BY Avg_Billing_Amount DESC
"""
doctor_billing_data = get_data(query14)
fig14 = px.bar(doctor_billing_data, x='Doctor', y='Avg_Billing_Amount', title='Average Billing by Doctor')
st.plotly_chart(fig14)

# Query 15: Bed Occupancy by Diagnosis
st.header('Bed Occupancy by Diagnosis')
query15 = """
SELECT Diagnosis, Bed_Occupancy, COUNT(Patient_ID) AS Occupancy_Count
FROM patients
GROUP BY Diagnosis, Bed_Occupancy
ORDER BY Occupancy_Count DESC
"""
bed_occupancy_diagnosis_data = get_data(query15)
fig15 = px.bar(bed_occupancy_diagnosis_data, x='Diagnosis', y='Occupancy_Count', color='Bed_Occupancy', title='Bed Occupancy by Diagnosis')
st.plotly_chart(fig15)

# Query 16: Seasonal Feedback Patterns
st.header('Seasonal Feedback Patterns')
query16 = """
SELECT MONTH(Followup_Date) AS Followup_Month, Feedback, COUNT(Patient_ID) AS Feedback_Count
FROM patients
WHERE Followup_Date IS NOT NULL
GROUP BY Followup_Month, Feedback
ORDER BY Followup_Month, Feedback_Count DESC
"""
feedback_seasonal_data = get_data(query16)
fig16 = px.bar(feedback_seasonal_data, x='Followup_Month', y='Feedback_Count', color='Feedback', title='Seasonal Feedback Patterns')
st.plotly_chart(fig16)

# Query 17: Billing vs Insurance Amount
st.header('Billing vs Insurance Amount')
query17 = """
SELECT SUM(Billing_Amount) AS Total_Billing_Amount, SUM(Health_Insurance_Amount) AS Total_Insurance_Amount
FROM patients
"""
billing_vs_insurance_data = get_data(query17)
st.write(billing_vs_insurance_data)

# Query 18: Followup Appointments Over Time
st.header('Followup Appointments Over Time')
query18 = """
SELECT DATE_FORMAT(Followup_Date, '%Y-%m') AS Followup_Month, COUNT(Patient_ID) AS Followup_Count
FROM patients
WHERE Followup_Date IS NOT NULL
GROUP BY Followup_Month
ORDER BY Followup_Month
"""
followup_time_data = get_data(query18)
fig18 = px.line(followup_time_data, x='Followup_Month', y='Followup_Count', title='Followup Appointments Over Time')
st.plotly_chart(fig18)

