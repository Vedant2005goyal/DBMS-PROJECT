-- Attendance Management System Database Schema
-- This file is used to initialize the MySQL database in Docker

CREATE TABLE IF NOT EXISTS User (
    User_ID INT PRIMARY KEY AUTO_INCREMENT,
    Name VARCHAR(100) NOT NULL,
    Email VARCHAR(100) UNIQUE NOT NULL,
    Password_Hash VARCHAR(255) NOT NULL,
    Contact_No VARCHAR(10),
    User_Role VARCHAR(10) NOT NULL
);

CREATE TABLE IF NOT EXISTS Class (
    Class_ID INT PRIMARY KEY,
    Class_Name VARCHAR(50) NOT NULL,
    Year INT,
    Department VARCHAR(30) NOT NULL
);

CREATE TABLE IF NOT EXISTS Students (
    User_ID INT PRIMARY KEY,
    Roll_no VARCHAR(9) UNIQUE,
    Parent_Email VARCHAR(100),
    Class_ID INT,
    FOREIGN KEY (User_ID) REFERENCES User(User_ID),
    FOREIGN KEY (Class_ID) REFERENCES Class(Class_ID)
);

CREATE TABLE IF NOT EXISTS Faculty (
    User_ID INT PRIMARY KEY,
    Department VARCHAR(50),
    Faculty_Role VARCHAR(20) DEFAULT 'Faculty',
    FOREIGN KEY (User_ID) REFERENCES User(User_ID)
);

CREATE TABLE IF NOT EXISTS Subject (
    Subject_ID INT PRIMARY KEY AUTO_INCREMENT,
    Subject_Name VARCHAR(100) NOT NULL,
    Subject_Code VARCHAR(20) UNIQUE,
    Credits INT DEFAULT 3,
    User_ID INT,
    Class_ID INT,
    Semester INT,
    Is_Active BOOLEAN DEFAULT TRUE,
    FOREIGN KEY (User_ID) REFERENCES Faculty(User_ID),
    FOREIGN KEY (Class_ID) REFERENCES Class(Class_ID)
);

CREATE TABLE IF NOT EXISTS Alert (
    Alert_ID INT PRIMARY KEY AUTO_INCREMENT,
    Alert_Type VARCHAR(50),
    alert_priority VARCHAR(10) DEFAULT 'NORMAL',
    Created_By INT,
    Message TEXT,
    Date_Time DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (Created_By) REFERENCES User(User_ID)
);

CREATE TABLE IF NOT EXISTS Attendance_Session (
    Session_ID INT PRIMARY KEY AUTO_INCREMENT,
    Subject_ID INT NOT NULL,
    Session_Date DATE NOT NULL,
    Start_Time TIME NOT NULL,
    End_Time TIME NOT NULL,
    Session_Type VARCHAR(20) DEFAULT 'Lecture',
    Status VARCHAR(20) DEFAULT 'Scheduled',
    Created_By INT,
    FOREIGN KEY (Subject_ID) REFERENCES Subject(Subject_ID),
    FOREIGN KEY (Created_By) REFERENCES Faculty(User_ID),
    INDEX idx_subject_date (Subject_ID, Session_Date),
    UNIQUE KEY unique_session (Subject_ID, Session_Date, Start_Time)
);

CREATE TABLE IF NOT EXISTS Attendance (
    Attendance_ID INT PRIMARY KEY AUTO_INCREMENT,
    Session_ID INT NOT NULL,
    User_ID INT NOT NULL,
    Subject_ID INT NOT NULL,
    Date DATE NOT NULL,
    Check_In_Time DATETIME,
    Status VARCHAR(10) NOT NULL,
    Marked_By VARCHAR(20) DEFAULT 'Face Recognition',
    FOREIGN KEY (Session_ID) REFERENCES Attendance_Session(Session_ID),
    FOREIGN KEY (User_ID) REFERENCES Students(User_ID),
    FOREIGN KEY (Subject_ID) REFERENCES Subject(Subject_ID),
    UNIQUE KEY (User_ID, Session_ID)
);

