-- SQL script to create contact_requests table for the help system

CREATE TABLE IF NOT EXISTS contact_requests (
    RequestID INT AUTO_INCREMENT PRIMARY KEY,
    UserID INT NULL,
    Name VARCHAR(255) NOT NULL,
    Email VARCHAR(255) NOT NULL,
    Subject VARCHAR(255) NOT NULL,
    Message TEXT NOT NULL,
    Priority ENUM('low', 'normal', 'high', 'critical') DEFAULT 'normal',
    Category ENUM('general', 'technical', 'billing', 'course', 'account', 'feature', 'bug', 'other') DEFAULT 'general',
    Status ENUM('open', 'in_progress', 'resolved', 'closed') DEFAULT 'open',
    AdminResponse TEXT NULL,
    AssignedTo INT NULL,
    CreatedAt TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UpdatedAt TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    ResolvedAt TIMESTAMP NULL,
    
    FOREIGN KEY (UserID) REFERENCES users(UserID) ON DELETE SET NULL,
    FOREIGN KEY (AssignedTo) REFERENCES users(UserID) ON DELETE SET NULL,
    
    INDEX idx_status (Status),
    INDEX idx_priority (Priority),
    INDEX idx_category (Category),
    INDEX idx_created_at (CreatedAt),
    INDEX idx_user_id (UserID)
);

-- Create table for FAQ management (for future admin functionality)
CREATE TABLE IF NOT EXISTS faq_items (
    FAQID INT AUTO_INCREMENT PRIMARY KEY,
    Category VARCHAR(100) NOT NULL,
    Question TEXT NOT NULL,
    Answer TEXT NOT NULL,
    SortOrder INT DEFAULT 0,
    IsActive BOOLEAN DEFAULT TRUE,
    CreatedBy INT NULL,
    CreatedAt TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UpdatedAt TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    
    FOREIGN KEY (CreatedBy) REFERENCES users(UserID) ON DELETE SET NULL,
    
    INDEX idx_category (Category),
    INDEX idx_active (IsActive),
    INDEX idx_sort_order (SortOrder)
);

-- Insert some default FAQ items
INSERT INTO faq_items (Category, Question, Answer, SortOrder) VALUES
('General', 'What is Sec Era Platform?', 'Sec Era is a comprehensive cybersecurity learning platform offering courses, certifications, and hands-on training for security professionals and enthusiasts.', 1),
('General', 'How do I get started?', 'Simply create an account and choose your learning path. You can start with our free courses or upgrade to premium for full access.', 2),
('General', 'Is there a mobile app?', 'Currently, we offer a fully responsive web platform. A mobile app is in development and will be available soon.', 3),
('Subscriptions', 'What subscription plans are available?', 'We offer Freemium (free), Standard ($29/month), and Premium ($99/year) plans with different levels of access to courses and features.', 1),
('Subscriptions', 'Can I cancel my subscription anytime?', 'Yes, you can cancel your subscription at any time. You will retain access until the end of your billing period.', 2),
('Subscriptions', 'Do you offer refunds?', 'We offer a 30-day money-back guarantee for all paid subscriptions. Contact support for refund requests.', 3),
('Courses', 'Are the certifications industry-recognized?', 'Our certifications are recognized by leading cybersecurity organizations and employers worldwide.', 1),
('Courses', 'Do I need prior experience?', 'We offer courses for all skill levels, from complete beginners to advanced professionals.', 2),
('Courses', 'How long do courses take to complete?', 'Course duration varies from 2-40 hours depending on the complexity and depth of the subject matter.', 3),
('Technical', 'I am having trouble accessing my account', 'Try resetting your password. If the issue persists, contact our support team with your email address.', 1),
('Technical', 'The platform is running slowly', 'Clear your browser cache and cookies. If issues continue, try using a different browser or contact support.', 2),
('Technical', 'I cannot submit my assignments', 'Ensure your files meet the size and format requirements. Check your internet connection and try again.', 3);

-- Create table for system announcements and notifications
CREATE TABLE IF NOT EXISTS system_announcements (
    AnnouncementID INT AUTO_INCREMENT PRIMARY KEY,
    Title VARCHAR(255) NOT NULL,
    Content TEXT NOT NULL,
    Type ENUM('info', 'warning', 'success', 'danger') DEFAULT 'info',
    Priority ENUM('low', 'normal', 'high') DEFAULT 'normal',
    TargetAudience ENUM('all', 'students', 'instructors', 'companies', 'admins') DEFAULT 'all',
    IsActive BOOLEAN DEFAULT TRUE,
    StartDate TIMESTAMP NULL,
    EndDate TIMESTAMP NULL,
    CreatedBy INT NULL,
    CreatedAt TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UpdatedAt TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    
    FOREIGN KEY (CreatedBy) REFERENCES users(UserID) ON DELETE SET NULL,
    
    INDEX idx_active (IsActive),
    INDEX idx_type (Type),
    INDEX idx_target (TargetAudience),
    INDEX idx_dates (StartDate, EndDate)
);
