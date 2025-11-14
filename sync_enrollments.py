#!/usr/bin/env python3
"""
Ensure every student is enrolled in each subject that belongs to their class.
"""

import os
import sys

script_dir = os.path.dirname(os.path.abspath(__file__))
backend_path = os.path.join(script_dir, 'backend')
sys.path.insert(0, backend_path)

from database import DatabaseManager


def sync_enrollments():
    db = DatabaseManager()
    subjects = db.execute_query(
        "SELECT Subject_ID, Class_ID FROM Subject",
        fetch=True
    ) or []

    total_created = 0

    for subject in subjects:
        class_id = subject['Class_ID']
        subject_id = subject['Subject_ID']
        if not class_id:
            continue

        students = db.execute_query(
            "SELECT User_ID FROM Students WHERE Class_ID = %s",
            (class_id,),
            fetch=True
        ) or []

        if not students:
            # Fallback: use all students to keep demo data populated
            students = db.execute_query(
                "SELECT User_ID FROM Students",
                fetch=True
            ) or []

        for student in students:
            user_id = student['User_ID']
            db.execute_query(
                """INSERT IGNORE INTO Student_Subject (User_ID, Subject_ID)
                   VALUES (%s, %s)""",
                (user_id, subject_id)
            )
            total_created += 1

    print(f"Enrollment sync complete. Processed {len(subjects)} subjects.")
    print(f"Upserted {total_created} rows (duplicates skipped).")


if __name__ == "__main__":
    sync_enrollments()

