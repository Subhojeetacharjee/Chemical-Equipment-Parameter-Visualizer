# Chemical Equipment Parameter Visualizer

A full-stack hybrid application for uploading, analyzing, and visualizing chemical equipment data. This project includes a Django REST API backend, a React.js web frontend, and a PyQt5 desktop application.

![Project Banner](https://via.placeholder.com/1200x300/667eea/ffffff?text=Chemical+Equipment+Parameter+Visualizer)

## 📋 Table of Contents

- [Features](#-features)
- [Tech Stack](#-tech-stack)
- [Project Structure](#-project-structure)
- [Prerequisites](#-prerequisites)
- [Installation](#-installation)
  - [Backend Setup](#backend-setup)
  - [Web Frontend Setup](#web-frontend-setup)
  - [Desktop Application Setup](#desktop-application-setup)
- [Usage](#-usage)
- [API Documentation](#-api-documentation)
- [Screenshots](#-screenshots)
- [Contributing](#-contributing)
- [License](#-license)

## ✨ Features

- **CSV Upload**: Upload CSV files with equipment data (Equipment Name, Type, Flowrate, Pressure, Temperature)
- **Data Analysis**: Automatic calculation of summary statistics
  - Total equipment count
  - Average values for Flowrate, Pressure, and Temperature
  - Equipment type distribution
- **Data Visualization**:
  - Interactive charts using Chart.js (Web)
  - Matplotlib charts (Desktop)
  - Pie charts, bar charts, and line graphs
- **History Management**: Store and access the last 5 uploaded datasets
- **PDF Report Generation**: Generate detailed PDF reports with authentication
- **Dual Interface**: Access via web browser or desktop application
- **Responsive Design**: Web application works on all screen sizes

## 🛠 Tech Stack

| Component | Technology |
|-----------|------------|
| Backend | Python Django + Django REST Framework |
| Web Frontend | React.js + Chart.js |
| Desktop Frontend | PyQt5 + Matplotlib |
| Data Processing | Pandas |
| Database | SQLite |
| PDF Generation | ReportLab |

## 📁 Project Structure

```
Chemical Equipment Parameter Visualizer/
├── backend/                          # Django REST API
│   ├── api/                          # API application
│   │   ├── models.py                 # Database models
│   │   ├── serializers.py            # REST serializers
│   │   ├── views.py                  # API views
│   │   ├── urls.py                   # API routes
│   │   └── admin.py                  # Admin configuration
│   ├── backend/                      # Django project settings
│   │   ├── settings.py               # Project settings
│   │   ├── urls.py                   # Main URL configuration
│   │   └── wsgi.py                   # WSGI configuration
│   ├── manage.py                     # Django management script
│   └── requirements.txt              # Python dependencies
├── web-frontend/                     # React Web Application
│   ├── public/
│   │   └── index.html
│   ├── src/
│   │   ├── components/               # React components
│   │   │   ├── Charts.js             # Chart.js visualizations
│   │   │   ├── DataTable.js          # Data table component
│   │   │   ├── FileUpload.js         # File upload component
│   │   │   ├── History.js            # History list component
│   │   │   ├── ReportModal.js        # PDF report modal
│   │   │   └── SummaryCards.js       # Summary statistics cards
│   │   ├── services/
│   │   │   └── api.js                # API service layer
│   │   ├── App.js                    # Main application component
│   │   ├── index.js                  # React entry point
│   │   └── index.css                 # Global styles
│   └── package.json                  # Node.js dependencies
├── desktop-frontend/                 # PyQt5 Desktop Application
│   ├── main.py                       # Desktop application entry point
│   └── requirements.txt              # Python dependencies
├── sample_equipment_data.csv         # Sample data for testing
└── README.md                         # This file
```

## 📌 Prerequisites

Before you begin, ensure you have the following installed:

- **Python 3.9+** - [Download](https://www.python.org/downloads/)
- **Node.js 18+** - [Download](https://nodejs.org/)
- **Git** - [Download](https://git-scm.com/)

## 🚀 Installation

### Backend Setup

1. **Navigate to the backend directory:**
   ```bash
   cd backend
   ```

2. **Create and activate a virtual environment:**
   ```bash
   # Windows
   python -m venv venv
   venv\Scripts\activate

   # macOS/Linux
   python3 -m venv venv
   source venv/bin/activate
   ```

3. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

4. **Run database migrations:**
   ```bash
   python manage.py migrate
   ```

5. **Create a superuser (for PDF report generation):**
   ```bash
   python manage.py createsuperuser
   ```
   Follow the prompts to create an admin user.

6. **Start the development server:**
   ```bash
   python manage.py runserver
   ```
   The API will be available at `http://localhost:8000/api/`

### Web Frontend Setup

1. **Open a new terminal and navigate to the web frontend directory:**
   ```bash
   cd web-frontend
   ```

2. **Install dependencies:**
   ```bash
   npm install
   ```

3. **Start the development server:**
   ```bash
   npm start
   ```
   The web application will open at `http://localhost:3000`

### Desktop Application Setup

1. **Open a new terminal and navigate to the desktop frontend directory:**
   ```bash
   cd desktop-frontend
   ```

2. **Create and activate a virtual environment (recommended):**
   ```bash
   # Windows
   python -m venv venv
   venv\Scripts\activate

   # macOS/Linux
   python3 -m venv venv
   source venv/bin/activate
   ```

3. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

4. **Run the desktop application:**
   ```bash
   python main.py
   ```

## 💻 Usage

### Using the Web Application

1. Open `http://localhost:3000` in your browser
2. Click on the upload area or drag & drop a CSV file
3. View the summary statistics and interactive charts
4. Switch between Charts and Data Table tabs
5. Access upload history in the sidebar
6. Click "Generate PDF Report" to create a downloadable report (requires authentication)

### Using the Desktop Application

1. Run `python main.py` in the desktop-frontend directory
2. Click "Select CSV File" to choose a CSV file
3. View summary statistics and Matplotlib charts
4. Switch between Charts and Data Table tabs
5. Select previous uploads from the history list
6. Click "Generate PDF Report" to save a report

### CSV File Format

Your CSV file should have the following columns:

| Column | Description | Type |
|--------|-------------|------|
| Equipment Name | Name/identifier of the equipment | Text |
| Type | Type/category of equipment | Text |
| Flowrate | Flowrate value | Number |
| Pressure | Pressure value | Number |
| Temperature | Temperature value | Number |

**Example:**
```csv
Equipment Name,Type,Flowrate,Pressure,Temperature
Reactor-001,Reactor,150.5,25.3,180.0
Pump-001,Pump,85.0,15.2,45.0
```

A sample file `sample_equipment_data.csv` is included in the project root.

## 📡 API Documentation

### Base URL
```
http://localhost:8000/api/
```

### Data Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/` | API root with available endpoints |
| POST | `/upload/` | Upload a CSV file |
| GET | `/history/` | Get last 5 uploaded datasets |
| GET | `/datasets/<id>/` | Get specific dataset details |
| DELETE | `/datasets/<id>/delete/` | Delete a dataset |
| POST | `/report/<id>/` | Generate PDF report (auth required) |
| GET | `/latest/` | Get the most recent dataset |

### Authentication Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/auth/register/` | Register new user (sends OTP) |
| POST | `/auth/verify-signup-otp/` | Verify signup OTP and activate account |
| POST | `/auth/login/` | Login with email/password (returns JWT) |
| POST | `/auth/request-password-reset/` | Request password reset OTP |
| POST | `/auth/verify-reset-otp/` | Verify password reset OTP |
| POST | `/auth/reset-password/` | Reset password with OTP |
| POST | `/auth/resend-otp/` | Resend OTP (for signup or password reset) |

### Authentication Flow

#### 1. Registration
```bash
POST /api/auth/register/
Content-Type: application/json

{
  "email": "user@example.com",
  "password": "SecurePass123!",
  "confirm_password": "SecurePass123!",
  "name": "John Doe"  # optional
}

# Response (201)
{
  "success": true,
  "message": "Account created successfully. Please check your email for verification code.",
  "otp_required": true,
  "email": "user@example.com"
}
```

#### 2. Verify Email OTP
```bash
POST /api/auth/verify-signup-otp/
Content-Type: application/json

{
  "email": "user@example.com",
  "otp": "123456"
}

# Response (200)
{
  "success": true,
  "message": "Email verified successfully. Your account is now active.",
  "user": { "id": 1, "email": "user@example.com", "name": "John Doe" },
  "tokens": {
    "access": "eyJ...",
    "refresh": "eyJ..."
  }
}
```

#### 3. Login
```bash
POST /api/auth/login/
Content-Type: application/json

{
  "email": "user@example.com",
  "password": "SecurePass123!"
}

# Response (200)
{
  "success": true,
  "message": "Login successful.",
  "user": { "id": 1, "email": "user@example.com", "name": "John Doe" },
  "tokens": {
    "access": "eyJ...",
    "refresh": "eyJ..."
  }
}
```

#### 4. Password Reset Flow
```bash
# Step 1: Request OTP
POST /api/auth/request-password-reset/
{ "email": "user@example.com" }

# Step 2: Verify OTP (optional)
POST /api/auth/verify-reset-otp/
{ "email": "user@example.com", "otp": "123456" }

# Step 3: Reset Password
POST /api/auth/reset-password/
{
  "email": "user@example.com",
  "otp": "123456",
  "new_password": "NewSecurePass123!",
  "confirm_new_password": "NewSecurePass123!"
}
```

### Environment Variables for SendGrid Email

Create a `.env` file in the `backend/` directory with these variables:

```env
# Django Secret Key
DJANGO_SECRET_KEY=your-super-secret-key-change-in-production

# SendGrid Configuration
EMAIL_HOST=smtp.sendgrid.net
EMAIL_PORT=587
EMAIL_HOST_USER=apikey
SENDGRID_API_KEY=your-sendgrid-api-key-here
EMAIL_USE_TLS=True
DEFAULT_FROM_EMAIL=noreply@yourdomain.com

# OTP Settings
OTP_EXPIRY_MINUTES=10
```

**Note:** Get your SendGrid API key from https://app.sendgrid.com/settings/api_keys

### Upload Response Example

```json
{
  "message": "File uploaded and processed successfully",
  "dataset_id": 1,
  "summary": {
    "total_equipment": 30,
    "avg_flowrate": 142.35,
    "avg_pressure": 15.67,
    "avg_temperature": 85.42,
    "type_distribution": {
      "Reactor": 2,
      "Pump": 3,
      "Heat Exchanger": 2
    }
  },
  "equipment_list": [...]
}
```

## 📸 Screenshots

### Web Application
- Dashboard with summary statistics
- Interactive Chart.js visualizations
- Data table with sortable columns
- Upload history sidebar

### Desktop Application
- PyQt5 native interface
- Matplotlib chart visualizations
- Integrated file browser
- PDF report generation dialog

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## � Deployment

### Deploy Backend to Render

1. **Create a new Web Service on Render:**
   - Go to https://render.com and create an account
   - Click "New" → "Web Service"
   - Connect your GitHub repository

2. **Configure the service:**
   - **Root Directory:** `backend`
   - **Build Command:** `pip install -r requirements.txt`
   - **Start Command:** `gunicorn backend.wsgi:application`

3. **Add Environment Variables on Render:**
   ```
   DJANGO_SECRET_KEY=<generate-a-secure-key>
   DEBUG=False
   ALLOWED_HOSTS=your-app-name.onrender.com
   CORS_ALLOWED_ORIGINS=https://your-frontend.vercel.app
   SENDGRID_API_KEY=<your-sendgrid-api-key>
   DEFAULT_FROM_EMAIL=noreply@yourdomain.com
   ```

4. **Add PostgreSQL Database:**
   - In Render dashboard, create a PostgreSQL database
   - Copy the "External Database URL"
   - Add `DATABASE_URL` environment variable

5. **Deploy and run migrations:**
   - After deploy, open Shell and run: `python manage.py migrate`

### Deploy Frontend to Vercel

1. **Create a new project on Vercel:**
   - Go to https://vercel.com and connect your GitHub
   - Import the repository

2. **Configure the project:**
   - **Root Directory:** `web-frontend`
   - **Build Command:** `npm run build`
   - **Output Directory:** `build`

3. **Add Environment Variables on Vercel:**
   ```
   REACT_APP_API_URL=https://your-backend.onrender.com/api
   ```

4. **Deploy:**
   - Click "Deploy" and wait for the build to complete

### Post-Deployment Checklist

- [ ] Backend is accessible at `https://your-app.onrender.com/api/`
- [ ] Frontend can communicate with backend (test file upload)
- [ ] CORS is properly configured
- [ ] Email OTP is working (check SendGrid logs)
- [ ] Database migrations are applied

## �📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

**Built with ❤️ for chemical engineers and data enthusiasts**