CREATE TABLE IF NOT EXISTS User_Alert (
    User_ID INT,
    Alert_ID INT,
    PRIMARY KEY (User_ID, Alert_ID),
    FOREIGN KEY (User_ID) REFERENCES User(User_ID),
    FOREIGN KEY (Alert_ID) REFERENCES Alert(Alert_ID)
);

CREATE TABLE IF NOT EXISTS Faculty_Class (
    User_ID INT,
    Class_ID INT,
    PRIMARY KEY (User_ID, Class_ID),
    FOREIGN KEY (User_ID) REFERENCES Faculty(User_ID),
    FOREIGN KEY (Class_ID) REFERENCES Class(Class_ID)
);

CREATE TABLE IF NOT EXISTS Class_Subject (
    Class_ID INT,
    Subject_ID INT,
    PRIMARY KEY (Class_ID, Subject_ID),
    FOREIGN KEY (Class_ID) REFERENCES Class(Class_ID),
    FOREIGN KEY (Subject_ID) REFERENCES Subject(Subject_ID)
);

CREATE TABLE IF NOT EXISTS Student_Subject (
    User_ID INT,
    Subject_ID INT,
    PRIMARY KEY (User_ID, Subject_ID),
    FOREIGN KEY (User_ID) REFERENCES Students(User_ID),
    FOREIGN KEY (Subject_ID) REFERENCES Subject(Subject_ID)
);

CREATE TABLE IF NOT EXISTS Face_Embeddings (
    Face_ID INT PRIMARY KEY AUTO_INCREMENT,
    User_ID INT NOT NULL,
    Face_Encoding TEXT NOT NULL,
    Photo_Path VARCHAR(255),
    Created_At TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (User_ID) REFERENCES User(User_ID) ON DELETE CASCADE ON UPDATE CASCADE,
    INDEX idx_user (User_ID)
);

CREATE TABLE IF NOT EXISTS Attendance_Settings (
    Setting_ID INT PRIMARY KEY AUTO_INCREMENT,
    Setting_Key VARCHAR(50) UNIQUE NOT NULL,
    Setting_Value VARCHAR(100) NOT NULL,
    Description TEXT,
    Updated_At TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS Audit_Log (
    Log_ID INT PRIMARY KEY AUTO_INCREMENT,
    User_ID INT,
    Action_Type VARCHAR(50) NOT NULL,
    Table_Name VARCHAR(50) NOT NULL,
    Record_ID INT,
    Old_Value TEXT,
    New_Value TEXT,
    Timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
    IP_Address VARCHAR(45),
    FOREIGN KEY (User_ID) REFERENCES User(User_ID),
    INDEX idx_user_time (User_ID, Timestamp)
);

CREATE TABLE IF NOT EXISTS Notification_Queue (
    Notification_ID INT PRIMARY KEY AUTO_INCREMENT,
    User_ID INT,
    Notification_Type VARCHAR(30),
    Recipient VARCHAR(100),
    Subject VARCHAR(200),
    Message TEXT,
    Status VARCHAR(20) DEFAULT 'Pending',
    Attempts INT DEFAULT 0,
    Created_At TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    Sent_At DATETIME,
    FOREIGN KEY (User_ID) REFERENCES User(User_ID),
    INDEX idx_status (Status)
);

-- Insert default settings
INSERT INTO Attendance_Settings (Setting_Key, Setting_Value, Description) VALUES
('late_threshold_minutes', '10', 'Minutes after start time to mark as late'),
('min_attendance_percentage', '75', 'Minimum required attendance percentage'),
('auto_absent_after_minutes', '30', 'Mark absent if not present within X minutes')
ON DUPLICATE KEY UPDATE Setting_Value = VALUES(Setting_Value);

