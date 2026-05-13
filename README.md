# Hybrid GNN-RF Software Vulnerability Detection

A hybrid deep learning and machine learning based system for detecting software vulnerabilities using **Graph Neural Networks (GNNs)** and **Random Forest (RF)** classifiers.

---

## 📌 Project Overview

Modern software systems contain complex code structures and dependencies, making traditional vulnerability detection methods less effective. This project introduces a hybrid approach that:

- Converts source code into graph representations such as:
  - Abstract Syntax Trees (AST)
  - Control Flow Graphs (CFG)
  - Program Dependency Graphs (PDG)
- Uses a **Graph Neural Network (GNN)** to learn structural and semantic relationships in code
- Uses a **Random Forest classifier** for final vulnerability classification
- Detects vulnerabilities such as:
  - SQL Injection
  - JavaScript Vulnerabilities
  - Other malicious code patterns

The system is designed for scalable and intelligent vulnerability analysis in large software codebases.

---

# 🚀 Features

- 🔍 Automated software vulnerability detection
- 🧠 Graph Neural Network based feature extraction
- 🌲 Random Forest based classification
- 📊 TF-IDF preprocessing for code tokenization
- 📈 Evaluation metrics visualization
- 🌐 Web interface for uploading and testing source code
- 🔐 Role-Based Access Control (RBAC)
- 📁 Vulnerability logging and storage support

---

# 🏗️ System Architecture

The project follows a hybrid layered architecture:

1. Data Collection  
2. Graph Construction & Feature Extraction  
3. GNN-Based Structural Learning  
4. Random Forest Classification  
5. Vulnerability Detection  
6. Alert & Logging System  

---

# 🛠️ Technologies Used

## Programming Languages
- Python

## Frameworks & Libraries
- PyTorch
- PyTorch Geometric
- Scikit-learn
- Flask / Django
- TensorFlow
- NetworkX
- DGL (Deep Graph Library)
- Pandas
- NumPy
- Matplotlib
- Seaborn

## Database
- PostgreSQL

---

# 📂 Project Workflow

```text
Source Code Upload
        ↓
Code Preprocessing
        ↓
Graph Generation (AST/CFG/PDG)
        ↓
Feature Extraction
        ↓
Graph Neural Network (GNN)
        ↓
Random Forest Classification
        ↓
Vulnerability Detection
        ↓
Security Alerts & Logs
```

---

# 📊 Machine Learning Models

## Graph Neural Network (GNN)
Used for:
- Structural code understanding
- Dependency analysis
- Semantic feature extraction

## Random Forest (RF)
Used for:
- Final vulnerability classification
- Improved robustness
- Reduced false positives

---

# 📈 Evaluation Metrics

The system evaluates model performance using:

- Accuracy
- Precision
- Recall
- F1-Score
- Confusion Matrix

---

# 💻 Hardware Requirements

- Intel i7 Processor or higher
- Minimum 16GB RAM
- 100GB SSD Storage
- NVIDIA RTX GPU (recommended for GNN training)

---

# ⚙️ Installation

## 1️⃣ Clone the Repository

```bash
git clone https://github.com/your-username/software-vulnerability-detection.git

cd software-vulnerability-detection
```

## 2️⃣ Create Virtual Environment

```bash
python -m venv venv
```

## 3️⃣ Activate Virtual Environment

### Windows
```bash
venv\Scripts\activate
```

### Linux / Mac
```bash
source venv/bin/activate
```

## 4️⃣ Install Dependencies

```bash
pip install -r requirements.txt
```

## 5️⃣ Run the Project

```bash
python manage.py runserver
```

or

```bash
python app.py
```

---

# 📁 Dataset

The project can work with:
- Custom vulnerability datasets
- Public vulnerability datasets
- Open-source repositories

Example vulnerabilities include:
- SQL Injection
- Code Injection
- Unsafe API Usage
- Malicious Scripts

---

# 🧪 Testing

The project includes:
- Unit Testing
- Integration Testing
- Functional Testing

---

# 📷 Sample Outputs

- Vulnerability Prediction Dashboard
- Uploaded Source Code Analysis
- Attack Prediction Results
- Confusion Matrix Visualization

---

# 🔮 Future Enhancements

- Real-time vulnerability monitoring
- Support for multiple programming languages
- Transformer-based vulnerability detection
- Cloud deployment integration
- CI/CD security pipeline integration

---

# 👨‍💻 Author

**Pathuri Rama Krishna**  
B.Tech – Computer Science & Engineering (Cyber Security)  
Institute of Aeronautical Engineering, Hyderabad

---

# 📜 License

This project is intended for academic and research purposes only.

---

# ⭐ Acknowledgement

Special thanks to the Department of CSE (Cyber Security), Institute of Aeronautical Engineering, Hyderabad, for guidance and support throughout the project development.
