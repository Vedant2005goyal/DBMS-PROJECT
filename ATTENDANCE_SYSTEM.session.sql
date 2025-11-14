CREATE TABLE User ( --entity
    User_ID INT PRIMARY KEY AUTO_INCREMENT,
    Name VARCHAR(100) NOT NULL,
    Email VARCHAR(100) UNIQUE NOT NULL,    -- Used for login
    Password_Hash VARCHAR(255) NOT NULL, -- Use a hash, never store plain text
    Contact_No VARCHAR(10),              -- Common to both
    User_Role VARCHAR(10) NOT NULL       -- 'Student' or 'Faculty'
);
CREATE TABLE Class ( --entity
    Class_ID INT PRIMARY KEY,
    Class_Name VARCHAR(50) not null,
    Year int,
    Department varchar(30) not null
);
CREATE TABLE Students ( --entity
    User_ID INT PRIMARY KEY,       
    Roll_no VARCHAR(9) UNIQUE,
    Parent_Email VARCHAR(100),
    Class_ID INT,
    FOREIGN KEY (User_ID) REFERENCES User(User_ID), 
    FOREIGN KEY (Class_ID) REFERENCES Class(Class_ID)
);
CREATE TABLE Faculty ( --entity
    User_ID INT PRIMARY KEY,       -- This is the Primary Key
    Department VARCHAR(50),
    Faculty_Role VARCHAR(20) DEFAULT 'Faculty', -- e.g., 'Faculty', 'HOD'
    FOREIGN KEY (User_ID) REFERENCES User(User_ID)
);
CREATE TABLE Subject ( --entity
    Subject_ID INT PRIMARY KEY AUTO_INCREMENT,
    Subject_Name VARCHAR(100) NOT NULL,
    Subject_Code VARCHAR(20) UNIQUE,
    Credits INT DEFAULT 3,
    User_ID INT, -- This is the Faculty's User_ID
    Class_ID INT,
    Semester INT,
    FOREIGN KEY (User_ID) REFERENCES Faculty(User_ID),
    FOREIGN KEY (Class_ID) REFERENCES Class(Class_ID)
);
CREATE TABLE Alert ( --entity
    Alert_ID INT PRIMARY KEY AUTO_INCREMENT,
    Alert_Type VARCHAR(50),
    alert_priority VARCHAR(10) DEFAULT 'NORMAL', -- Can be 'HIGH' or 'LOW' also
    Created_By INT,
    Message TEXT,
    Date_Time DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (Created_By) REFERENCES User(User_ID)
);
CREATE TABLE Attendance (
    Attendance_ID INT PRIMARY KEY AUTO_INCREMENT,
    Session_ID INT NOT NULL, -- Link to specific session
    User_ID INT NOT NULL, -- Student's User_ID
    Subject_ID INT NOT NULL,
    Date DATE NOT NULL,
    Check_In_Time DATETIME, -- When they arrived
    Status VARCHAR(10) NOT NULL, -- 'Present', 'Absent', 'Late'
    Marked_By VARCHAR(20) DEFAULT 'Face Recognition', -- 'Face Recognition', 'Manual', 'Faculty'
    FOREIGN KEY (Session_ID) REFERENCES Attendance_Session(Session_ID),
    FOREIGN KEY (User_ID) REFERENCES Students(User_ID),
    FOREIGN KEY (Subject_ID) REFERENCES Subject(Subject_ID),
    UNIQUE KEY (User_ID, Session_ID) -- One attendance per student per session
);
CREATE TABLE User_Alert (
    User_ID INT,
    Alert_ID INT,
    PRIMARY KEY (User_ID, Alert_ID),
    FOREIGN KEY (User_ID) REFERENCES User(User_ID), -- Links to the main User table
    FOREIGN KEY (Alert_ID) REFERENCES Alert(Alert_ID)
);
CREATE TABLE Faculty_Class (
    User_ID INT, -- This is the Faculty's User_ID
    Class_ID INT,
    PRIMARY KEY (User_ID, Class_ID),
    FOREIGN KEY (User_ID) REFERENCES Faculty(User_ID),
    FOREIGN KEY (Class_ID) REFERENCES Class(Class_ID)
);
CREATE TABLE Class_Subject (
    Class_ID INT,
    Subject_ID INT,
    PRIMARY KEY (Class_ID, Subject_ID),
    FOREIGN KEY (Class_ID) REFERENCES Class(Class_ID),
    FOREIGN KEY (Subject_ID) REFERENCES Subject(Subject_ID)
);
CREATE TABLE Student_Subject (
    User_ID INT, 
    Subject_ID INT,
    PRIMARY KEY (User_ID, Subject_ID),
    FOREIGN KEY (User_ID) REFERENCES Students(User_ID),
    FOREIGN KEY (Subject_ID) REFERENCES Subject(Subject_ID)
);

