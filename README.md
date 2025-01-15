# Scholarhive

Scholarhive is a platform connecting students with scholarship opportunities. It enables students to explore scholarships, submit applications, and generate professional application letters. Providers can create scholarships and manage applications efficiently.

## Table of Contents

1. [Features](#features)
2. [Requirements](#requirements)
3. [Installation and Setup](#installation-and-setup)
4. [Usage](#usage)
5. [API Endpoints](#api-endpoints)
6. [User Flow](#user-flow)
7. [Database Design](#database-design)
8. [Contributing](#contributing)
9. [License](#license)

## Features

### For Students
- Sign up and log in securely.
- Explore available scholarships.
- Submit applications, including file uploads.
- Generate application letters.
- Track application statuses.

### For Providers
- Sign up and log in securely.
- Create, update, and delete scholarships.
- Customize application forms.
- View and manage student applications.
- Accept or reject applications.

## Requirements

To run Scholarhive locally, ensure the following are installed:

- Python 3.10+
- Node.js 16+
- PostgreSQL 12+
- pipenv

### Libraries and Frameworks
- Backend: Django, Django REST Framework
- Frontend: React
- Database: PostgreSQL

## Installation and Setup

### Clone the Repository
```bash
git clone https://github.com/yourusername/scholarhive.git
cd scholarhive
```

### Backend Setup

1. Navigate to the `backend` directory:
   ```bash
   cd backend
   ```

2. Create a virtual environment and install dependencies:
   ```bash
   pipenv install
   pipenv shell
   ```

3. Configure environment variables:
   - Create a `.env` file in the `backend` directory with the following:
     ```env
     SECRET_KEY=your-secret-key
     DEBUG=True
     DATABASE_NAME=your-database-name
     DATABASE_USER=your-username
     DATABASE_PASSWORD=your-db-password
     DATABASE_HOST=localhost
     DATABASE_PORT=5432
     ```

4. Apply database migrations:
   ```bash
   python manage.py makemigrations
   python manage.py migrate
   ```

5. Run the development server:
   ```bash
   python manage.py runserver
   ```

### Frontend Setup

1. Navigate to the `frontend` directory:
   ```bash
   cd frontend
   ```

2. Install dependencies:
   ```bash
   npm install
   ```

3. Start the development server:
   ```bash
   npm start
   ```

## Usage

### Running Locally

1. Start the backend server (from the `backend` directory):
   ```bash
   python manage.py runserver
   ```

2. Start the frontend server (from the `frontend` directory):
   ```bash
   npm start
   ```

3. Open your browser and navigate to `http://localhost:3000` to access the application.

### Testing API Endpoints

Use Postman or any API client to test backend endpoints. Ensure you provide the required headers (e.g., authentication tokens) where necessary.

## API Endpoints

### Authentication
- **POST** `/api/student/register/` - Register a new student.
- **POST** `/api/provider/register/` - Register a new provider.
- **POST** `/api/login/` - Log in as a student or provider.

### Scholarships
- **GET** `/api/scholarships/` - List all scholarships.
- **POST** `/api/provider/scholarships/` - Create a scholarship (providers only).

### Applications
- **POST** `/api/scholarships/{id}/apply/` - Submit an application (students only).
- **GET** `/api/provider/scholarships/{id}/applications/` - View applications for a scholarship (providers only).

For a full list of endpoints, refer to the API documentation in the `docs` folder.

## User Flow

1. **Student Workflow**:
   - Sign up as a student.
   - Log in to your account.
   - Browse available scholarships.
   - View details of a scholarship.
   - Fill out and submit the application form.
   - Track your application status.

2. **Provider Workflow**:
   - Sign up as a provider.
   - Log in to your account.
   - Create a scholarship and define its application form.
   - Manage applications by viewing, accepting, or rejecting them.

## Database Design

### Key Models

1. **Students**
   - `first_name`, `last_name`, `email`, `education_level`.

2. **Providers**
   - `organization_name`, `email`, `website_url`.

3. **Scholarships**
   - `title`, `description`, `provider`, `deadline`.

4. **Applications**
   - `student`, `scholarship`, `status`, `responses`.

### Relationships
- A **Provider** can create multiple **Scholarships**.
- A **Student** can apply to multiple **Scholarships**.
- Each **Application** is linked to one **Student** and one **Scholarship**.

## Contributing

Contributions are welcome! To contribute:

1. Fork the repository.
2. Create a feature branch:
   ```bash
   git checkout -b feature-name
   ```
3. Commit your changes:
   ```bash
   git commit -m "Description of changes"
   ```
4. Push to the branch:
   ```bash
   git push origin feature-name
   ```
5. Open a pull request.

## License

This project is licensed under the MIT License. See the `LICENSE` file for more details.

