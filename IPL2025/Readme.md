# 🏏 IPL 2025 Bowler Dashboard

An interactive web application built with **Streamlit** to explore and compare IPL 2025 bowler statistics with powerful visualizations and analytics tools.

---

## 📌 Overview

The IPL 2025 Bowler Dashboard enables cricket analysts and fans to interactively explore key bowling metrics such as:

- Wickets taken
- Bowling pace (km/h)
- Dot ball and boundary ball efficiency
- Economy rate across different match phases (PP, MO, DO)
- Visual comparisons between bowlers

---

## 🚀 Features

✅ Filter bowlers by overs, wickets, pace, and economy  
✅ Top 5 disciplined bowlers by Dot/Boundary ratio  
✅ Advanced interactive charts:
- Area chart (Overs vs Wickets)
- Scatter & Bubble plots (Pace, Economy, Wickets)
- Donut chart (Wicket shares, Overs bowled)
- Treemap (Runs conceded)
✅ Phase-wise economy breakdown  
✅ Head-to-head bowler comparison with heatmaps and tables

---

## 🛠️ Tech Stack

| Layer        | Technology       |
|--------------|------------------|
| Frontend/UI  | Streamlit        |
| Data Source  | IPL 2025 CSV (GitHub) |
| Visualization| Plotly, Matplotlib, Seaborn |
| Backend      | Python 3.x, Pandas, NumPy |

---

## 📂 Project Structure

```bash
ipl-bowler-dashboard/
├── dashboard.py         # Main Streamlit app
├── requirements.txt     # Python dependencies
└── README.md            # This documentation
📥 Installation
🧰 Prerequisites
Python 3.8+

pip package manager

##🔧 Setup

### 📄 requirements.txt (Dependencies)
streamlit>=1.20
pandas>=1.5
numpy>=1.22
matplotlib>=3.5
seaborn>=0.11
scikit-learn>=1.0
plotly>=5.10

pip install streamlit pandas numpy matplotlib seaborn scikit-learn plotly


git clone https://github.com/yourusername/ipl-bowler-dashboard.git
cd ipl-bowler-dashboard
pip install -r requirements.txt

## ▶️ Run the App

streamlit run dashboard.py
Visit http://localhost:8501 in your browser to explore the dashboard.

## 📊 Data Source
The data is fetched live from:

https://raw.githubusercontent.com/kanadkapil/Data/main/IPL2025_BowlerData.csv
Fields include:

Bowler Name

Overs, Wickets, Pace (km/h)

Dot Ball %, Boundary %

Runs Conceded

Phase-wise Economy: Powerplay (PP), Middle Overs (MO), Death Overs (DO)

## 🧭 How to Use
## 🔍 Sidebar Filters
Minimum Overs: Filter out part-time bowlers

Minimum Wickets: Narrow to more effective bowlers

Pace Range: Set desired speed window (e.g., 130–145 km/h)

Max Economy: Limit to economical bowlers only

## 📌 Main Dashboard Sections
Section	Description
📋 Complete Bowler Dataset	Full sortable dataset view
🔥 Dot/Boundary Discipline	Top 5 based on dot-to-boundary ratio
📊 Advanced Visualizations	Interactive charts for exploration
🆚 Compare Bowlers Tool	Compare two bowlers visually/statistically

📈 Key Metrics Explained
Metric	Description
Economy_calc	Runs conceded / Overs
Dot/Boundary Ratio	Dot % divided by Boundary %
Phase-wise Economy	Runs per over during PP, MO, DO phases
Pace (km/h)	Average speed of bowler deliveries

🧪 Example Use Cases
🆚 Compare two death-over specialists for economy

🔍 Filter pacers above 140+ km/h with low boundary %

🔥 Identify top wicket-takers in middle overs

📊 Explore overall performance trends by visuals

🤝 Contributing
Contributions are welcome!


# Step 1: Fork the repo
# Step 2: Create your feature branch
git checkout -b feature-name

# Step 3: Commit and push your changes
git commit -m "Add new feature"
git push origin feature-name

# Step 4: Open a pull request
📄 License

🙋‍♂️ Author & Credits
👤 Kanad Kapil
GitHub: @kanadkapil

