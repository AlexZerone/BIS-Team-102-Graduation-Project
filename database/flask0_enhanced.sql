-- Enhanced SQL Schema for Sec Era Platform
-- Includes admin functionality, subscriptions, approvals, and best practices
-- Version: 2.0.0

SET SQL_MODE = "NO_AUTO_VALUE_ON_ZERO";
START TRANSACTION;
SET time_zone = "+00:00";

-- Users Table (Enhanced with admin support)
CREATE TABLE `users` (
  `UserID` int(11) NOT NULL AUTO_INCREMENT,
  `First` varchar(64) NOT NULL,
  `Last` varchar(64) NOT NULL,
  `Email` varchar(255) NOT NULL UNIQUE,
  `Password` varchar(255) NOT NULL,
  `UserType` enum('student','instructor','company','admin') NOT NULL,
  `ProfilePicture` varchar(255) DEFAULT NULL,
  `CreatedAt` timestamp NOT NULL DEFAULT current_timestamp(),
  `UpdatedAt` timestamp NOT NULL DEFAULT current_timestamp() ON UPDATE current_timestamp(),
  `Status` enum('Active','Inactive','Pending','Suspended') NOT NULL DEFAULT 'Active',
  `ApprovalStatus` enum('Approved','Pending','Rejected') DEFAULT 'Approved',
  `ApprovedBy` int(11) DEFAULT NULL,
  `ApprovedAt` timestamp NULL DEFAULT NULL,
  PRIMARY KEY (`UserID`),
  KEY `ApprovedBy` (`ApprovedBy`),
  INDEX `idx_email` (`Email`),
  INDEX `idx_user_type` (`UserType`),
  INDEX `idx_status` (`Status`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

-- Students Table
CREATE TABLE `students` (
  `StudentID` int(11) NOT NULL AUTO_INCREMENT,
  `UserID` int(11) NOT NULL,
  `University` varchar(128) DEFAULT NULL,
  `Major` varchar(64) DEFAULT NULL,
  `GPA` float DEFAULT NULL,
  `ExpectedGraduationDate` date DEFAULT NULL,
  `ResumeFile` varchar(255) DEFAULT NULL,
  `Bio` text DEFAULT NULL,
  `SubscriptionTier` enum('freemium','basic','standard','premium','premium_annual') DEFAULT 'freemium',
  `SubscriptionStatus` enum('active','inactive','cancelled','expired') DEFAULT 'active',
  `SubscriptionStart` date DEFAULT NULL,
  `SubscriptionEnd` date DEFAULT NULL,
  `CreatedAt` timestamp NOT NULL DEFAULT current_timestamp(),
  `UpdatedAt` timestamp NOT NULL DEFAULT current_timestamp() ON UPDATE current_timestamp(),
  PRIMARY KEY (`StudentID`),
  KEY `UserID` (`UserID`),
  INDEX `idx_subscription` (`SubscriptionTier`, `SubscriptionStatus`),
  CONSTRAINT `students_ibfk_1` FOREIGN KEY (`UserID`) REFERENCES `users` (`UserID`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

-- Instructors Table (Enhanced with approval system)
CREATE TABLE `instructors` (
  `InstructorID` int(11) NOT NULL AUTO_INCREMENT,
  `UserID` int(11) NOT NULL,
  `Department` varchar(128) DEFAULT NULL,
  `Specialization` varchar(128) DEFAULT NULL,
  `Experience` int(11) DEFAULT NULL,
  `Bio` text DEFAULT NULL,
  `Qualifications` text DEFAULT NULL,
  `ApprovalStatus` enum('Approved','Pending','Rejected') DEFAULT 'Pending',
  `ApprovedBy` int(11) DEFAULT NULL,
  `ApprovedAt` timestamp NULL DEFAULT NULL,
  `RejectionReason` text DEFAULT NULL,
  `CreatedAt` timestamp NOT NULL DEFAULT current_timestamp(),
  `UpdatedAt` timestamp NOT NULL DEFAULT current_timestamp() ON UPDATE current_timestamp(),
  PRIMARY KEY (`InstructorID`),
  KEY `UserID` (`UserID`),
  KEY `ApprovedBy` (`ApprovedBy`),
  INDEX `idx_approval_status` (`ApprovalStatus`),
  CONSTRAINT `instructors_ibfk_1` FOREIGN KEY (`UserID`) REFERENCES `users` (`UserID`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

-- Companies Table (Enhanced with approval system)
CREATE TABLE `companies` (
  `CompanyID` int(11) NOT NULL AUTO_INCREMENT,
  `UserID` int(11) NOT NULL,
  `Name` varchar(128) NOT NULL,
  `Industry` varchar(128) DEFAULT NULL,
  `Location` varchar(128) DEFAULT NULL,
  `CompanySize` int(11) DEFAULT NULL,
  `FoundedDate` date DEFAULT NULL,
  `Bio` text DEFAULT NULL,
  `Website` varchar(255) DEFAULT NULL,
  `VerificationDocument` varchar(255) DEFAULT NULL,
  `ApprovalStatus` enum('Approved','Pending','Rejected') DEFAULT 'Pending',
  `ApprovedBy` int(11) DEFAULT NULL,
  `ApprovedAt` timestamp NULL DEFAULT NULL,
  `RejectionReason` text DEFAULT NULL,
  `CreatedAt` timestamp NOT NULL DEFAULT current_timestamp(),
  `UpdatedAt` timestamp NOT NULL DEFAULT current_timestamp() ON UPDATE current_timestamp(),
  PRIMARY KEY (`CompanyID`),
  KEY `UserID` (`UserID`),
  KEY `ApprovedBy` (`ApprovedBy`),
  INDEX `idx_approval_status` (`ApprovalStatus`),
  CONSTRAINT `companies_ibfk_1` FOREIGN KEY (`UserID`) REFERENCES `users` (`UserID`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

-- Subscription Plans Table
CREATE TABLE `subscription_plans` (
  `PlanID` int(11) NOT NULL AUTO_INCREMENT,
  `Name` varchar(50) NOT NULL,
  `Description` text DEFAULT NULL,
  `Price` decimal(10,2) NOT NULL,
  `BillingCycle` enum('monthly','annual') NOT NULL,
  `Features` JSON DEFAULT NULL,
  `IsActive` tinyint(1) DEFAULT 1,
  `CreatedAt` timestamp NOT NULL DEFAULT current_timestamp(),
  `UpdatedAt` timestamp NOT NULL DEFAULT current_timestamp() ON UPDATE current_timestamp(),
  PRIMARY KEY (`PlanID`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

-- Subscription Payments Table
CREATE TABLE `subscription_payments` (
  `PaymentID` int(11) NOT NULL AUTO_INCREMENT,
  `StudentID` int(11) NOT NULL,
  `PlanID` int(11) NOT NULL,
  `Amount` decimal(10,2) NOT NULL,
  `PaymentDate` timestamp NOT NULL DEFAULT current_timestamp(),
  `PaymentMethod` varchar(50) DEFAULT NULL,
  `TransactionID` varchar(100) DEFAULT NULL,
  `Status` enum('pending','completed','failed','refunded') DEFAULT 'pending',
  `IsInstallment` tinyint(1) DEFAULT 0,
  `InstallmentNumber` int(11) DEFAULT NULL,
  `TotalInstallments` int(11) DEFAULT NULL,
  PRIMARY KEY (`PaymentID`),
  KEY `StudentID` (`StudentID`),
  KEY `PlanID` (`PlanID`),
  CONSTRAINT `subscription_payments_ibfk_1` FOREIGN KEY (`StudentID`) REFERENCES `students` (`StudentID`) ON DELETE CASCADE,
  CONSTRAINT `subscription_payments_ibfk_2` FOREIGN KEY (`PlanID`) REFERENCES `subscription_plans` (`PlanID`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

-- Company Sizes Lookup
CREATE TABLE `company_sizes` (
  `SizeID` int(11) NOT NULL AUTO_INCREMENT,
  `SizeLabel` varchar(50) NOT NULL UNIQUE,
  PRIMARY KEY (`SizeID`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

-- Course Types Lookup
CREATE TABLE `course_types` (
  `TypeID` int(11) NOT NULL AUTO_INCREMENT,
  `TypeLabel` varchar(50) NOT NULL UNIQUE,
  PRIMARY KEY (`TypeID`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

-- Courses Table (Enhanced with approval system)
CREATE TABLE `courses` (
  `CourseID` int(11) NOT NULL AUTO_INCREMENT,
  `Title` varchar(100) NOT NULL,
  `Description` text DEFAULT NULL,
  `StartDate` date DEFAULT NULL,
  `EndDate` date DEFAULT NULL,
  `Duration` varchar(50) DEFAULT NULL,
  `TypeID` int(11) DEFAULT NULL,
  `RequiredTier` enum('freemium','basic','standard','premium','premium_annual') DEFAULT 'freemium',
  `MaxStudents` int(11) DEFAULT NULL,
  `Price` decimal(10,2) DEFAULT 0.00,
  `IsPublished` tinyint(1) DEFAULT 0,
  `ApprovalStatus` enum('Approved','Pending','Rejected') DEFAULT 'Pending',
  `ApprovedBy` int(11) DEFAULT NULL,
  `ApprovedAt` timestamp NULL DEFAULT NULL,
  `RejectionReason` text DEFAULT NULL,
  `CreatedAt` timestamp NOT NULL DEFAULT current_timestamp(),
  `UpdatedAt` timestamp NOT NULL DEFAULT current_timestamp() ON UPDATE current_timestamp(),
  PRIMARY KEY (`CourseID`),
  KEY `TypeID` (`TypeID`),
  KEY `ApprovedBy` (`ApprovedBy`),
  INDEX `idx_approval_status` (`ApprovalStatus`),
  INDEX `idx_published` (`IsPublished`),
  INDEX `idx_required_tier` (`RequiredTier`),
  CONSTRAINT `courses_ibfk_1` FOREIGN KEY (`TypeID`) REFERENCES `course_types` (`TypeID`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

-- Course Prerequisites Table
CREATE TABLE `course_prerequisites` (
  `CourseID` int(11) NOT NULL,
  `PrerequisiteCourseID` int(11) NOT NULL,
  PRIMARY KEY (`CourseID`, `PrerequisiteCourseID`),
  KEY `PrerequisiteCourseID` (`PrerequisiteCourseID`),
  CONSTRAINT `course_prerequisites_ibfk_1` FOREIGN KEY (`CourseID`) REFERENCES `courses` (`CourseID`) ON DELETE CASCADE,
  CONSTRAINT `course_prerequisites_ibfk_2` FOREIGN KEY (`PrerequisiteCourseID`) REFERENCES `courses` (`CourseID`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

-- Instructor Courses (Many-to-Many)
CREATE TABLE `instructor_courses` (
  `InstructorID` int(11) NOT NULL,
  `CourseID` int(11) NOT NULL,
  `AssignedDate` timestamp NOT NULL DEFAULT current_timestamp(),
  PRIMARY KEY (`InstructorID`, `CourseID`),
  KEY `CourseID` (`CourseID`),
  CONSTRAINT `instructor_courses_ibfk_1` FOREIGN KEY (`InstructorID`) REFERENCES `instructors` (`InstructorID`) ON DELETE CASCADE,
  CONSTRAINT `instructor_courses_ibfk_2` FOREIGN KEY (`CourseID`) REFERENCES `courses` (`CourseID`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

-- Course Registrations
CREATE TABLE `course_registrations` (
  `RegistrationID` int(11) NOT NULL AUTO_INCREMENT,
  `StudentID` int(11) NOT NULL,
  `CourseID` int(11) NOT NULL,
  `RegistrationDate` date NOT NULL,
  `Status` enum('Enrolled','Completed','Dropped','In Progress') DEFAULT 'Enrolled',
  `CompletionDate` date DEFAULT NULL,
  `Grade` varchar(5) DEFAULT NULL,
  `Progress` decimal(5,2) DEFAULT 0.00,
  `CreatedAt` timestamp NOT NULL DEFAULT current_timestamp(),
  `UpdatedAt` timestamp NOT NULL DEFAULT current_timestamp() ON UPDATE current_timestamp(),
  PRIMARY KEY (`RegistrationID`),
  UNIQUE KEY `unique_enrollment` (`StudentID`,`CourseID`),
  KEY `CourseID` (`CourseID`),
  INDEX `idx_status` (`Status`),
  CONSTRAINT `course_registrations_ibfk_1` FOREIGN KEY (`StudentID`) REFERENCES `students` (`StudentID`) ON DELETE CASCADE,
  CONSTRAINT `course_registrations_ibfk_2` FOREIGN KEY (`CourseID`) REFERENCES `courses` (`CourseID`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

-- Course Materials Table
CREATE TABLE `course_materials` (
  `MaterialID` int(11) NOT NULL AUTO_INCREMENT,
  `CourseID` int(11) NOT NULL,
  `Title` varchar(100) NOT NULL,
  `Description` text DEFAULT NULL,
  `FilePath` varchar(255) DEFAULT NULL,
  `FileType` varchar(50) DEFAULT NULL,
  `FileSize` bigint(20) DEFAULT NULL,
  `IsPublic` tinyint(1) DEFAULT 1,
  `UploadedBy` int(11) NOT NULL,
  `CreatedAt` timestamp NOT NULL DEFAULT current_timestamp(),
  PRIMARY KEY (`MaterialID`),
  KEY `CourseID` (`CourseID`),
  KEY `UploadedBy` (`UploadedBy`),
  CONSTRAINT `course_materials_ibfk_1` FOREIGN KEY (`CourseID`) REFERENCES `courses` (`CourseID`) ON DELETE CASCADE,
  CONSTRAINT `course_materials_ibfk_2` FOREIGN KEY (`UploadedBy`) REFERENCES `users` (`UserID`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

-- Assessments Table
CREATE TABLE `assessments` (
  `AssessID` int(11) NOT NULL AUTO_INCREMENT,
  `CourseID` int(11) NOT NULL,
  `Type` varchar(50) DEFAULT NULL,
  `Description` text DEFAULT NULL,
  `DueDate` date DEFAULT NULL,
  `MaxScore` float DEFAULT NULL,
  `Weight` decimal(5,2) DEFAULT NULL CHECK (`Weight` between 0 and 1),
  `Instructions` text DEFAULT NULL,
  `AllowLateSubmission` tinyint(1) DEFAULT 0,
  `LatePenalty` decimal(5,2) DEFAULT 0.00,
  `CreatedAt` timestamp NOT NULL DEFAULT current_timestamp(),
  `UpdatedAt` timestamp NOT NULL DEFAULT current_timestamp() ON UPDATE current_timestamp(),
  PRIMARY KEY (`AssessID`),
  KEY `CourseID` (`CourseID`),
  INDEX `idx_due_date` (`DueDate`),
  CONSTRAINT `assessments_ibfk_1` FOREIGN KEY (`CourseID`) REFERENCES `courses` (`CourseID`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

-- Student Assessments Table
CREATE TABLE `student_assessments` (
  `StudentID` int(11) NOT NULL,
  `AssessmentID` int(11) NOT NULL,
  `Score` float DEFAULT NULL,
  `SubmissionDate` timestamp NULL DEFAULT NULL,
  `Status` enum('Not Started','In Progress','Submitted','Graded','Late') DEFAULT 'Not Started',
  `Feedback` text DEFAULT NULL,
  `SubmissionFile` varchar(255) DEFAULT NULL,
  `Attempts` int(11) DEFAULT 0,
  `TimeSpent` int(11) DEFAULT 0,
  `CreatedAt` timestamp NOT NULL DEFAULT current_timestamp(),
  `UpdatedAt` timestamp NOT NULL DEFAULT current_timestamp() ON UPDATE current_timestamp(),
  PRIMARY KEY (`StudentID`,`AssessmentID`),
  KEY `AssessmentID` (`AssessmentID`),
  INDEX `idx_status` (`Status`),
  CONSTRAINT `student_assessments_ibfk_1` FOREIGN KEY (`StudentID`) REFERENCES `students` (`StudentID`) ON DELETE CASCADE,
  CONSTRAINT `student_assessments_ibfk_2` FOREIGN KEY (`AssessmentID`) REFERENCES `assessments` (`AssessID`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

-- Certificates Table
CREATE TABLE `certificates` (
  `CertificateID` int(11) NOT NULL AUTO_INCREMENT,
  `StudentID` int(11) NOT NULL,
  `CourseID` int(11) NOT NULL,
  `CertificateNumber` varchar(50) NOT NULL UNIQUE,
  `IssuedDate` date NOT NULL,
  `FilePath` varchar(255) DEFAULT NULL,
  `VerificationCode` varchar(100) DEFAULT NULL,
  `IsValid` tinyint(1) DEFAULT 1,
  `CreatedAt` timestamp NOT NULL DEFAULT current_timestamp(),
  PRIMARY KEY (`CertificateID`),
  KEY `StudentID` (`StudentID`),
  KEY `CourseID` (`CourseID`),
  INDEX `idx_certificate_number` (`CertificateNumber`),
  INDEX `idx_verification_code` (`VerificationCode`),
  CONSTRAINT `certificates_ibfk_1` FOREIGN KEY (`StudentID`) REFERENCES `students` (`StudentID`) ON DELETE CASCADE,
  CONSTRAINT `certificates_ibfk_2` FOREIGN KEY (`CourseID`) REFERENCES `courses` (`CourseID`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

-- Jobs Table
CREATE TABLE `jobs` (
  `JobID` int(11) NOT NULL AUTO_INCREMENT,
  `CompanyID` int(11) NOT NULL,
  `Title` varchar(100) NOT NULL,
  `Description` text DEFAULT NULL,
  `Requirements` text DEFAULT NULL,
  `RequiredCourses` JSON DEFAULT NULL,
  `MinSalary` decimal(10,2) DEFAULT NULL,
  `MaxSalary` decimal(10,2) DEFAULT NULL,
  `PostingDate` date NOT NULL,
  `DeadlineDate` date DEFAULT NULL,
  `Type` enum('Full-time','Part-time','Contract','Internship','Remote') DEFAULT 'Full-time',
  `Location` varchar(128) DEFAULT NULL,
  `ExperienceLevel` enum('Entry','Mid','Senior','Executive') DEFAULT 'Entry',
  `IsActive` tinyint(1) NOT NULL DEFAULT 1,
  `IsUrgent` tinyint(1) DEFAULT 0,
  `IsFeatured` tinyint(1) DEFAULT 0,
  `Views` int(11) DEFAULT 0,
  `CreatedAt` timestamp NOT NULL DEFAULT current_timestamp(),
  `UpdatedAt` timestamp NOT NULL DEFAULT current_timestamp() ON UPDATE current_timestamp(),
  PRIMARY KEY (`JobID`),
  KEY `CompanyID` (`CompanyID`),
  INDEX `idx_posting_date` (`PostingDate`),
  INDEX `idx_deadline` (`DeadlineDate`),
  INDEX `idx_active` (`IsActive`),
  INDEX `idx_type` (`Type`),
  CONSTRAINT `jobs_ibfk_1` FOREIGN KEY (`CompanyID`) REFERENCES `companies` (`CompanyID`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

-- Application Statuses Lookup
CREATE TABLE `application_statuses` (
  `StatusID` int(11) NOT NULL AUTO_INCREMENT,
  `Name` varchar(20) NOT NULL UNIQUE,
  PRIMARY KEY (`StatusID`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

-- Job Applications Table
CREATE TABLE `job_applications` (
  `ApplicationID` int(11) NOT NULL AUTO_INCREMENT,
  `JobID` int(11) NOT NULL,
  `StudentID` int(11) NOT NULL,
  `ApplicationDate` timestamp NOT NULL DEFAULT current_timestamp(),
  `StatusID` int(11) DEFAULT 1,
  `ResumePath` varchar(255) DEFAULT NULL,
  `CoverLetter` text DEFAULT NULL,
  `Notes` text DEFAULT NULL,
  `ReviewedBy` int(11) DEFAULT NULL,
  `ReviewedAt` timestamp NULL DEFAULT NULL,
  `InterviewDate` timestamp NULL DEFAULT NULL,
  `CreatedAt` timestamp NOT NULL DEFAULT current_timestamp(),
  `UpdatedAt` timestamp NOT NULL DEFAULT current_timestamp() ON UPDATE current_timestamp(),
  PRIMARY KEY (`ApplicationID`),
  UNIQUE KEY `unique_application` (`JobID`,`StudentID`),
  KEY `StudentID` (`StudentID`),
  KEY `StatusID` (`StatusID`),
  KEY `ReviewedBy` (`ReviewedBy`),
  INDEX `idx_application_date` (`ApplicationDate`),
  CONSTRAINT `job_applications_ibfk_1` FOREIGN KEY (`JobID`) REFERENCES `jobs` (`JobID`) ON DELETE CASCADE,
  CONSTRAINT `job_applications_ibfk_2` FOREIGN KEY (`StudentID`) REFERENCES `students` (`StudentID`) ON DELETE CASCADE,
  CONSTRAINT `job_applications_ibfk_3` FOREIGN KEY (`StatusID`) REFERENCES `application_statuses` (`StatusID`),
  CONSTRAINT `job_applications_ibfk_4` FOREIGN KEY (`ReviewedBy`) REFERENCES `users` (`UserID`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

-- Admin Activity Log Table
CREATE TABLE `admin_activity_log` (
  `LogID` int(11) NOT NULL AUTO_INCREMENT,
  `AdminID` int(11) NOT NULL,
  `Action` varchar(100) NOT NULL,
  `TargetType` enum('user','course','job','application','payment') NOT NULL,
  `TargetID` int(11) NOT NULL,
  `OldValue` JSON DEFAULT NULL,
  `NewValue` JSON DEFAULT NULL,
  `Description` text DEFAULT NULL,
  `IPAddress` varchar(45) DEFAULT NULL,
  `UserAgent` text DEFAULT NULL,
  `CreatedAt` timestamp NOT NULL DEFAULT current_timestamp(),
  PRIMARY KEY (`LogID`),
  KEY `AdminID` (`AdminID`),
  INDEX `idx_action` (`Action`),
  INDEX `idx_target` (`TargetType`, `TargetID`),
  INDEX `idx_created_at` (`CreatedAt`),
  CONSTRAINT `admin_activity_log_ibfk_1` FOREIGN KEY (`AdminID`) REFERENCES `users` (`UserID`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

-- System Settings Table
CREATE TABLE `system_settings` (
  `SettingID` int(11) NOT NULL AUTO_INCREMENT,
  `SettingKey` varchar(100) NOT NULL UNIQUE,
  `SettingValue` text DEFAULT NULL,
  `Description` text DEFAULT NULL,
  `IsPublic` tinyint(1) DEFAULT 0,
  `UpdatedBy` int(11) DEFAULT NULL,
  `UpdatedAt` timestamp NOT NULL DEFAULT current_timestamp() ON UPDATE current_timestamp(),
  PRIMARY KEY (`SettingID`),
  KEY `UpdatedBy` (`UpdatedBy`),
  INDEX `idx_setting_key` (`SettingKey`),
  CONSTRAINT `system_settings_ibfk_1` FOREIGN KEY (`UpdatedBy`) REFERENCES `users` (`UserID`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

-- Insert default subscription plans
INSERT INTO `subscription_plans` (`Name`, `Description`, `Price`, `BillingCycle`, `Features`) VALUES
('Freemium', 'Free access to introductory courses', 0.00, 'monthly', 
 '{"courses": "intro_only", "certifications": "paid", "support": "community", "materials": "limited"}'),
('Basic Plan', 'Access to recordings and materials', 29.99, 'monthly', 
 '{"courses": "recordings", "certifications": "included", "support": "email", "materials": "full", "live_sessions": false}'),
('Standard Plan', 'Live sessions and interactive assessments', 49.99, 'monthly', 
 '{"courses": "live_and_recorded", "certifications": "included", "support": "priority", "materials": "full", "live_sessions": true, "assessments": "interactive"}'),
('Premium Plan', 'All features with personalized coaching', 99.99, 'monthly', 
 '{"courses": "all", "certifications": "included", "support": "24_7", "materials": "full", "live_sessions": true, "assessments": "interactive", "coaching": true, "internships": true}'),
('Premium Annual', 'Premium features with annual billing', 999.99, 'annual', 
 '{"courses": "all", "certifications": "included", "support": "24_7", "materials": "full", "live_sessions": true, "assessments": "interactive", "coaching": true, "internships": true, "installments": true}');

-- Insert default application statuses
INSERT INTO `application_statuses` (`StatusID`, `Name`) VALUES
(1, 'Pending'),
(2, 'Under Review'),
(3, 'Interview'),
(4, 'Accepted'),
(5, 'Rejected'),
(6, 'Withdrawn');

-- Insert default company sizes
INSERT INTO `company_sizes` (`SizeLabel`) VALUES
('1-10 employees'),
('11-50 employees'),
('51-200 employees'),
('201-500 employees'),
('501-1000 employees'),
('1000+ employees');

-- Insert default course types
INSERT INTO `course_types` (`TypeLabel`) VALUES
('Programming'),
('Data Science'),
('Machine Learning'),
('Web Development'),
('Mobile Development'),
('DevOps'),
('Cybersecurity'),
('UI/UX Design'),
('Business Analysis'),
('Project Management');

-- Insert default admin user
INSERT INTO `users` (`First`, `Last`, `Email`, `Password`, `UserType`, `Status`, `ApprovalStatus`) VALUES
('System', 'Administrator', 'admin@secera.com', '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewYFKL4X0WUrHa5u', 'admin', 'Active', 'Approved');

-- Insert default system settings
INSERT INTO `system_settings` (`SettingKey`, `SettingValue`, `Description`, `IsPublic`) VALUES
('site_name', 'Sec Era Platform', 'Name of the platform', 1),
('site_description', 'Advanced Learning Management System', 'Description of the platform', 1),
('max_file_size', '16777216', 'Maximum file upload size in bytes (16MB)', 0),
('allowed_file_types', 'pdf,doc,docx,txt,zip', 'Allowed file extensions for uploads', 0),
('email_notifications', '1', 'Enable email notifications', 0),
('course_approval_required', '1', 'Require admin approval for new courses', 0),
('instructor_approval_required', '1', 'Require admin approval for new instructors', 0),
('company_approval_required', '1', 'Require admin approval for new companies', 0);

COMMIT;