Create table Face_Embeddings(
    Face_ID INT PRIMARY KEY AUTO_INCREMENT,
    User_ID INT NOT NULL,
<<<<<<< HEAD
    Face_Encoding TEXT NOT NULL, -- Stores the face encoding
    Photo_Path VARCHAR(255), -- Path to the stored photo
    Created_At TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (User_ID) REFERENCES Students(User_ID),
    INDEX idx_user (User_ID)
);
=======
    Face_Encoding TEXT NOT NULL, 
    Photo_Path VARCHAR(255),
    Created_At TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (User_ID) REFERENCES User(User_ID)
    ON DELETE CASCADE
    ON UPDATE CASCADE,
    INDEX idx_user (User_ID)
);

>>>>>>> 5a3d8ce (sql code for the database part of the project)
CREATE TABLE Attendance_Session (
    Session_ID INT PRIMARY KEY AUTO_INCREMENT,
    Subject_ID INT NOT NULL,
    Session_Date DATE NOT NULL,
    Start_Time TIME NOT NULL,
    End_Time TIME NOT NULL,
    Session_Type VARCHAR(20) DEFAULT 'Lecture', -- 'Lecture', 'Lab', 'Tutorial'
    Status VARCHAR(20) DEFAULT 'Scheduled', -- 'Scheduled', 'Ongoing', 'Completed'
    Created_By INT, -- Faculty who created the session
    FOREIGN KEY (Subject_ID) REFERENCES Subject(Subject_ID),
    FOREIGN KEY (Created_By) REFERENCES Faculty(User_ID),
    INDEX idx_subject_date (Subject_ID, Session_Date)
);
CREATE TABLE Attendance_Settings (
    Setting_ID INT PRIMARY KEY AUTO_INCREMENT,
    Setting_Key VARCHAR(50) UNIQUE NOT NULL,
    Setting_Value VARCHAR(100) NOT NULL,
    Description TEXT,
    Updated_At TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
);
-- Insert default values
INSERT INTO Attendance_Settings (Setting_Key, Setting_Value, Description) VALUES
('late_threshold_minutes', '10', 'Minutes after start time to mark as late'),
('min_attendance_percentage', '75', 'Minimum required attendance percentage'),
('auto_absent_after_minutes', '30', 'Mark absent if not present within X minutes');
CREATE TABLE Audit_Log (
    Log_ID INT PRIMARY KEY AUTO_INCREMENT,
    User_ID INT, -- Who made the change
    Action_Type VARCHAR(50) NOT NULL, -- 'INSERT', 'UPDATE', 'DELETE'
    Table_Name VARCHAR(50) NOT NULL,
    Record_ID INT,
    Old_Value TEXT,
    New_Value TEXT,
    Timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
    IP_Address VARCHAR(45),
    FOREIGN KEY (User_ID) REFERENCES User(User_ID),
    INDEX idx_user_time (User_ID, Timestamp)
);
-- it will queue the messages that is to be send to the user and hum ek alag se app bnayenge jo ki after some time iss table ke data ke according mail send karegi and it wont hamper the performance of our main app
CREATE TABLE Notification_Queue (
    Notification_ID INT PRIMARY KEY AUTO_INCREMENT,
    User_ID INT,
    Notification_Type VARCHAR(30), -- 'Email', 'SMS', 'Push'
    Recipient VARCHAR(100), -- Email or phone number
    Subject VARCHAR(200),
    Message TEXT,
    Status VARCHAR(20) DEFAULT 'Pending', -- 'Pending', 'Sent', 'Failed'
    Attempts INT DEFAULT 0,
    Created_At TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    Sent_At DATETIME,
    FOREIGN KEY (User_ID) REFERENCES User(User_ID),
    INDEX idx_status (Status)
);

