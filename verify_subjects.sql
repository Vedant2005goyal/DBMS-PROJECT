-- Quick verification script to check subjects for teachers
-- Run this to see what subjects are assigned to which teachers

-- Check all subjects with their assigned teachers
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

-- Check subjects for specific teacher (replace 3 with your teacher's User_ID)
SELECT 
    Subject_ID,
    Subject_Name,
    Subject_Code,
    Class_ID,
    Semester
FROM Subject
WHERE User_ID = 3
ORDER BY Subject_Name;

-- Verify Faculty table entries
SELECT 
    f.User_ID,
    u.Name,
    u.Email,
    f.Department,
    f.Faculty_Role
FROM Faculty f
LEFT JOIN User u ON f.User_ID = u.User_ID
ORDER BY f.User_ID;

