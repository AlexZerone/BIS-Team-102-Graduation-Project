-- SQL script to enhance job applications with prerequisite checking

-- Add columns to job_applications table for prerequisite tracking
ALTER TABLE job_applications 
ADD COLUMN PrerequisiteScore DECIMAL(5,2) DEFAULT 0.00 COMMENT 'Percentage score of how well student meets prerequisites (0-100)',
ADD COLUMN Notes TEXT NULL COMMENT 'JSON data containing prerequisite check results and recommendations';

-- Add column to jobs table for structured requirements
ALTER TABLE jobs 
ADD COLUMN StructuredRequirements JSON NULL COMMENT 'JSON structure for automated prerequisite checking';

-- Create index for better performance on prerequisite scores
CREATE INDEX idx_prerequisite_score ON job_applications(PrerequisiteScore);

-- Update existing jobs with sample structured requirements for testing
UPDATE jobs 
SET StructuredRequirements = JSON_OBJECT(
    'required_courses', JSON_ARRAY(),
    'required_certifications', JSON_ARRAY(),
    'preferred_skills', JSON_ARRAY(),
    'minimum_experience', 'beginner',
    'subscription_level', 'any'
) 
WHERE StructuredRequirements IS NULL;

-- Add some sample structured requirements for cybersecurity jobs
UPDATE jobs 
SET StructuredRequirements = JSON_OBJECT(
    'required_courses', JSON_ARRAY('Introduction to Cybersecurity', 'Network Security Fundamentals'),
    'required_certifications', JSON_ARRAY(),
    'preferred_skills', JSON_ARRAY('penetration testing', 'vulnerability assessment', 'incident response'),
    'minimum_experience', 'intermediate',
    'subscription_level', 'standard'
)
WHERE Title LIKE '%Security%' OR Title LIKE '%Cyber%' LIMIT 3;

-- Add table for tracking user skill assessments (for future enhancement)
CREATE TABLE IF NOT EXISTS user_skills (
    SkillID INT AUTO_INCREMENT PRIMARY KEY,
    StudentID INT NOT NULL,
    SkillName VARCHAR(255) NOT NULL,
    ProficiencyLevel ENUM('beginner', 'intermediate', 'advanced', 'expert') DEFAULT 'beginner',
    VerifiedDate TIMESTAMP NULL,
    VerificationMethod ENUM('course_completion', 'certification', 'assessment', 'self_reported') DEFAULT 'self_reported',
    CreatedAt TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UpdatedAt TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    
    FOREIGN KEY (StudentID) REFERENCES students(StudentID) ON DELETE CASCADE,
    
    UNIQUE KEY unique_student_skill (StudentID, SkillName),
    INDEX idx_student_skills (StudentID),
    INDEX idx_skill_name (SkillName),
    INDEX idx_proficiency (ProficiencyLevel)
);

-- Add table for job recommendation tracking
CREATE TABLE IF NOT EXISTS job_recommendations (
    RecommendationID INT AUTO_INCREMENT PRIMARY KEY,
    StudentID INT NOT NULL,
    JobID INT NOT NULL,
    RecommendationScore DECIMAL(5,2) NOT NULL,
    RecommendationReason TEXT,
    IsViewed BOOLEAN DEFAULT FALSE,
    CreatedAt TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    FOREIGN KEY (StudentID) REFERENCES students(StudentID) ON DELETE CASCADE,
    FOREIGN KEY (JobID) REFERENCES jobs(JobID) ON DELETE CASCADE,
    
    UNIQUE KEY unique_recommendation (StudentID, JobID),
    INDEX idx_student_recommendations (StudentID),
    INDEX idx_score (RecommendationScore DESC),
    INDEX idx_viewed (IsViewed)
);

-- Add table for application feedback and improvement suggestions
CREATE TABLE IF NOT EXISTS application_feedback (
    FeedbackID INT AUTO_INCREMENT PRIMARY KEY,
    ApplicationID INT NOT NULL,
    FeedbackType ENUM('prerequisite_suggestion', 'skill_improvement', 'course_recommendation') NOT NULL,
    Title VARCHAR(255) NOT NULL,
    Description TEXT NOT NULL,
    Priority ENUM('low', 'medium', 'high') DEFAULT 'medium',
    IsCompleted BOOLEAN DEFAULT FALSE,
    CreatedAt TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    CompletedAt TIMESTAMP NULL,
    
    FOREIGN KEY (ApplicationID) REFERENCES job_applications(ApplicationID) ON DELETE CASCADE,
    
    INDEX idx_application_feedback (ApplicationID),
    INDEX idx_feedback_type (FeedbackType),
    INDEX idx_priority (Priority),
    INDEX idx_completed (IsCompleted)
);
