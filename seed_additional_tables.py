#!/usr/bin/env python3
"""
Seed remaining relational/utility tables so that every table has data:
- Faculty_Class
- Class_Subject
- Alert / User_Alert
- Audit_Log
- Notification_Queue
"""

import os
import sys
from datetime import datetime

script_dir = os.path.dirname(os.path.abspath(__file__))
backend_path = os.path.join(script_dir, 'backend')
sys.path.insert(0, backend_path)

from database import DatabaseManager  # type: ignore


def seed_faculty_class(db: DatabaseManager):
    faculties = db.execute_query(
        "SELECT User_ID FROM Faculty",
        fetch=True
    ) or []
    classes = db.execute_query(
        "SELECT Class_ID FROM Class",
        fetch=True
    ) or []

    if not faculties or not classes:
        return

    pairs = []
    for i, fac in enumerate(faculties):
        fac_id = fac["User_ID"]
        # Assign each faculty to up to 4 classes in a round-robin fashion
        for cls in classes[i::len(faculties)][:4]:
            pairs.append((fac_id, cls["Class_ID"]))

    for fac_id, class_id in pairs:
        db.execute_query(
            """INSERT IGNORE INTO Faculty_Class (User_ID, Class_ID)
               VALUES (%s, %s)""",
            (fac_id, class_id),
        )


def seed_class_subject(db: DatabaseManager):
    subjects = db.execute_query(
        "SELECT Subject_ID, Class_ID FROM Subject",
        fetch=True
    ) or []

    for subj in subjects:
        sid = subj["Subject_ID"]
        cid = subj["Class_ID"]
        if not cid:
            continue
        db.execute_query(
            """INSERT IGNORE INTO Class_Subject (Class_ID, Subject_ID)
               VALUES (%s, %s)""",
            (cid, sid),
        )


def seed_alerts(db: DatabaseManager):
    # Create a couple of generic alerts from the first faculty user
    creator = db.execute_query(
        "SELECT User_ID FROM Faculty LIMIT 1",
        fetch_one=True
    )
    if not creator:
        return

    creator_id = creator["User_ID"]

    alerts_data = [
        ("Low Attendance Warning",
         "HIGH",
         "Some students have attendance below 75%. Please review and take action."),
        ("System Maintenance",
         "NORMAL",
         "Attendance system will be under maintenance this weekend."),
    ]

    alert_ids = []
    for alert_type, priority, message in alerts_data:
        alert_id = db.execute_query(
            """INSERT INTO Alert (Alert_Type, alert_priority, Created_By, Message)
               VALUES (%s, %s, %s, %s)""",
            (alert_type, priority, creator_id, message),
        )
        alert_ids.append(alert_id)

    # Link all students to the first alert, and all faculty to the second
    students = db.execute_query(
        "SELECT User_ID FROM Students",
        fetch=True
    ) or []
    faculties = db.execute_query(
        "SELECT User_ID FROM Faculty",
        fetch=True
    ) or []

    if alert_ids:
        first_alert = alert_ids[0]
        second_alert = alert_ids[-1]

        for s in students:
            db.execute_query(
                """INSERT IGNORE INTO User_Alert (User_ID, Alert_ID)
                   VALUES (%s, %s)""",
                (s["User_ID"], first_alert),
            )

        for f in faculties:
            db.execute_query(
                """INSERT IGNORE INTO User_Alert (User_ID, Alert_ID)
                   VALUES (%s, %s)""",
                (f["User_ID"], second_alert),
            )


def seed_audit_log(db: DatabaseManager):
    # Log a simple seed event
    now = datetime.now()
    db.execute_query(
        """INSERT INTO Audit_Log
           (User_ID, Action_Type, Table_Name, Record_ID, Old_Value, New_Value, Timestamp, IP_Address)
           VALUES (%s, %s, %s, %s, %s, %s, %s, %s)""",
        (
            None,
            "SEED",
            "ALL",
            None,
            None,
            "Initial demo data populated",
            now,
            "127.0.0.1",
        ),
    )


def seed_notification_queue(db: DatabaseManager):
    # Queue a sample notification for the first student
    student = db.execute_query(
        "SELECT u.User_ID, u.Email, u.Name FROM User u "
        "JOIN Students s ON u.User_ID = s.User_ID LIMIT 1",
        fetch_one=True,
    )
    if not student:
        return

    db.execute_query(
        """INSERT INTO Notification_Queue
           (User_ID, Notification_Type, Recipient, Subject, Message, Status)
           VALUES (%s, %s, %s, %s, %s, %s)""",
        (
            student["User_ID"],
            "Email",
            student["Email"],
            "Welcome to Smart Attendance System",
            f"Hello {student['Name']}, your profile has been created in the demo system.",
            "Pending",
        ),
    )


def main():
    db = DatabaseManager()
    seed_faculty_class(db)
    seed_class_subject(db)
    seed_alerts(db)
    seed_audit_log(db)
    seed_notification_queue(db)
    print("Additional tables seeded successfully.")


if __name__ == "__main__":
    main()


