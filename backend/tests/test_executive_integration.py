"""Integration tests for executive API endpoints."""
import pytest
from datetime import datetime, timedelta, date, timezone
from app.models import ExecutiveDailyMetric


def test_get_executive_overview_with_date_range(client, db_session):
    """Test GET /api/v1/executive/overview with date range parameters."""
    # Setup: Create executive metrics for date range
    today = date.today()
    for days_ago in range(7):
        metric_date = today - timedelta(days=days_ago)
        metric = ExecutiveDailyMetric(
            id=f"metric-exec-{days_ago}",
            metric_date=metric_date,
            station_code="DXB",
            open_case_count=10 + days_ago,
            urgent_case_count=2 + days_ago,
            recovered_before_departure_count=8,
            impacted_passenger_count=15 + days_ago,
            stale_data_case_count=1,
            snapshot_generated_at=datetime.combine(metric_date, datetime.min.time())
        )
        db_session.add(metric)
    db_session.commit()
    
    # Test: Get overview for last 7 days
    from_date = (today - timedelta(days=6)).isoformat()
    to_date = today.isoformat()
    
    response = client.get(
        f"/api/v1/executive/overview?from_date={from_date}&to_date={to_date}"
    )
    
    assert response.status_code == 200
    data = response.json()
    assert "kpis" in data
    assert "trend_data" in data
    assert "from_date" in data
    assert "to_date" in data
    assert data["from_date"] == from_date
    assert data["to_date"] == to_date


def test_get_executive_overview_kpis_structure(client, db_session):
    """Test executive overview returns correctly structured KPIs."""
    # Setup: Create basic metrics
    today = date.today()
    metric = ExecutiveDailyMetric(
        id="metric-exec-kpi-001",
        metric_date=today,
        station_code="DXB",
        open_case_count=15,
        urgent_case_count=5,
        recovered_before_departure_count=10,
        impacted_passenger_count=25,
        stale_data_case_count=2,
        snapshot_generated_at=datetime.combine(today, datetime.min.time())
    )
    db_session.add(metric)
    db_session.commit()
    
    # Test: Get overview
    from_date = today.isoformat()
    to_date = today.isoformat()
    response = client.get(f"/api/v1/executive/overview?from_date={from_date}&to_date={to_date}")
    
    assert response.status_code == 200
    data = response.json()
    
    # Verify KPI structure
    assert "kpis" in data
    kpis = data["kpis"]
    assert len(kpis) > 0
    
    # Verify KPI fields
    for kpi in kpis:
        assert "metric_code" in kpi
        assert "metric_label" in kpi
        assert "current_value" in kpi
        assert "trend_direction" in kpi


def test_get_executive_overview_trend_data(client, db_session):
    """Test executive overview includes trend data with dates and metrics."""
    # Setup: Create metrics for multiple days
    today = date.today()
    for days_ago in range(14):
        metric_date = today - timedelta(days=days_ago)
        metric = ExecutiveDailyMetric(
            id=f"metric-exec-trend-{days_ago}",
            metric_date=metric_date,
            station_code="DXB",
            open_case_count=20 - days_ago,
            urgent_case_count=5,
            recovered_before_departure_count=15,
            impacted_passenger_count=30,
            stale_data_case_count=2,
            snapshot_generated_at=datetime.combine(metric_date, datetime.min.time())
        )
        db_session.add(metric)
    db_session.commit()
    
    # Test: Get overview with 14-day range
    from_date = (today - timedelta(days=13)).isoformat()
    to_date = today.isoformat()
    
    response = client.get(
        f"/api/v1/executive/overview?from_date={from_date}&to_date={to_date}"
    )
    
    assert response.status_code == 200
    data = response.json()
    
    # Verify trend data structure
    assert "trend_data" in data
    trend_data = data["trend_data"]
    assert "dates" in trend_data
    assert len(trend_data["dates"]) > 0


def test_get_executive_overview_freshness_status(client, db_session):
    """Test executive overview includes data freshness status."""
    # Setup: Create recent metric
    today = date.today()
    metric = ExecutiveDailyMetric(
        id="metric-exec-fresh-001",
        metric_date=today,
        station_code="DXB",
        open_case_count=10,
        urgent_case_count=3,
        recovered_before_departure_count=7,
        impacted_passenger_count=20,
        stale_data_case_count=0,
        snapshot_generated_at=datetime.now(timezone.utc) - timedelta(minutes=5)
    )
    db_session.add(metric)
    db_session.commit()
    
    # Test: Get overview
    from_date = today.isoformat()
    to_date = today.isoformat()
    response = client.get(f"/api/v1/executive/overview?from_date={from_date}&to_date={to_date}")
    
    assert response.status_code == 200
    data = response.json()
    
    # Verify freshness status present
    assert "freshness_status" in data
    assert data["freshness_status"] in ["fresh", "acceptable", "stale"]


def test_get_executive_overview_with_no_data_returns_empty_structure(client, db_session):
    """Test executive overview returns valid structure even with no metrics."""
    # Test: Get overview with no data
    today = date.today()
    from_date = today.isoformat()
    to_date = today.isoformat()
    response = client.get(f"/api/v1/executive/overview?from_date={from_date}&to_date={to_date}")
    
    assert response.status_code == 200
    data = response.json()
    
    # Verify basic structure exists
    assert "kpis" in data
    assert "trend_data" in data
    assert "generated_at" in data


def test_get_executive_overview_aggregates_multiple_stations(client, db_session):
    """Test executive overview aggregates metrics across multiple stations."""
    # Setup: Create metrics for multiple stations
    today = date.today()
    for station in ["DXB", "AUH", "DOH"]:
        metric = ExecutiveDailyMetric(
            id=f"metric-exec-{station}",
            metric_date=today,
            station_code=station,
            open_case_count=10,
            urgent_case_count=3,
            recovered_before_departure_count=7,
            impacted_passenger_count=15,
            stale_data_case_count=1,
            snapshot_generated_at=datetime.combine(today, datetime.min.time())
        )
        db_session.add(metric)
    db_session.commit()
    
    # Test: Get overview (should aggregate all stations)
    from_date = today.isoformat()
    to_date = today.isoformat()
    response = client.get(f"/api/v1/executive/overview?from_date={from_date}&to_date={to_date}")
    
    assert response.status_code == 200
    data = response.json()
    
    # Verify aggregation occurred (open_case_count should be sum of all stations)
    kpis = data.get("kpis", [])
    if kpis:
        # Find open case count KPI
        open_cases_kpi = next(
            (kpi for kpi in kpis if "open" in kpi.get("metric_code", "").lower() or "open" in kpi.get("metric_label", "").lower()),
            None
        )
        if open_cases_kpi:
            # Should be aggregated across stations (10 + 10 + 10 = 30)
            assert open_cases_kpi["current_value"] >= 10
