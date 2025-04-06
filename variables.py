import datetime

today = datetime.datetime.now()
current_year, current_week, _ = today.isocalendar()

trades = ["EUR-US","EUR-ANZ","EUR-FPI","US EX", "LATAM EX"]

csv_path = "vol_contrib_data.csv"