# 📊 Sales Performance Dashboard

An interactive **Sales Performance Dashboard** built with **Python** and **Streamlit** to analyze and visualize sales data.  
The project uses the `warehouse_and_retail_sales.csv` dataset to provide actionable insights into **monthly sales trends, department-level performance, and item movement**.

---

## 🚀 Features

- 📈 **Sales Trend Analysis** – Visualize monthly and yearly sales growth  
- 🏬 **Supplier Performance** – Identify top-performing and underperforming suppliers 
- 📦 **Item Movement Tracking** – Monitor product-level sales distribution  
- 🎯 **KPIs Dashboard** – Highlight total sales, average sales, top-selling items  
- ⚡ **Interactive Filters** – Drill down by year, supplier, item  

---

## 📂 Project Structure
sales-performance-dashboard/
│── data/
│ └── warehouse_and_retail_sales.csv # Raw and cleaned dataset (ignored in git)
│ └── sample.csv # Small sample for demo
│── visuals/
│ └── monthly_retail_sales_trend.png
│ └── retail_vs_warehouse.png.png
│ └── top_items.png.png
│ └── top_suppliers.png.png
│── streamlit_dashboard_app.py # Streamlit application
│── requirements.txt # Python dependencies
│── .gitignore # Ignore unnecessary files
│── README.md # Project documentation


---

## 🛠️ Installation & Setup

### 1. Clone the repository

git clone https://github.com/your-username/sales-performance-dashboard.git
cd sales-performance-dashboard

### 2. Create a virtual environment (optional but recommended)

python -m venv venv
# On Windows: 
venv\Scripts\activate

### 3. Install dependencies

pip install -r requirements.txt

### 4. Run the Streamlit app

streamlit run app.py

### 🔮 Future Improvements

Add forecasting module for future sales prediction

Integrate with SQL database for real-time data updates

Deploy the app on Streamlit Cloud / Heroku

🤝 Contributing

Pull requests are welcome! For major changes, please open an issue first to discuss what you’d like to improve.

📜 License

This project is licensed under the MIT License.