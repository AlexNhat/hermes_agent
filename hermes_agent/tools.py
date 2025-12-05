import pandas as pd
from datetime import timedelta

# load once when the module starts
try:
    df = pd.read_csv("data/shipments.csv", parse_dates=["date"])
except Exception:
    df = pd.DataFrame()





#
def route_with_biggest_delay_last_week() -> dict:
    """
    Returns the route with the largest total delay in the last 7 days.
    """
    if df.empty:
        return {"message": "No shipment data available"}

    end = df["date"].max()
    start = end - timedelta(days=7)

    week_data = df[
        (df["date"] > start) &
        (df["date"] <= end) &
        (df["delay_minutes"] > 0)
    ]

    if week_data.empty:
        return {"message": "No delayed shipments in the last week"}

    agg = (
        week_data.groupby("route")["delay_minutes"]
        .sum()
        .sort_values(ascending=False)
    )

    top = agg.index[0]
    total = int(agg.iloc[0])

    return {
        "route": top,
        "total_delay_minutes": total,
        "from": start.date().isoformat(),
        "to": end.date().isoformat()
    }

#-----------------------------------------------

def delay_stats_by_reason() -> dict:
    """
    Simple breakdown of delay counts by reason.
    """
    d = df[df["delay_minutes"] > 0]
    if d.empty:
        return {"message": "No delays found"}

    result = (
        d.groupby("delay_reason")["id"]
        .count()
        .sort_values(ascending=False)
        .to_dict()
    )
    return {"delay_by_reason": result}


#------------------------------------------------
def warehouses_over_delivery(threshold: float = 5.0) -> dict:
    """
    Warehouses that exceed the given average delivery time.
    """
    if df.empty:
        return {"message": "No data"}

    avg = df.groupby("warehouse")["delivery_time"].mean()
    over = avg[avg > threshold]

    if over.empty:
        return {"message": f"No warehouse above {threshold} days"}

    return {"threshold": threshold, "warehouses": over.to_dict()}

#------------------------------------------------
def top3_warehouses_by_processing() -> dict:
    """
    Top 3 warehouses with the highest avg delivery time.
    """
    if df.empty:
        return {"message": "No data"}

    avg = df.groupby("warehouse")["delivery_time"].mean()
    top3 = avg.sort_values(ascending=False).head(3)

    return {"top3": top3.to_dict()}


def monthly_avg_delay(year: int, month: int) -> dict:
    """
    Average delay for a specific month.
    """
    m = df[
        (df["date"].dt.year == year) &
        (df["date"].dt.month == month)
    ]

    if m.empty:
        return {"message": f"No data for {month}/{year}"}

    return {
        "year": year,
        "month": month,
        "average_delay": float(m["delay_minutes"].mean())
    }


def predict_next_week_delay(window_weeks: int = 4) -> dict:
    """
    Naive prediction: moving average of recent weeks.
    """
    if df.empty:
        return {"message": "Not enough data"}

    tmp = df.copy()
    tmp["week_start"] = tmp["date"].dt.to_period("W").apply(lambda r: r.start_time)
    weekly = tmp.groupby("week_start")["delay_minutes"].mean().sort_index()

    if weekly.empty:
        return {"message": "No weekly data"}

    recent = weekly.tail(window_weeks)
    pred = float(recent.mean())

    return {
        "method": f"moving_avg_{len(recent)}w",
        "prediction": pred,
        "used_weeks": {str(k.date()): float(v) for k, v in recent.items()}
    }
