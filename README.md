
# 🏥 Smart Health Prediction System

A **Flask-based web application** that predicts potential diseases based on user-selected symptoms using a **Random Forest** machine learning model. The interface is designed to resemble a professional hospital website, featuring **user authentication**, **symptom analysis**, and **profile management**.

---

## 🔍 Features

- 🔐 **User Authentication**: Register with username, password, full name, email, age, gender, height, and weight; log in securely.
- 🩺 **Symptom Checker**: Select symptoms and their severity (Mild, Moderate, Severe) to receive disease predictions with confidence scores.
- 👤 **Profile Page**: View user details (name, username, email, age, gender, height, weight).
- 💾 **Database**: Uses SQLite (`users.db`) to store user information.

---

## 🛠 Prerequisites

- Python: `3.8` – `3.12`
- SQLite: Optional (for inspecting the database)
- Web Browser: Chrome / Firefox / Edge
- Git: For cloning the repository

---

## 📥 Installation

### 1. Clone the Repository

```bash
git clone https://github.com/praveenh001/disease-prediction.git
```

### 2. Navigate into the Project Directory

```bash
cd disease-prediction
```

### 3. Set Up a Virtual Environment (Recommended)

```bash
python -m venv venv
```

#### Activate it:

- **Windows (PowerShell):**
  ```bash
  .\venv\Scripts\Activate.ps1
  ```

- **macOS/Linux:**
  ```bash
  source venv/bin/activate
  ```

### 4. Install Dependencies

```bash
pip install -r requirements.txt
```

#### `requirements.txt` content:
```
Flask==2.3.3  
pandas==2.2.2  
numpy==1.26.4  
scikit-learn==1.5.1  
werkzeug==3.0.3
```

---

## 🔧 Database Setup

Run this command once to initialize the database and launch the app:

```bash
python doctor.py
```

This creates a `users.db` file with a default user:

- Username: `testuser`
- Password: `password123`

---

## 🚀 Run the Application

```bash
python doctor.py
```

Then open your browser and visit:

```
http://127.0.0.1:5000/
```

---

## 📁 Directory Structure

```
disease-prediction/
├── doctor.py
├── requirements.txt
├── README.md
├── static/
│   ├── styles.css
│   └── images/
├── templates/
│   ├── home.html
│   ├── login.html
│   ├── profile.html
│   ├── symptoms.html
│   ├── results.html
└── users.db (auto-generated)
```

For bugs or suggestions, open an issue or email:  
📧 `praveenpuni80@gmail.com`  
🌐 GitHub: [@praveenh001](https://github.com/praveenh001)
