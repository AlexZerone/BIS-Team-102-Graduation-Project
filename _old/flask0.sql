-- Improved SQL Schema for Sec Era Platform
-- Includes best practices: timestamps, constraints, sensible defaults, indexes, and audit fields

SET SQL_MODE = "NO_AUTO_VALUE_ON_ZERO";
START TRANSACTION;
SET time_zone = "+00:00";

-- Users Table
CREATE TABLE `users` (
  `UserID` int(11) NOT NULL AUTO_INCREMENT,
  `First` varchar(64) NOT NULL,
  `Last` varchar(64) NOT NULL,
  `Email` varchar(255) NOT NULL UNIQUE,
  `Password` varchar(255) NOT NULL,
  `UserType` enum('student','instructor','company') NOT NULL,
  `ProfilePicture` varchar(255) DEFAULT NULL,
  `CreatedAt` timestamp NOT NULL DEFAULT current_timestamp(),
  `UpdatedAt` timestamp NOT NULL DEFAULT current_timestamp() ON UPDATE current_timestamp(),
  `Status` enum('Active','Inactive') NOT NULL DEFAULT 'Active',
  PRIMARY KEY (`UserID`)
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
  `CreatedAt` timestamp NOT NULL DEFAULT current_timestamp(),
  `UpdatedAt` timestamp NOT NULL DEFAULT current_timestamp() ON UPDATE current_timestamp(),
  PRIMARY KEY (`StudentID`),
  KEY `UserID` (`UserID`),
  CONSTRAINT `students_ibfk_1` FOREIGN KEY (`UserID`) REFERENCES `users` (`UserID`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

-- Instructors Table
CREATE TABLE `instructors` (
  `InstructorID` int(11) NOT NULL AUTO_INCREMENT,
  `UserID` int(11) NOT NULL,
  `Department` varchar(128) DEFAULT NULL,
  `Specialization` varchar(128) DEFAULT NULL,
  `Experience` int(11) DEFAULT NULL,
  `Bio` text DEFAULT NULL,
  `CreatedAt` timestamp NOT NULL DEFAULT current_timestamp(),
  `UpdatedAt` timestamp NOT NULL DEFAULT current_timestamp() ON UPDATE current_timestamp(),
  PRIMARY KEY (`InstructorID`),
  KEY `UserID` (`UserID`),
  CONSTRAINT `instructors_ibfk_1` FOREIGN KEY (`UserID`) REFERENCES `users` (`UserID`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

-- Companies Table
CREATE TABLE `companies` (
  `CompanyID` int(11) NOT NULL AUTO_INCREMENT,
  `UserID` int(11) NOT NULL,
  `Name` varchar(128) NOT NULL,
  `Industry` varchar(128) DEFAULT NULL,
  `Location` varchar(128) DEFAULT NULL,
  `CompanySize` int(11) DEFAULT NULL,
  `FoundedDate` date DEFAULT NULL,
  `Bio` text DEFAULT NULL,
  `CreatedAt` timestamp NOT NULL DEFAULT current_timestamp(),
  `UpdatedAt` timestamp NOT NULL DEFAULT current_timestamp() ON UPDATE current_timestamp(),
  PRIMARY KEY (`CompanyID`),
  KEY `UserID` (`UserID`),
  CONSTRAINT `companies_ibfk_1` FOREIGN KEY (`UserID`) REFERENCES `users` (`UserID`) ON DELETE CASCADE
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

-- Courses Table
CREATE TABLE `courses` (
  `CourseID` int(11) NOT NULL AUTO_INCREMENT,
  `Title` varchar(100) NOT NULL UNIQUE,
  `Description` text DEFAULT NULL,
  `StartDate` date DEFAULT NULL,
  `EndDate` date DEFAULT NULL,
  `Duration` varchar(50) DEFAULT NULL,
  `TypeID` int(11) DEFAULT NULL,
  `CreatedAt` timestamp NOT NULL DEFAULT current_timestamp(),
  `UpdatedAt` timestamp NOT NULL DEFAULT current_timestamp() ON UPDATE current_timestamp(),
  PRIMARY KEY (`CourseID`),
  KEY `TypeID` (`TypeID`),
  CONSTRAINT `courses_ibfk_1` FOREIGN KEY (`TypeID`) REFERENCES `course_types` (`TypeID`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

-- Instructor Courses (Many-to-Many)
CREATE TABLE `instructor_courses` (
  `InstructorID` int(11) NOT NULL,
  `CourseID` int(11) NOT NULL,
  PRIMARY KEY (`InstructorID`,`CourseID`),
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
  `Status` enum('Enrolled','Completed','Dropped') DEFAULT 'Enrolled',
  `CompletionDate` date DEFAULT NULL,
  `Grade` varchar(5) DEFAULT NULL,
  `CreatedAt` timestamp NOT NULL DEFAULT current_timestamp(),
  `UpdatedAt` timestamp NOT NULL DEFAULT current_timestamp() ON UPDATE current_timestamp(),
  PRIMARY KEY (`RegistrationID`),
  UNIQUE KEY `unique_enrollment` (`StudentID`,`CourseID`),
  KEY `CourseID` (`CourseID`),
  CONSTRAINT `course_registrations_ibfk_1` FOREIGN KEY (`StudentID`) REFERENCES `students` (`StudentID`) ON DELETE CASCADE,
  CONSTRAINT `course_registrations_ibfk_2` FOREIGN KEY (`CourseID`) REFERENCES `courses` (`CourseID`) ON DELETE CASCADE
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
  `CreatedAt` timestamp NOT NULL DEFAULT current_timestamp(),
  `UpdatedAt` timestamp NOT NULL DEFAULT current_timestamp() ON UPDATE current_timestamp(),
  PRIMARY KEY (`AssessID`),
  KEY `CourseID` (`CourseID`),
  CONSTRAINT `assessments_ibfk_1` FOREIGN KEY (`CourseID`) REFERENCES `courses` (`CourseID`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

-- Student Assessments Table
CREATE TABLE `student_assessments` (
  `StudentID` int(11) NOT NULL,
  `AssessmentID` int(11) NOT NULL,
  `Score` float DEFAULT NULL,
  `SubmissionDate` date DEFAULT NULL,
  `Status` varchar(50) DEFAULT NULL,
  `Feedback` text DEFAULT NULL,
  `CreatedAt` timestamp NOT NULL DEFAULT current_timestamp(),
  `UpdatedAt` timestamp NOT NULL DEFAULT current_timestamp() ON UPDATE current_timestamp(),
  PRIMARY KEY (`StudentID`,`AssessmentID`),
  KEY `AssessmentID` (`AssessmentID`),
  CONSTRAINT `student_assessments_ibfk_1` FOREIGN KEY (`StudentID`) REFERENCES `students` (`StudentID`) ON DELETE CASCADE,
  CONSTRAINT `student_assessments_ibfk_2` FOREIGN KEY (`AssessmentID`) REFERENCES `assessments` (`AssessID`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

-- Jobs Table
CREATE TABLE `jobs` (
  `JobID` int(11) NOT NULL AUTO_INCREMENT,
  `CompanyID` int(11) NOT NULL,
  `Title` varchar(100) NOT NULL,
  `Description` text DEFAULT NULL,
  `Requirements` text DEFAULT NULL,
  `MinSalary` decimal(10,2) DEFAULT NULL,
  `MaxSalary` decimal(10,2) DEFAULT NULL,
  `PostingDate` date NOT NULL,
  `DeadlineDate` date DEFAULT NULL,
  `Type` varchar(50) DEFAULT NULL,
  `Location` varchar(128) DEFAULT NULL,
  `IsActive` tinyint(1) NOT NULL DEFAULT 1,
  `CreatedAt` timestamp NOT NULL DEFAULT current_timestamp(),
  `UpdatedAt` timestamp NOT NULL DEFAULT current_timestamp() ON UPDATE current_timestamp(),
  PRIMARY KEY (`JobID`),
  KEY `CompanyID` (`CompanyID`),
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
  `ApplicationDate` date NOT NULL,
  `StatusID` int(11) DEFAULT 1,
  `ResumePath` varchar(255) DEFAULT NULL,
  `CoverLetter` text DEFAULT NULL,
  `CreatedAt` timestamp NOT NULL DEFAULT current_timestamp(),
  `UpdatedAt` timestamp NOT NULL DEFAULT current_timestamp() ON UPDATE current_timestamp(),
  PRIMARY KEY (`ApplicationID`),
  UNIQUE KEY `unique_application` (`JobID`,`StudentID`),
  KEY `StudentID` (`StudentID`),
  KEY `StatusID` (`StatusID`),
  CONSTRAINT `job_applications_ibfk_1` FOREIGN KEY (`JobID`) REFERENCES `jobs` (`JobID`) ON DELETE CASCADE,
  CONSTRAINT `job_applications_ibfk_2` FOREIGN KEY (`StudentID`) REFERENCES `students` (`StudentID`) ON DELETE CASCADE,
  CONSTRAINT `job_applications_ibfk_3` FOREIGN KEY (`StatusID`) REFERENCES `application_statuses` (`StatusID`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

COMMIT;
