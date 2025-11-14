-- Fix missing students in Students table
-- These students exist in User table with User_Role='Student' but are missing from Students table

INSERT INTO Students (User_ID, Roll_no, Parent_Email, Class_ID) VALUES
(15, '10230115', 'parent.cruise@gmail.com', 101),  -- Tom Cruise
(17, '10230117', 'parent.smith@gmail.com', 101),  -- Will Smith
(20, '10230220', 'parent.aditya@gmail.com', 101), -- Aditya Gupta
(21, '10230221', 'parent.vedant@gmail.com', 101), -- Vedant Goyal
(22, '10230222', 'parent.rushil@gmail.com', 101), -- Rushil Upadhyay
(23, '10230223', 'parent.nikunj@gmail.com', 101), -- Nikunj Garg
(24, '10230224', 'parent.kusham@gmail.com', 101)  -- Kusham Lata
ON DUPLICATE KEY UPDATE
    Roll_no = VALUES(Roll_no),
    Parent_Email = VALUES(Parent_Email),
    Class_ID = VALUES(Class_ID);

