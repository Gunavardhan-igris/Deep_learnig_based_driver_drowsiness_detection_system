# Driver Drowsiness Detection System

A real-time driver drowsiness detection web application built with Django and deep learning models. This system uses computer vision and machine learning to detect signs of driver fatigue, including eye closure and yawning, to help prevent accidents caused by drowsy driving.

## Features

- **Real-time Detection**: Detects drowsy driving indicators in real-time using webcam feed
- **Multiple Detection Models**: Supports various CNN and Vision Transformer models for accurate detection
- **User Management**: Separate authentication for Autoist (drivers) and Admin users
- **Detection History**: Stores and displays detection history for each user
- **Web Interface**: Intuitive web-based interface for easy access and monitoring
- **Face Detection**: Uses Haar Cascade classifiers for robust face and eye detection

## Project Structure

- **admins/** - Admin panel and management functionality
- **users/** - User/Autoist management and authentication
- **assets/** - Static files (CSS, JavaScript, images)
- **media/** - Trained models and Haar cascade files
- **DriverDrowsiness/** - Django project configuration

## Prerequisites

- Python 3.7+
- pip (Python package manager)
- Webcam (for detection)

## Installation

### 1. Clone the Repository
```bash
git clone <repository-url>
cd DriverDrowsiness
```

### 2. Create a Virtual Environment
```bash
python -m venv venv
source venv/Scripts/activate  # On Windows
# OR
source venv/bin/activate  # On macOS/Linux
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

### 4. Database Setup
```bash
python manage.py migrate
python manage.py createsuperuser
```

### 5. Collect Static Files (Optional)
```bash
python manage.py collectstatic
```

## Running the Application

```bash
python manage.py runserver
```

The application will be available at `http://127.0.0.1:8000/`

### Default Access Points
- **Admin Login**: `/admin/login`
- **Autoist Login**: `/autoist/login`
- **Autoist Registration**: `/autoist/register`

## Usage

1. **Register** as an Autoist or login with existing credentials
2. **Start Detection** from the dashboard
3. **View Results** in your detection history
4. **Admins** can view registered users and their detection records

## Technology Stack

- **Backend**: Django
- **Frontend**: HTML, CSS, JavaScript, Bootstrap
- **ML Models**: TensorFlow/Keras (CNN, Vision Transformer)
- **Computer Vision**: OpenCV, dlib, Haar Cascade
- **Database**: SQLite

## Models Available

- `best_model.h5` - Primary CNN model
- `cnnCat2.h5` - CNN classifier
- `Dp_hybrid_final.h5` - Hybrid model
- `Dp_vitCat2.h5` - Vision Transformer variant

## License

This project is for educational and research purposes.
