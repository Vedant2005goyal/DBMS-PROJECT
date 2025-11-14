-- Fix Faculty table and verify Subject assignments
-- This script fixes the Faculty table structure and verifies subject assignments

-- First, check current state
SELECT 'Current Faculty entries:' as Info;
SELECT * FROM Faculty;

SELECT 'Current Subjects with their assigned teachers:' as Info;
SELECT Subject_ID, Subject_Name, Subject_Code, User_ID, Class_ID 
FROM Subject 
ORDER BY User_ID, Subject_Name;

-- Fix Faculty table if it has wrong structure
-- Delete existing entries if they were inserted incorrectly
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

-- Verify Faculty entries
SELECT 'Updated Faculty entries:' as Info;
SELECT * FROM Faculty;

-- Check which teachers have subjects assigned
SELECT 'Teachers with subjects assigned:' as Info;
SELECT 
    f.User_ID,
    u.Name as Teacher_Name,
    u.Email,
    f.Department,
    f.Faculty_Role,
    COUNT(s.Subject_ID) as Subject_Count
FROM Faculty f
LEFT JOIN User u ON f.User_ID = u.User_ID
LEFT JOIN Subject s ON f.User_ID = s.User_ID
GROUP BY f.User_ID, u.Name, u.Email, f.Department, f.Faculty_Role
ORDER BY f.User_ID;

-- Show all subjects with their teacher info
SELECT 'All subjects with teacher details:' as Info;
SELECT 
    s.Subject_ID,
    s.Subject_Name,
    s.Subject_Code,
    s.User_ID as Teacher_User_ID,
    u.Name as Teacher_Name,
    u.Email as Teacher_Email,
    s.Class_ID,
    s.Semester
FROM Subject s
LEFT JOIN User u ON s.User_ID = u.User_ID
ORDER BY s.User_ID, s.Subject_Name;

-- Check for subjects with NULL or invalid User_ID
SELECT 'Subjects with NULL or invalid User_ID:' as Info;
SELECT 
    Subject_ID,
    Subject_Name,
    Subject_Code,
    User_ID,
    Class_ID
FROM Subject
WHERE User_ID IS NULL 
   OR User_ID NOT IN (SELECT User_ID FROM Faculty);

