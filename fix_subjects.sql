-- Script to fix Subject table and ensure Is_Active column exists
-- Run this in your MySQL database

-- Check if Is_Active column exists, if not add it
SET @col_exists = (
    SELECT COUNT(*) 
    FROM INFORMATION_SCHEMA.COLUMNS 
    WHERE TABLE_SCHEMA = 'attendance_system' 
    AND TABLE_NAME = 'Subject' 
    AND COLUMN_NAME = 'Is_Active'
);

SET @sql = IF(@col_exists = 0,
    'ALTER TABLE Subject ADD COLUMN Is_Active BOOLEAN DEFAULT TRUE',
    'SELECT "Is_Active column already exists" AS message'
);

PREPARE stmt FROM @sql;
EXECUTE stmt;
DEALLOCATE PREPARE stmt;

-- Update all existing subjects to be active
UPDATE Subject SET Is_Active = TRUE WHERE Is_Active IS NULL OR Is_Active = FALSE;

-- Verify subjects for each teacher
SELECT 
    u.User_ID,
    u.Name as Teacher_Name,
    u.Email,
    COUNT(s.Subject_ID) as Subject_Count,
    GROUP_CONCAT(s.Subject_Name SEPARATOR ', ') as Subjects
FROM User u
LEFT JOIN Subject s ON u.User_ID = s.User_ID
WHERE u.User_Role = 'Faculty'
GROUP BY u.User_ID, u.Name, u.Email;

