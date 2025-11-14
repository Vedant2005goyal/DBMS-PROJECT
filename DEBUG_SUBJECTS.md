# Debugging Subject Loading Issue

## Steps to Debug

### 1. Check Browser Console
Open browser developer tools (F12) and check the Console tab. You should see:
- "Loading subjects for teacher_id: X"
- "Subjects response: {...}"

### 2. Check API Response
Open Network tab in browser dev tools and look for the request to `/api/teacher/subjects`. Check:
- Status code (should be 200)
- Response body

### 3. Check Database

Run this SQL query to see what subjects exist for your teacher:

```sql
SELECT 
    s.Subject_ID,
    s.Subject_Name,
    s.Subject_Code,
    s.User_ID as Teacher_ID,
    u.Name as Teacher_Name,
    s.Is_Active
FROM Subject s
JOIN User u ON s.User_ID = u.User_ID
WHERE u.User_Role = 'Faculty'
ORDER BY s.User_ID, s.Subject_Name;
```

### 4. Verify Teacher ID

Check what User_ID your logged-in teacher has. The subjects in your CSV have:
- User_ID 3: Denzel Washington (subjects: 1001, 1005, 1007, 1010, 1028)
- User_ID 7: Kate Winslet (subjects: 1002, 1008, 1013, 1016, 1018, 1020)
- User_ID 16: Tom Hanks (subjects: 1003, 1009, 1011, 1014, 1022, 1024, 1026, 1027)

### 5. Fix Is_Active Column

If the Is_Active column doesn't exist or has NULL values, run:

```bash
docker-compose exec -T mysql mysql -u root -p${DB_PASSWORD} attendance_system < fix_subjects.sql
```

Or manually:

```sql
-- Add column if it doesn't exist
ALTER TABLE Subject ADD COLUMN Is_Active BOOLEAN DEFAULT TRUE;

-- Update all subjects to be active
UPDATE Subject SET Is_Active = TRUE WHERE Is_Active IS NULL;
```

### 6. Check API Logs

```bash
docker-compose logs api | grep -i subject
```

You should see: "Found X subjects for teacher_id Y"

## Common Issues

1. **Is_Active column doesn't exist**: The query will fail. Solution: Add the column or the code will now handle this.

2. **Teacher ID doesn't match**: If you login with a teacher that has no subjects assigned, dropdown will be empty. Solution: Use a teacher from the CSV (User_ID 3, 7, or 16).

3. **Subjects not in database**: If subjects from CSV weren't imported. Solution: Import the CSV data into Subject table.

