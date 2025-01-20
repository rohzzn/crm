# Insurance Agent Client Management System

A Flask-based web application for insurance agents to manage their clients and dependents.

## Features Implemented

- User authentication (register, login, logout)
- Client management (CRUD operations)
- Dependent management for each client
- Pagination for client list
- Search functionality for clients
- Access control (agents can only access their own clients/dependents)
- Flash messages for user feedback
- Secure password hashing with bcrypt
- Enhanced client fields with comprehensive data collection
- Client data validation and error handling
- Policy management and search

## Prerequisites

- Python 3.8 or higher
- pip (Python package manager)
- Virtual environment (recommended)

## Installation & Setup

1. Clone the repository:
```bash
git clone https://github.com/photonguava/mc_crm
cd mc_crm
```

2. Create and activate a virtual environment:
```bash
# Windows
python -m venv venv
venv\Scripts\activate

# macOS/Linux
python3 -m venv venv
source venv/bin/activate
```

3. Install required packages:
```bash
pip install -r requirements.txt
```

4. Run the application:
```bash
python app.py
```

The application will be available at `http://127.0.0.1:5000`

Note: The database will be automatically initialized when you first run the application.

## Project Structure

```
├── app.py              # Application initialization
├── config.py           # Configuration settings
├── models.py           # Database models
├── routes.py           # Route handlers
└── templates/          # HTML templates
    ├── auth/          
    │   ├── login.html
    │   └── register.html
    ├── clients/
    │   ├── add_client.html
    │   ├── clients.html
    │   └── edit_client.html
    └── home.html
```

## Future Development Checklist


- [ ] Add profile management for agents
- [ ] Add policy management

## QOL Improvements
- [x] Improve client fields
- [x] Add validation for client data

## v2 Features
- [ ] Add email verification for new agent registrations
- [ ] Implement password reset functionality
- [ ] Add Google Login
- [ ] Add Payments
- [ ] Add cronjob for sending reminders



## Contributing

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/NEWFeature`)
3. Commit your changes (`git commit -m 'Add some new Feature'`)
4. Push to the branch (`git push origin feature/NEWFeature`)
5. Open a Pull Request
