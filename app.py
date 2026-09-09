from flask import Flask, render_template, request, redirect, url_for
import mysql.connector

app = Flask(__name__)


# ==========================================
# MySQL Database Connection
# ==========================================

def get_db_connection():

    connection = mysql.connector.connect(
        host="localhost",
        user="root",
        password="REMOVED_PASSWORD",
        database="CollegeManagement"
    )

    return connection


# ==========================================
# STUDENT INFORMATION
# ==========================================

@app.route("/")
def index():

    connection = get_db_connection()
    cursor = connection.cursor(dictionary=True)

    cursor.execute(
        "SELECT * FROM Student ORDER BY StudentId DESC"
    )

    students = cursor.fetchall()

    cursor.close()
    connection.close()

    return render_template(
        "index.html",
        students=students
    )


# ==========================================
# ADD STUDENT
# ==========================================

@app.route("/add_student", methods=["POST"])
def add_student():

    student_name = request.form["StudentName"]
    register_no = request.form["RegisterNo"]
    department = request.form["Department"]
    year = request.form["Year"]
    gender = request.form["Gender"]
    date_of_birth = request.form["DateOfBirth"]
    phone_no = request.form["PhoneNo"]
    email = request.form["Email"]
    address = request.form["Address"]

    connection = get_db_connection()
    cursor = connection.cursor()

    try:

        # Check Register Number
        cursor.execute(
            "SELECT StudentId FROM Student WHERE RegisterNo = %s",
            (register_no,)
        )

        existing_register = cursor.fetchone()

        if existing_register:

            return """
                <script>
                    alert("Register Number already exists. Please enter a different Register Number.");
                    window.history.back();
                </script>
            """

        # Check Phone Number
        cursor.execute(
            "SELECT StudentId FROM Student WHERE PhoneNo = %s",
            (phone_no,)
        )

        existing_phone = cursor.fetchone()

        if existing_phone:

            return """
                <script>
                    alert("Phone Number already exists. Please enter a different Phone Number.");
                    window.history.back();
                </script>
            """

        # Insert Student
        query = """
            INSERT INTO Student
            (
                StudentName,
                RegisterNo,
                Department,
                Year,
                Gender,
                DateOfBirth,
                PhoneNo,
                Email,
                Address
            )
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
        """

        values = (
            student_name,
            register_no,
            department,
            year,
            gender,
            date_of_birth,
            phone_no,
            email,
            address
        )

        cursor.execute(query, values)

        connection.commit()

        return redirect(url_for("index"))

    except mysql.connector.Error as error:

        connection.rollback()

        print("Database Error:", error)

        return """
            <script>
                alert("Unable to save student details. Please try again.");
                window.history.back();
            </script>
        """

    finally:

        cursor.close()
        connection.close()


# ==========================================
# ATTENDANCE PAGE
# ==========================================

@app.route("/attendance")
def attendance():

    connection = get_db_connection()
    cursor = connection.cursor(dictionary=True)

    # Get students for dropdown
    cursor.execute("""
        SELECT StudentId, StudentName, RegisterNo
        FROM Student
        ORDER BY StudentName
    """)

    students = cursor.fetchall()

    # Get attendance records
    cursor.execute("""
        SELECT
            a.AttendanceId,
            a.StudentId,
            s.StudentName,
            s.RegisterNo,
            a.Date,
            a.Subject,
            a.Status,
            a.Remarks
        FROM Attendance a
        JOIN Student s
        ON a.StudentId = s.StudentId
        ORDER BY a.Date DESC
    """)

    attendance_records = cursor.fetchall()

    cursor.close()
    connection.close()

    return render_template(
        "attendance.html",
        students=students,
        attendance_records=attendance_records
    )


# ==========================================
# ADD ATTENDANCE
# ==========================================

@app.route("/add_attendance", methods=["POST"])
def add_attendance():

    student_id = request.form["StudentId"]
    date = request.form["Date"]
    subject = request.form["Subject"]
    status = request.form["Status"]
    remarks = request.form.get("Remarks", "")

    connection = get_db_connection()
    cursor = connection.cursor()

    try:

        query = """
            INSERT INTO Attendance
            (
                StudentId,
                Date,
                Subject,
                Status,
                Remarks
            )
            VALUES (%s, %s, %s, %s, %s)
        """

        values = (
            student_id,
            date,
            subject,
            status,
            remarks
        )

        cursor.execute(query, values)

        connection.commit()

        return redirect(url_for("attendance"))

    except mysql.connector.Error as error:

        connection.rollback()

        print("Attendance Database Error:", error)

        return """
            <script>
                alert("Unable to save attendance.");
                window.history.back();
            </script>
        """

    finally:

        cursor.close()
        connection.close()


# ==========================================
# MARKS PAGE
# ==========================================

@app.route("/marks")
def marks():

    connection = get_db_connection()
    cursor = connection.cursor(dictionary=True)

    # Get students for dropdown
    cursor.execute("""
        SELECT StudentId, StudentName, RegisterNo
        FROM Student
        ORDER BY StudentName
    """)

    students = cursor.fetchall()

    # Get marks records
    cursor.execute("""
        SELECT
            m.MarkId,
            m.StudentId,
            s.StudentName,
            s.RegisterNo,
            m.SubjectId,
            m.InternalMark,
            m.ExternalMark,
            m.TotalMark,
            m.Grade,
            m.Result
        FROM Marks m
        JOIN Student s
        ON m.StudentId = s.StudentId
        ORDER BY m.MarkId DESC
    """)

    marks_records = cursor.fetchall()

    cursor.close()
    connection.close()

    return render_template(
        "marks.html",
        students=students,
        marks_records=marks_records
    )


# ==========================================
# ADD MARKS
# ==========================================

@app.route("/add_marks", methods=["POST"])
def add_marks():

    student_id = request.form["StudentId"]
    subject_id = request.form["SubjectId"]

    internal_mark = float(
        request.form["InternalMark"]
    )

    external_mark = float(
        request.form["ExternalMark"]
    )

    # Calculate Total
    total_mark = internal_mark + external_mark


    # Calculate Grade
    if total_mark >= 90:

        grade = "A+"

    elif total_mark >= 80:

        grade = "A"

    elif total_mark >= 70:

        grade = "B"

    elif total_mark >= 60:

        grade = "C"

    elif total_mark >= 50:

        grade = "D"

    else:

        grade = "F"


    # Calculate Result
    if total_mark >= 50:

        result = "Pass"

    else:

        result = "Fail"


    connection = get_db_connection()
    cursor = connection.cursor()

    try:

        query = """
            INSERT INTO Marks
            (
                StudentId,
                SubjectId,
                InternalMark,
                ExternalMark,
                TotalMark,
                Grade,
                Result
            )
            VALUES (%s, %s, %s, %s, %s, %s, %s)
        """

        values = (
            student_id,
            subject_id,
            internal_mark,
            external_mark,
            total_mark,
            grade,
            result
        )

        cursor.execute(query, values)

        connection.commit()

        return redirect(url_for("marks"))

    except mysql.connector.Error as error:

        connection.rollback()

        print("Marks Database Error:", error)

        return """
            <script>
                alert("Unable to save marks.");
                window.history.back();
            </script>
        """

    finally:

        cursor.close()
        connection.close()


# ==========================================
# RUN FLASK APPLICATION
# ==========================================

if __name__ == "__main__":

    app.run(debug=True)