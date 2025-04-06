import datetime

today = datetime.datetime.now()
current_year, current_week, _ = today.isocalendar()

trades = ["EUR-US","EUR-ANZ","EUR-FPI","US EX", "LATAM EX"]

csv_path = "vol_contrib_data.csv"

equipment_colors = ["#7886C7", "#006A71", "#48A6A7", "#9ACBD0", "#F2EFE7", "#98D2C0"]