<<<<<<< HEAD
=======
INSERT INTO User (User_ID, Name, Email, Password_Hash, Contact_No, User_Role) VALUES
(1, 'Angelina Jolie', 'ajolie@thapar.edu', 'passAJo1!@', '9876543210', 'Student'),
(2, 'Brad Pitt', 'bpitt@thapar.edu', 'passBPi2#$', '9876543211', 'Student'),
(3, 'Denzel Washington', 'dwashington@thapar.edu', 'passDWa3%^', '9876543212', 'Faculty'),
(4, 'Hugh Jackman', 'hjackman@thapar.edu', 'passHJa4&*', '9876543213', 'Student'),
(5, 'Jennifer Lawrence', 'jlawrence@thapar.edu', 'passJLa5()', '9876543214', 'Student'),
(6, 'Johnny Depp', 'jdepp@thapar.edu', 'passJDe6!#', '9876543215', 'Student'),
(7, 'Kate Winslet', 'kwinslet@thapar.edu', 'passKWi7@$', '9876543216', 'Faculty'),
(8, 'Leonardo DiCaprio', 'ldicaprio@thapar.edu', 'passLDi8%^', '9876543217', 'Student'),
(9, 'Megan Fox', 'mfox@thapar.edu', 'passMFo9&*', '9876543218', 'Student'),
(10, 'Natalie Portman', 'nportman@thapar.edu', 'passNPo1()', '9876543219', 'Student'),
(11, 'Nicole Kidman', 'nkidman@thapar.edu', 'passNKi2!@', '9876543220', 'Student'),
(12, 'Robert Downey Jr', 'rdowney@thapar.edu', 'passRDo3#$', '9876543221', 'Student'),
(13, 'Sandra Bullock', 'sbullock@thapar.edu', 'passSBu4%^', '9876543222', 'Student'),
(14, 'Scarlett Johansson', 'sjohansson@thapar.edu', 'passSJo5&*', '9876543223', 'Student'),
(15, 'Tom Cruise', 'tcruise@thapar.edu', 'passTCr6()', '9876543224', 'Student'),
(16, 'Tom Hanks', 'thanks@thapar.edu', 'passTHa7!#', '9876543225', 'Faculty'),
(17, 'Will Smith', 'wsmith@thapar.edu', 'passWSi8@$', '9876543226', 'Student'),
(18, 'Osho', 'rajneeshpuram@thapar.edu', 'jpafjTE@', '9876535871', 'Faculty'),
(19, 'Khalil Gibran', 'prophet@thapar.edu', 'passfjTE@', '9682535871', 'Faculty'),
(20, 'Aditya Gupta','aditya@thapar.edu','a7c2f1201','9352196565','Student'),
(21, 'Vedant Goyal', 'vgoyal@thapar.edu', 'uf422ets@', '8571027278', 'Student'),
(22, 'Rushil Upadhyay','rupadh@thapar.edu','Asdfgh@20','1234567890', 'Student'),
(23, 'Nikunj Garg', 'nikunj@thapar.edu','bhhb0611#','9644863454','Student'),
(24, 'Kusham Lata', 'kusham@thapar.edu','kl@7353er','8899248891','Student');


INSERT INTO Class (Class_ID, Class_Name, Year, Department) VALUES
(101, '1S01', 1, 'COE'),
(102, '1S02', 1, 'COE'),
(103, '2S01', 2, 'COE'),
(104, '2S02', 2, 'COE'),
(105, '3S01', 3, 'COE'),
(106, '3S02', 3, 'COE'),
(107, '4S01', 4, 'COE'),
(108, '4S02', 4, 'COE'),
(111, '1S03', 1, 'EEC'),
(112, '1S04', 1, 'EEC'),
(113, '2S03', 2, 'EEC'),
(114, '3S03', 3, 'EEE'),
(115, '4S03', 4, 'EEC'),
(121, '1S05', 1, 'ME'),
(122, '1S06', 1, 'ME'),
(123, '2S04', 2, 'ME'),
(124, '3S04', 3, 'ME'),
(125, '4S04', 4, 'ME'),
(131, '1S07', 1, 'CE'),
(132, '2S05', 2, 'CE'),
(133, '3S05', 3, 'CE'),
(134, '4S05', 4, 'CE'),
(141, '1S08', 1, 'CHE'),
(142, '2S06', 2, 'CHE'),
(151, '1S09', 1, 'BT');

