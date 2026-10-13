# ⚽ Football Player Performance Analytics Dashboard

An interactive football analytics dashboard built with Streamlit and Plotly, offering rich visualisations of player performance metrics across positions, teams, and seasons. Explore KPI summaries, compare players head-to-head, and drill into team and position-level statistics — all powered by a synthetically generated dataset of 200 players.

> ⚠️ **Synthetic Data Notice:** All player statistics in this dashboard are synthetically generated for demonstration purposes only. They do not represent real football players, clubs, or match results.

---

## Features

- **Overview KPI cards** — at-a-glance summary of key metrics (goals, assists, pass accuracy, and more)
- **Player comparison & scatter plots** — compare any two players side-by-side, with interactive scatter charts for any two numeric metrics
- **Team analysis charts** — bar and grouped charts breaking down team-level averages and totals
- **Position analysis** — donut charts, box plots, and radar charts for position-based performance profiling
- **Sidebar filters** — filter by season, team, position, and individual player to scope every chart simultaneously
- **Searchable player statistics table** — sortable, searchable full data table for deep inspection
- **CSV download button** — export the currently filtered dataset with a single click
- **Dark modern football-inspired UI** — custom dark/green theme configured via `.streamlit/config.toml`
- **Responsive Plotly charts with tooltips** — fully interactive charts that adapt to any screen width
- **Input validation and error handling** — graceful handling of empty filter results and edge cases

---

## Project Structure

```
football-analytics-dashboard/
├── app.py                    # Main Streamlit application
├── football_players.csv      # Synthetic dataset (200 players)
├── requirements.txt          # Python dependencies
├── README.md                 # This file
├── generate_dataset.py       # Script to regenerate the dataset
└── .streamlit/
    └── config.toml           # Dark/green theme configuration
```

---

## Prerequisites

- Python **3.10** or higher
- **pip**

---

## Run Locally

1. **Clone the repository**
   ```bash
   git clone <your-repo-url>
   ```

2. **Change into the project directory**
   ```bash
   cd football-analytics-dashboard
   ```

3. **(Optional) Create and activate a virtual environment**
   ```bash
   python -m venv venv
   # macOS / Linux
   source venv/bin/activate
   # Windows
   venv\Scripts\activate
   ```

4. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

5. **Run the app**
   ```bash
   streamlit run app.py
   ```

6. **Open your browser** and navigate to `http://localhost:8501`

---

## Deploy to Streamlit Community Cloud

1. Push your project to a **public GitHub repository**.
2. Visit [share.streamlit.io](https://share.streamlit.io) and sign in with GitHub.
3. Click **"New app"**, then select your repository and branch.
4. Set the **main file path** to `app.py`.
5. Click **"Deploy!"** — your app will be live in seconds.

---

## Tech Stack

| Technology | Purpose |
|------------|---------|
| **Python** | Core language (3.10+) |
| **Streamlit** | Web app framework & UI |
| **Pandas** | Data loading & manipulation |
| **NumPy** | Numerical computations |
| **Plotly** | Interactive charts & visualisations |

---

## License

MIT
