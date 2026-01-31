# 🌍 Real-Time Sales Analytics Dashboard

An **interactive Streamlit dashboard** visualizing global retail sales data. The app shows key metrics, top products, and customer insights in **real-time cumulative analytics**.  

---

## **Features**

- **KPIs:** Revenue, Units Sold, Orders, Active Countries, Unique Customers, Average Order Value  
- **Charts:**  
  - Revenue by Country (Pie)  
  - Top 5 Products by Units Sold & Revenue (Bar)  
  - Orders per Country (Bubble)  
  - Unique Customers per Country (Heatmap)  
  - Revenue Over Time (Line)  
- **Interactive Dashboard:** Hover for details, adjustable stream speed, reset button.  

---

## **Simulated Real-Time Data**

The dashboard **simulates the real-time arrival of sales transactions**:  

- **Data Preprocessing:** Each new data point is **validated and cleaned** using functions in `engine/processor.py`.  
- **Error Handling:** Missing or invalid entries are automatically removed.  
- **Cumulative Analytics:** All charts and KPIs reflect **data accumulated from the beginning**, updating dynamically as new points arrive.  

---

## **Tech Stack**

- Python, Pandas, Seaborn, Altair, Streamlit  

---

## **Run Locally**

```bash
git clone https://github.com/<username>/real-time-sales-dashboard.git
cd real-time-sales-dashboard
pip install -r requirements.txt
streamlit run app.py
'''
