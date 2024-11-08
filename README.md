# Olist: E-Commerce Collection Dashboard
by Abdurrohman Ibnul Mufadlol

## Description

This project is a Data Analysis initiative on the Brazilian E-commerce dataset by Olist. The analysis results will be deployed into an interactive dashboard on the Streamlit platform.

This project includes a Jupyter Notebook for data analysis (`notebook.ipynb`), a deployed Streamlit dashboard (`url.txt`), and the main Streamlit app file (`dashboard/dashboard.py`). This README provides setup instructions for the environment and guidance on running the Jupyter Notebook and Streamlit dashboard.

## Setup Environment

1. **Create Project Folder and Virtual Environment**
   ```bash
   mkdir project_folder
   cd project_folder
   python -m venv venv
   ```

2. **Activate Virtual Environment**
   - **Windows**: 
     ```bash
     venv\Scripts\activate
     ```
   - **macOS/Linux**:
     ```bash
     source venv/bin/activate
     ```

3. **Install Required Packages**
   ```bash
   pip install -r requirements.txt
   ```

4. **Run Jupyter Notebook**
   ```bash
   jupyter notebook
   ```

## File Descriptions

- **`notebook.ipynb`**: The main Jupyter Notebook for data analysis. Run this notebook to explore the project's data and analyses.
- **`url.txt`**: Contains the URL link to the deployed Streamlit dashboard.
- **`dashboard/dashboard.py`**: The main Streamlit file for the dashboard. Run this file to view the dashboard locally.

## Running the Streamlit Dashboard

To run the Streamlit dashboard locally, use the following command:

```bash
streamlit run dashboard/dashboard.py
```

This command will start a local server for the dashboard. Open the link displayed in the terminal to view the dashboard.

## Prompt for Running Project Files

1. **To explore the data and analysis**: Open `notebook.ipynb` in Jupyter Notebook.
2. **To access the deployed dashboard**: Use the link in `url.txt`.
3. **To run the Streamlit dashboard locally**: Use `streamlit run dashboard/dashboard.py` in your terminal.

---

This README covers the setup and usage instructions for the project environment and main components.
