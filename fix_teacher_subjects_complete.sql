-- Complete fix for teacher-subject assignment issue
-- This script ensures all teachers have their subjects properly assigned

-- Step 1: Verify and fix Faculty table entries
-- Delete any incorrect entries first
DELETE FROM Faculty WHERE User_ID IN (3, 7, 16, 18, 19);

-- Insert correct Faculty entries
INSERT INTO Faculty (User_ID, Department, Faculty_Role) VALUES
(3, 'COE', 'Professor'),
(7, 'ECE', 'Associate Professor'),
(16, 'ME', 'Professor'),
(18, 'COE', 'Faculty'),
(19, 'COE', 'Faculty')
ON DUPLICATE KEY UPDATE 
    Department = VALUES(Department),
    Faculty_Role = VALUES(Faculty_Role);

-- Step 2: Verify Subject table has correct User_ID references
-- Check if subjects exist, if not, insert them
-- First, let's see what we have
SELECT 'Current Subjects:' as Info;
SELECT Subject_ID, Subject_Name, Subject_Code, User_ID FROM Subject ORDER BY User_ID;

-- Step 3: Ensure all subjects from the CSV/data are in the database
-- Delete existing subjects to avoid duplicates, then re-insert
DELETE FROM Subject WHERE Subject_ID IN (1001, 1002, 1003, 1005, 1007, 1008, 1009, 1010, 1011, 1013, 1014, 1016, 1018, 1020, 1022, 1024, 1026, 1027, 1028);

-- Insert all subjects with correct teacher assignments
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
(1028, 'Surveying', 'UCE310', 3, 132, 3, 3)
ON DUPLICATE KEY UPDATE
    Subject_Name = VALUES(Subject_Name),
    Subject_Code = VALUES(Subject_Code),
    User_ID = VALUES(User_ID),
    Class_ID = VALUES(Class_ID),
    Credits = VALUES(Credits),
    Semester = VALUES(Semester);

-- Step 4: Verify the assignments
SELECT 'Verification - Teachers with Subjects:' as Info;
SELECT 
    f.User_ID,
    u.Name as Teacher_Name,
    u.Email,
    f.Department,
    COUNT(s.Subject_ID) as Subject_Count,
    GROUP_CONCAT(s.Subject_Code ORDER BY s.Subject_Code SEPARATOR ', ') as Subjects
FROM Faculty f
LEFT JOIN User u ON f.User_ID = u.User_ID
LEFT JOIN Subject s ON f.User_ID = s.User_ID
GROUP BY f.User_ID, u.Name, u.Email, f.Department
ORDER BY f.User_ID;

-- Step 5: Show all subjects with their teachers
SELECT 'All Subjects with Teachers:' as Info;
SELECT 
    s.Subject_ID,
    s.Subject_Name,
    s.Subject_Code,
    s.User_ID as Teacher_User_ID,
    u.Name as Teacher_Name,
    s.Class_ID,
    s.Semester
FROM Subject s
LEFT JOIN User u ON s.User_ID = u.User_ID
ORDER BY s.User_ID, s.Subject_Name;

-- Step 6: Check for any orphaned subjects (subjects without valid teachers)
SELECT 'Orphaned Subjects (if any):' as Info;
SELECT 
    s.Subject_ID,
    s.Subject_Name,
    s.Subject_Code,
    s.User_ID
FROM Subject s
WHERE s.User_ID NOT IN (SELECT User_ID FROM Faculty)
   OR s.User_ID IS NULL;

