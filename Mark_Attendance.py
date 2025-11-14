#!/usr/bin/env python
# coding: utf-8

# In[1]:


import face_recognition
import cv2 as cv
import matplotlib.pyplot as ptl
import os 
import mysql.connector
import numpy as np
import pickle
import json
from datetime import datetime,date,time,timedelta


# In[2]:


class MarkAttendance:
    def __init__(self):
        try:
            self.mysql_connection=mysql.connector.connect(
                host="localhost",
                user="root",
                password="goyalvedant2005",
                database="attendance_system"
            )
            self.cursor=self.mysql_connection.cursor(dictionary=True)
            print('Database connected succesfully!!')
        except mysql.connector.Error as err:
            print(f"Database connection failed: {err}")
            raise

        self.known_face_encodings = []
        self.known_face_ids = []
        self.known_face_names = []
        self.load_known_faces()

    def load_known_faces(self):
        query="SELECT f.User_ID, u.Name, f.Face_Encoding FROM Face_Embeddings f JOIN User u ON f.User_ID = u.User_ID"
        self.cursor.execute(query)
        results=self.cursor.fetchall()
        for row in results:
            User_ID = row['User_ID'] # type: ignore 
            Name = row['Name']
            Encoding_json = row['Face_Encoding']

            # Convert hex string back to numpy array
            encoding_list = json.loads(Encoding_json)
            encoding = np.array(encoding_list)

            self.known_face_encodings.append(encoding)
            self.known_face_ids.append(User_ID)
            self.known_face_names.append(Name)
        print(f"Loaded {len(self.known_face_encodings)} registered faces")

    def get_buffer_time(self):
        try:
            query = """SELECT Setting_Value FROM Attendance_Settings WHERE Setting_Key = 'session_buffer_minutes'"""
            self.cursor.execute(query)
            setting = self.cursor.fetchone()

            if setting:
                buffer_minutes = int(setting['Setting_Value'])
            else:
                # If not in settings, insert default and use it
                insert_query = """
                    INSERT INTO Attendance_Settings (Setting_Key, Setting_Value, Description)
                    VALUES ('session_buffer_minutes', '5', 
                            'Buffer time before/after session for attendance marking')
                """
                self.cursor.execute(insert_query)
                self.mysql_connection.commit()
                buffer_minutes = 5

            print(f"📋 Session buffer time: {buffer_minutes} minutes")
            return buffer_minutes
        except mysql.connector.Error as err:
            print(f"⚠ Could not fetch buffer time, using default 5 minutes: {err}")
            return 5

    def mark_attendance(self,User_ID,Name,Session_ID,Subject_ID):
        today=date.today()
        current_time=datetime.now()
        check_query = "SELECT * FROM Attendance WHERE User_ID = %s AND Session_ID = %s"
        self.cursor.execute(check_query, (User_ID, Session_ID))
        existing = self.cursor.fetchone()

        if existing:
            print(f"{Name} already marked present for this session")
            return False

        session_query = "SELECT Start_Time, Session_Date FROM Attendance_Session WHERE Session_ID = %s"
        self.cursor.execute(session_query,(Session_ID,))
        session = self.cursor.fetchone()

        if not session:
            print(f'{Session_ID} not found!!')
            return False

        settings_query = "SELECT Setting_Value FROM Attendance_Settings WHERE Setting_Key = 'late_threshold_minutes'"
        self.cursor.execute(settings_query)
        setting = self.cursor.fetchone()
        late_threshold = int(setting['Setting_Value']) if setting else 15
        print(f'late_threshold is {late_threshold}')
        session_start = session['Start_Time']
        if isinstance(session_start, timedelta):
            # Convert timedelta to time
            total_seconds = int(session_start.total_seconds())
            hours = total_seconds // 3600
            minutes = (total_seconds % 3600) // 60
            seconds = total_seconds % 60
            session_start = time(hours, minutes, seconds)
        current_time_only = current_time.time()
        status = 'Present'

        session_start_dt = datetime.combine(today, session_start)
        current_dt = datetime.combine(today, current_time_only)
        time_diff = (current_dt - session_start_dt).total_seconds() / 60
        if time_diff>late_threshold:
            status = 'Late'
            print(f"{time_diff:.1f} minutes after start")
        else:
            print(f"On time ({time_diff:.1f} minutes)")

        insert_query = """INSERT INTO Attendance (Session_ID, User_ID, Subject_ID, Date, Check_In_Time, Status, Marked_By) VALUES (%s, %s, %s, %s, %s, %s, %s)"""
        try:
            self.cursor.execute(insert_query, (
                Session_ID,
                User_ID,
                Subject_ID,
                today,
                current_time,
                status,
                'Face Recognition'  # Marked_By field
            ))
            self.mysql_connection.commit()

            print(f"✓ Attendance marked for {User_ID}: {Name}")
            print(f"  Session ID: {Session_ID}")
            print(f"  Status: {status}")
            print(f"  Time: {current_time.strftime('%H:%M:%S')}")
            return True

        except mysql.connector.Error as err:
            print(f"✗ Error marking attendance: {err}")
            self.mysql_connection.rollback()
            return False

    # for faculty to create the session
    def create_attendance_session(self,Subject_ID,Session_Date,Start_Time,End_Time,Session_Type,Status,Created_By):
        insert_query = """INSERT INTO Attendance_Session (Subject_ID,Session_Date,Start_Time,End_Time,Session_Type,Status,Created_By) VALUES (%s, %s, %s, %s, %s, %s, %s)""" 
        try:
            self.cursor.execute(insert_query,(
                Subject_ID,
                Session_Date,
                Start_Time,
                End_Time,
                Session_Type,
                'Scheduled',
                Created_By
            ))
            self.mysql_connection.commit()
            session_id = self.cursor.lastrowid  
            print(f"✓ Session created for {Subject_ID} by {Created_By}")
            return session_id
        except mysql.connector.Error as err:
            print(f'✗ Error in making the session')
            self.mysql_connection.rollback()
            return False

    # Faculty will prior create the session and at the time of lecture they will activate it for attendace purposes
    def get_active_session(self, Subject_ID=None, use_buffer=True):
        today = date.today()
        if Subject_ID:
            query = """
                SELECT Session_ID, Subject_ID, Session_Date, Start_Time, End_Time, Session_Type
                FROM Attendance_Session
                WHERE Subject_ID = %s 
                AND Session_Date = %s
                AND Status IN ('Scheduled', 'Ongoing')
                ORDER BY Start_Time ASC
                LIMIT 1
            """
            self.cursor.execute(query, (Subject_ID, today))
        else:
            query = """
                SELECT Session_ID, Subject_ID, Session_Date, Start_Time, End_Time, Session_Type
                FROM Attendance_Session
                WHERE Session_Date = %s
                AND Status IN ('Scheduled', 'Ongoing')
                ORDER BY Start_Time ASC
            """
            self.cursor.execute(query, (today,))
        sessions = self.cursor.fetchall()

        if sessions:
            print(f"✓ Found {len(sessions)} active session(s)")
            for session in sessions:
                print(f"  Session_ID: {session['Session_ID']}, Subject_ID: {session['Subject_ID']}")
        else:
            print("⚠ No active sessions found at this time")

        return sessions

    def recognize_user(self,Subject_ID,Session_ID=None,use_buffer=True):
        sessions = self.get_active_session(Subject_ID)
        if not sessions:
            print(f'No session with ID:{Subject_ID} exists please create it first')
            return 
        session = sessions[0]  # Use the first active session
        session_id = session['Session_ID']

        print(f"\n{'*'*60}")
        print(f"ATTENDANCE SYSTEM - Session ID: {session_id}")
        print(f"Subject ID: {Subject_ID}")
        print(f"Session Type: {session['Session_Type']}")
        print(f"Time: {session['Start_Time']} - {session['End_Time']}")
        print(f"{'*'*60}")

        video_capture=cv.VideoCapture(0)
        print('Invoked Camera. Press Q/q to quit()')
        # for marking the session as ongoing
        self.cursor.execute("UPDATE Attendance_Session SET Status = 'Ongoing' WHERE Session_ID = %s",(session_id,))
        self.mysql_connection.commit()
        marked_students = set()

        while True:
            ret, frame = video_capture.read()
            if not ret:
                break
            # Resize frame for faster processing
            small_frame = cv.resize(frame, (0, 0), fx=0.25, fy=0.25)
            rgb_small_frame = cv.cvtColor(small_frame, cv.COLOR_BGR2RGB)

            # Find faces in current frame
            face_locations = face_recognition.face_locations(rgb_small_frame)
            face_encodings = face_recognition.face_encodings(rgb_small_frame, face_locations)

            for face_encoding, face_location in zip(face_encodings, face_locations):
                # Compare with known faces
                matches = face_recognition.compare_faces(
                    self.known_face_encodings, face_encoding, tolerance=0.55
                )
                name = "Unknown"
                User_ID = None
                color=(0,0,255)

                # Find best match
                if len(self.known_face_encodings) > 0:
                    face_distances = face_recognition.face_distance(self.known_face_encodings, face_encoding)
                    best_match_index = np.argmin(face_distances)
                    if matches[best_match_index] and face_distances[best_match_index] < 0.55:
                        name = self.known_face_names[best_match_index]
                        User_ID = self.known_face_ids[best_match_index]
                        color=(0,255,0)

                        if User_ID not in marked_students:
                            if self.mark_attendance(User_ID, name, session_id, Subject_ID):
                                marked_students.add(User_ID)
                                cv.putText(frame, "ATTENDANCE MARKED!",(50, 100), cv.FONT_HERSHEY_SIMPLEX, 1.5, (0, 255, 0), 3)
                                cv.imshow('Attendance System', frame)
                        else:
                            color = (255, 165, 0)  # Orange for already marked
                            label = f"{name} - MARKED ✓"
                # Draw rectangle and name
                top, right, bottom, left = face_location
                top *= 4
                right *= 4
                bottom *= 4
                left *= 4

                cv.rectangle(frame, (left, top), (right, bottom), color, 2)
                cv.rectangle(frame, (left, bottom - 35), (right, bottom), color, cv.FILLED)
                cv.putText(frame, name, (left + 6, bottom - 6), cv.FONT_HERSHEY_DUPLEX, 0.6, (255, 255, 255), 1)

            cv.putText(frame, f"Session: {session_id} | Marked: {len(marked_students)}", 
                      (10, 30), cv.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
            cv.putText(frame, "Press 'q' to quit", 
                      (10, frame.shape[0] - 20), cv.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2)
            # Display
            cv.imshow('Attendance System', frame)

            if cv.waitKey(1) & 0xFF == ord('q'):
                break

        self.mysql_connection.commit()
        video_capture.release()
        cv.destroyAllWindows()
    def close(self):
        self.cursor.close()
        self.mysql_connection.close()


# In[23]:


if __name__ == '__main__':
    system = MarkAttendance()

    # Create session and get the session_id
    session_id = system.create_attendance_session(
        Subject_ID=1009,
        Session_Date=date.today(),
        Start_Time=time(15, 40, 0),
        End_Time=time(16, 50, 0),
        Status='Scheduled',
        Session_Type='Lecture',
        Created_By=3  # Faculty's User_ID
    )

    system.recognize_user(Subject_ID=1009, use_buffer=True)

    system.close()


# In[ ]:




