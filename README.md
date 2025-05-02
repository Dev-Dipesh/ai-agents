# 📘 Jupyter Notebook Project Template (with venv)

A starter template for data projects using Jupyter Notebooks in VS Code, with a Python virtual environment.

---

## 🛠️ Setup Instructions (macOS / Linux)

### 1. 🔧 Create the Virtual Environment

In your terminal, run:

```bash
python3 -m venv venv
```

This creates a folder named `venv/` containing the isolated Python environment.

---

### 2. ▶️ Activate the Virtual Environment

```bash
source venv/bin/activate
```

You should see `(venv)` at the beginning of your terminal prompt.

---

### 3. 📦 Install Dependencies and Register Kernel

Run the setup script:

```bash
chmod +x setup_env.sh
./setup_env.sh
```

This will:

- Install packages from `requirements.txt`
- Register the environment as a Jupyter kernel named `Python (venv)`

---

### 4. 🧪 Use in VS Code

1. Open your `.ipynb` file (e.g., `notebooks/example.ipynb`)
2. In the top-right corner, click the **kernel picker**
3. Choose `Python (venv)` from the list

---

## 💡 Notes

- Add new packages via `pip install package_name`
- Update `requirements.txt` with:

  ```bash
  pip freeze > requirements.txt
  ```

- Reactivate the environment each time you open a new terminal:

  ```bash
  source venv/bin/activate
  ```

---

## 📁 Folder Structure

```
.
├── venv/                  # Virtual environment
├── notebooks/             # Jupyter notebooks
│   └── example.ipynb
├── data/                  # (Optional) datasets
├── requirements.txt       # Dependency list
├── setup_env.sh           # Setup script for macOS/Linux
└── README.md              # This file
```

---

Happy coding! 🚀
