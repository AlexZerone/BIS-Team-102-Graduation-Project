"""
Admin System Documentation - Sec Era Platform
===============================================

This document provides comprehensive information about the admin system implementation.

## Overview
The Sec Era Platform admin system provides comprehensive management capabilities for:
- User management and role assignments
- Course and instructor approval workflows  
- Company registration approvals
- Subscription and payment management
- Contact request handling
- System analytics and reporting

## Features Implemented

### 1. Admin Dashboard
- **Route**: `/admin` or `/admin/dashboard`
- **Features**: 
  - Real-time statistics overview
  - Pending approval notifications
  - Recent activity feed
  - System health indicators
  - Quick action buttons

### 2. User Management
- **Route**: `/admin/users`
- **Features**:
  - View all platform users
  - Filter by user type (Student, Instructor, Company, Admin)
  - Toggle user status (active/inactive)
  - User registration analytics
  - Search and pagination

### 3. Approval Workflows
- **Pending Instructors**: `/admin/pending-instructors`
  - Review instructor applications
  - Approve/reject with notes
  - View instructor credentials
  
- **Pending Companies**: `/admin/pending-companies`
  - Review company registrations
  - Verify business information
  - Approve/reject applications
  
- **Pending Courses**: `/admin/pending-courses`
  - Review course submissions
  - Content quality assessment
  - Approve/reject courses

### 4. Subscription Management
- **Route**: `/admin/subscriptions`
- **Features**:
  - View all subscription plans
  - Monitor payment statuses
  - Revenue analytics
  - Subscription trends

### 5. Contact Request Management
- **Route**: `/admin/contact-requests`
- **Features**:
  - View all support tickets
  - Filter by status and priority
  - Update ticket status
  - Add admin notes
  - Response tracking

### 6. Reports and Analytics
- **Route**: `/admin/reports`
- **Features**:
  - User registration trends
  - Course enrollment statistics
  - Job application analytics
  - Popular courses analysis
  - Revenue reports

### 7. System Settings
- **Route**: `/admin/settings`
- **Features**:
  - Platform configuration
  - Email settings
  - Security parameters
  - Feature toggles

## API Endpoints

### Real-time Data APIs
All API endpoints require admin authentication and return JSON responses.

1. **Statistics API**: `/admin/api/stats`
   - Returns real-time platform statistics
   - User counts, course metrics, revenue data
   - Contact request statistics

2. **Notifications API**: `/admin/api/notifications`
   - Pending approvals requiring attention
   - Critical alerts and system notifications
   - Priority-based notification system

3. **Activity Feed API**: `/admin/api/activity`
   - Recent platform activities
   - User registrations, course submissions
   - Contact requests and other events

## File Upload System

### Upload Endpoints
- **Profile Images**: `/uploads/profile-image`
- **Course Materials**: `/uploads/course-material`  
- **Admin Documents**: `/uploads/admin-document`

### Supported File Types
- **Images**: PNG, JPG, JPEG, GIF, WebP (max 5MB)
- **Documents**: PDF, DOC, DOCX, TXT, MD (max 10MB)
- **Videos**: MP4, AVI, MOV, WMV, FLV (max 100MB)
- **Archives**: ZIP, RAR, 7Z, TAR, GZ (max 50MB)

## Security Features

### Authentication
- Admin-only access control
- Session-based authentication
- Role-based permissions
- CSRF protection

### Password Security
- Secure password hashing with Werkzeug
- Password migration utility for existing accounts
- Automatic password strength validation

### File Upload Security
- File type validation
- Size limit enforcement
- Secure filename generation
- Upload directory protection

## Database Schema

### Key Tables Used
- `users` - Platform user accounts
- `instructors` - Instructor applications
- `companies` - Company registrations
- `courses` - Course submissions
- `contact_requests` - Support tickets
- `subscription_payments` - Payment records
- `course_registrations` - Enrollment data
- `job_applications` - Job application tracking

## UI/UX Design

### Design System
- **Primary Color**: #223947 (Dark Blue-Green)
- **Theme**: Modern dark theme with gradient accents
- **Typography**: Clean, professional fonts
- **Layout**: Responsive sidebar navigation
- **Components**: Bootstrap 5 with custom styling

### Navigation Structure
```
Admin Dashboard
├── Dashboard (Overview)
├── User Management
│   ├── All Users
│   └── User Analytics
├── Approvals
│   ├── Pending Instructors
│   ├── Pending Companies
│   └── Pending Courses
├── Subscriptions
│   ├── Active Subscriptions
│   └── Payment History
├── Support
│   └── Contact Requests
├── Reports
│   ├── User Analytics
│   ├── Course Statistics
│   └── Revenue Reports
└── Settings
    ├── Platform Settings
    └── System Configuration
```

## Installation & Setup

### Requirements
- Python 3.8+
- Flask 2.0+
- MySQL/MariaDB
- Required Python packages (see requirements.txt)

### Environment Setup
1. Install dependencies: `pip install -r requirements.txt`
2. Configure database connection in `config.py`
3. Initialize database with provided SQL files
4. Create admin user account
5. Run application: `python app.py`

### Admin Account Creation
To create an admin account, either:
1. Use the password migration utility: `/admin/fix-passwords`
2. Manually insert into database with role 'admin'
3. Use the user registration with admin role assignment

## Testing

### Test Suite
Run the comprehensive admin test suite:
```bash
python test_admin_interface.py
```

### Test Coverage
- ✅ All admin routes accessibility
- ✅ Template rendering
- ✅ API endpoint responses
- ✅ Authentication enforcement
- ✅ File upload validation
- ✅ Database operations

## Maintenance

### Regular Tasks
1. **User Management**: Review and approve pending applications
2. **Content Moderation**: Review course submissions
3. **Support**: Respond to contact requests
4. **Analytics**: Monitor platform performance
5. **Security**: Review user activities and system logs

### Monitoring
- Check dashboard notifications daily
- Review pending approval queues
- Monitor system performance metrics
- Track user engagement statistics

## Troubleshooting

### Common Issues
1. **Authentication Problems**: Check session configuration
2. **Database Errors**: Verify MySQL connection settings
3. **File Upload Issues**: Check directory permissions
4. **Template Errors**: Validate Jinja2 syntax

### Error Handling
- Comprehensive try-catch blocks
- User-friendly error messages
- Logging for debugging
- Graceful fallbacks

## Future Enhancements

### Planned Features
1. **Advanced Analytics**: Charts and graphs
2. **Email Notifications**: Automated admin alerts
3. **Bulk Operations**: Mass user management
4. **API Documentation**: Swagger/OpenAPI integration
5. **Mobile App**: Admin mobile interface
6. **Audit Logs**: Complete action tracking

### Scalability Considerations
- Database optimization
- Caching implementation
- Load balancing support
- CDN integration for file uploads

---

**Last Updated**: June 11, 2025
**Version**: 2.0.0
**Status**: Production Ready ✅

For technical support or questions, contact the development team.
"""