INSERT INTO Subject (Subject_ID, Subject_Name, Subject_Code, User_ID, Class_ID, Credits, Semester) VALUES
(1001, 'Introduction to Programming', 'UCS101', 3, 101, 4, 1),
(1002, 'Basic Electrical Engineering', 'UES101', 7, 101, 3, 1),
(1003, 'Physics', 'UPH101', 16, 101, 3, 2),
(1005, 'Data Structures', 'UCS310', 3, 103, 4, 3),
(1007, 'Operating Systems', 'UCS410', 3, 103, 4, 4),
(1008, 'Computer Architecture', 'UCS411', 7, 103, 3, 4),
(1009, 'Database Management Systems', 'UCS510', 16, 105, 3, 5),
(1010, 'Software Engineering', 'UCS511', 3, 105, 3, 5),
(1011, 'Computer Networks', 'UCS610', 16, 105, 4, 6),
(1013, 'Machine Learning', 'UCS710', 7, 107, 3, 7),
(1014, 'Capstone', 'UCS799', 16, 107, 4, 7),
(1016, 'Basic Electronics', 'UEC101', 7, 111, 4, 1),
(1018, 'Analog Electronics', 'UEC310', 7, 113, 3, 3),
(1020, 'Communication Systems', 'UEC510', 7, 114, 3, 5),
(1022, 'Engineering Drawing', 'UME101', 16, 121, 2, 1),
(1024, 'Thermodynamics', 'UME310', 16, 123, 4, 3),
(1026, 'Fluid Mechanics', 'UME510', 16, 124, 3, 5),
(1027, 'Heat Transfer', 'UME610', 16, 124, 4, 6),
(1028, 'Surveying', 'UCE310', 3, 132, 3, 3);

INSERT INTO Faculty (User_ID, Designation, Department) VALUES
(3, 'Professor', 'COE'),
(7, 'Associate Professor', 'ECE'),
(16, 'Professor', 'ME');

INSERT INTO Students (User_ID, Roll_no, Parent_Email, Class_ID) VALUES
(1, '10230101', 'parent.jolie@gmail.com', 101), 
(2, '10230102', 'parent.pitt@gmail.com', 102),  
(4, '10230301', 'parent.jackman@gmail.com', 111), 
(5, '10230302', 'parent.lawrence@gmail.com', 112),
(6, '10230501', 'parent.depp@gmail.com', 121),    
(8, '10220101', 'parent.dicaprio@gmail.com', 103),  
(9, '10220102', 'parent.fox@gmail.com', 104),       
(10, '10220301', 'parent.portman@gmail.com', 113),  
(11, '10220501', 'parent.kidman@gmail.com', 123),  
(12, '10220701', 'parent.downey@gmail.com', 132),  
(13, '10210101', 'parent.bullock@gmail.com', 105), 
(14, '10210102', 'parent.johansson@gmail.com', 106),
(15, '10210301', 'parent.cruise@gmail.com', 114),   
(17, '10210501', 'parent.smith@gmail.com', 124),
(20, '10200101', 'parent.aditya@thapar.edu', 107),
(21, '10200102', 'parent.vedant@thapar.edu', 107),
(22, '10200103', 'parent.rushil@thapar.edu', 108),
(23, '10200104', 'parent.nikunj@thapar.edu', 108),
(24, '10200105', 'parent.kusham@thapar.edu', 108);

COMMIT;
SELECT * FROM User;
SELECT * FROM Face_Embeddings;
-- TRUNCATE TABLE Face_Embeddings;
SELECT * FROM Class;
SELECT * from Faculty;
SELECT * from Subject;
SELECT * from Attendance;
SELECT * from Students;
SELECT * FROM Attendance_Session;
TRUNCATE TABLE Attendance_Session;
SET FOREIGN_KEY_CHECKS = 0;
TRUNCATE TABLE Attendance_Session;
TRUNCATE TABLE Attendance;
SET FOREIGN_KEY_CHECKS = 1;

ALTER TABLE Attendance_Session 
ADD CONSTRAINT unique_session 
UNIQUE (Subject_ID, Session_Date, Start_Time);

SELECT * FROM Attendance_Settings;
>>>>>>> 5a3d8ce (sql code for the database part of the project)
