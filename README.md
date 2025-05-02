# 🤖 AI Agents Collection

A repository of intelligent AI agents for various practical applications.

---

## 🌟 Featured Agents

### 📊 Finance Research Agent
An advanced agent for investment analysis and financial research that:
- Breaks down complex investment questions into detailed research plans
- Dynamically adjusts research based on gathered information
- Provides formatted, visual output suitable for client presentations
- Found in: `notebooks/finance_research_agent.ipynb`

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

### 4. 🧪 Use the Notebooks

1. Open a notebook file (e.g., `notebooks/finance_research_agent.ipynb`)
2. In the top-right corner, click the **kernel picker**
3. Choose `Python (venv)` from the list
4. Follow the instructions in the notebook to run the agent

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
│   └── finance_research_agent.ipynb
├── data/                  # Datasets used by agents
├── requirements.txt       # Dependency list
├── setup_env.sh           # Setup script for macOS/Linux
└── README.md              # This file
```

---

## 🔒 License

This project is licensed under the MIT License - see the LICENSE file for details.

---

Happy agent building! 🚀
