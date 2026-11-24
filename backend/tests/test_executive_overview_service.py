"""Tests for executive overview service and metrics aggregation."""
import pytest
from datetime import date, datetime, timedelta, timezone
from app.services.executive_overview_service import ExecutiveOverviewService
from app.repositories.executive_metrics_repository import ExecutiveMetricsRepository
from app.models.executive_metrics import ExecutiveDailyMetric
from app.models.exception_case import ExceptionCase
from app.models.approval import ApprovalDecision
from app.models.user import User


def test_get_overview_metrics_with_data(db_session):
    """Test executive overview metrics aggregation over date range with persisted daily metrics."""
    # Seed test data
    repo = ExecutiveMetricsRepository(db_session)
    today = date.today()
    
    # Create 3 days of metrics
    for day_offset in range(3):
        metric_date = today - timedelta(days=day_offset)
        repo.aggregate_daily(
            metric_date=metric_date,
            station_code="DXB",
            open_case_count=5,
            urgent_case_count=2,
            recovered_before_departure_count=4,
            impacted_passenger_count=12,
            stale_data_case_count=1
        )
    
    # Test overview service
    service = ExecutiveOverviewService(db_session)
    from_date = today - timedelta(days=2)
    to_date = today
    
    overview = service.get_overview_metrics(from_date, to_date, "DXB")
    
    assert overview is not None
    assert "kpis" in overview
    assert "trend_data" in overview
    assert "generated_at" in overview
    assert "freshness_status" in overview
    
    # Verify KPIs exist
    kpis = overview["kpis"]
    assert len(kpis) == 7
    
    kpi_codes = [kpi["metric_code"] for kpi in kpis]
    assert "exception_rate" in kpi_codes
    assert "recovered_within_cutoff" in kpi_codes
    assert "mean_time_to_decision" in kpi_codes
    assert "passengers_impacted" in kpi_codes
    assert "open_cases" in kpi_codes
    assert "open_case_ageing" in kpi_codes
    assert "stale_data_cases" in kpi_codes
    
    # Verify trend data
    trend = overview["trend_data"]
    assert len(trend["dates"]) == 3
    assert len(trend["exception_rate_per_1000"]) == 3
    assert len(trend["recovered_within_cutoff_pct"]) == 3
    assert len(trend["passengers_impacted"]) == 3
    assert len(trend["open_case_count"]) == 3
    assert len(trend["stale_data_case_count"]) == 3


def test_get_overview_metrics_no_data(db_session):
    """Test executive overview when no metrics exist for date range."""
    service = ExecutiveOverviewService(db_session)
    from_date = date.today() - timedelta(days=10)
    to_date = date.today() - timedelta(days=5)
    
    overview = service.get_overview_metrics(from_date, to_date, "DXB")
    
    assert overview["kpis"] == []
    assert overview["trend_data"]["exception_rate_per_1000"] == []
    assert overview["freshness_status"] == "no_data"


def test_kpi_calculation_recovered_percentage(db_session):
    """Test recovered within cutoff percentage KPI calculation."""
    repo = ExecutiveMetricsRepository(db_session)
    today = date.today()
    
    # 10 open cases, 7 recovered (70% recovery rate)
    repo.aggregate_daily(
        metric_date=today,
        station_code="DXB",
        open_case_count=10,
        urgent_case_count=3,
        recovered_before_departure_count=7,
        impacted_passenger_count=20,
        stale_data_case_count=2
    )
    
    service = ExecutiveOverviewService(db_session)
    overview = service.get_overview_metrics(today, today, "DXB")
    
    # Find recovered KPI
    recovered_kpi = next(kpi for kpi in overview["kpis"] if kpi["metric_code"] == "recovered_within_cutoff")
    assert recovered_kpi["current_value"] == 70.0  # 7/10 * 100 = 70%


def test_kpi_calculation_exception_rate(db_session):
    """Test exception rate per 1000 bags KPI calculation."""
    repo = ExecutiveMetricsRepository(db_session)
    today = date.today()
    
    # 5 cases per day, assuming 1000 bags/day → 5/1000 * 1000 = 5.0 per 1000
    repo.aggregate_daily(
        metric_date=today,
        station_code="DXB",
        open_case_count=5,
        urgent_case_count=2,
        recovered_before_departure_count=3,
        impacted_passenger_count=10,
        stale_data_case_count=1
    )
    
    service = ExecutiveOverviewService(db_session)
    overview = service.get_overview_metrics(today, today, "DXB")
    
    # Find exception rate KPI
    exception_kpi = next(kpi for kpi in overview["kpis"] if kpi["metric_code"] == "exception_rate")
    assert exception_kpi["current_value"] == 5.0  # 5 cases per 1000 bags


def test_mean_decision_time_calculation(db_session):
    """Test mean time to decision calculation from approval decisions."""
    # Create test user
    user = User(
        id="user-test-1",
        external_subject="test@example.com",
        role_code="operations",
        display_name="Test User",
        active_flag=True,
        created_at=datetime.now(timezone.utc),
        updated_at=datetime.now(timezone.utc)
    )
    db_session.add(user)
    
    # Create test case
    now = datetime.now(timezone.utc)
    case = ExceptionCase(
        id="case-test-1",
        case_reference="TEST-001",
        exception_type="short_connection_risk",
        severity_code="high",
        deadline_at=now + timedelta(hours=2),
        status_code="open",
        observed_state_summary="Test case",
        predicted_state_summary="Test prediction",
        created_by_user_id=user.id,
        created_at=now - timedelta(minutes=20),  # Case created 20 minutes ago
        updated_at=now - timedelta(minutes=20)
    )
    db_session.add(case)
    
    # Create approval decision 10 minutes after case creation
    approval = ApprovalDecision(
        id="approval-test-1",
        case_id=case.id,
        recommendation_id="rec-test-1",
        decided_by_user_id=user.id,
        decision_code="approved",
        rationale_text="Test approval",
        decided_at=now - timedelta(minutes=10),  # Decision 10 minutes after case
        decision_version=1
    )
    db_session.add(approval)
    db_session.commit()
    
    # Seed daily metric for today
    repo = ExecutiveMetricsRepository(db_session)
    repo.aggregate_daily(
        metric_date=date.today(),
        station_code="DXB",
        open_case_count=1,
        urgent_case_count=1,
        recovered_before_departure_count=0,
        impacted_passenger_count=5,
        stale_data_case_count=0
    )
    
    # Test service
    service = ExecutiveOverviewService(db_session)
    overview = service.get_overview_metrics(date.today(), date.today(), "DXB")
    
    # Find mean decision time KPI - should be 10 minutes
    decision_kpi = next(kpi for kpi in overview["kpis"] if kpi["metric_code"] == "mean_time_to_decision")
    assert decision_kpi["current_value"] == 10.0


def test_open_case_ageing_calculation(db_session):
    """Test open case ageing calculation."""
    # Create test user
    user = User(
        id="user-ageing-1",
        external_subject="test@example.com",
        role_code="operations",
        display_name="Test User",
        active_flag=True,
        created_at=datetime.now(timezone.utc),
        updated_at=datetime.now(timezone.utc)
    )
    db_session.add(user)
    
    # Create open case that's 3 hours old
    now = datetime.now(timezone.utc)
    case = ExceptionCase(
        id="case-ageing-1",
        case_reference="AGEING-001",
        exception_type="short_connection_risk",
        severity_code="high",
        deadline_at=now + timedelta(hours=2),
        status_code="open",
        observed_state_summary="Test case",
        predicted_state_summary="Test prediction",
        created_by_user_id=user.id,
        created_at=now - timedelta(hours=3),
        updated_at=now - timedelta(hours=3)
    )
    db_session.add(case)
    db_session.commit()
    
    # Seed daily metric
    repo = ExecutiveMetricsRepository(db_session)
    repo.aggregate_daily(
        metric_date=date.today(),
        station_code="DXB",
        open_case_count=1,
        urgent_case_count=1,
        recovered_before_departure_count=0,
        impacted_passenger_count=5,
        stale_data_case_count=0
    )
    
    # Test service
    service = ExecutiveOverviewService(db_session)
    overview = service.get_overview_metrics(date.today(), date.today(), "DXB")
    
    # Find open case ageing KPI - should be 3.0 hours
    ageing_kpi = next(kpi for kpi in overview["kpis"] if kpi["metric_code"] == "open_case_ageing")
    assert ageing_kpi["current_value"] == 3.0


def test_freshness_status_mixed_with_stale_data(db_session):
    """Test freshness status when stale data cases exist."""
    repo = ExecutiveMetricsRepository(db_session)
    today = date.today()
    
    # Metric with stale data cases
    repo.aggregate_daily(
        metric_date=today,
        station_code="DXB",
        open_case_count=5,
        urgent_case_count=2,
        recovered_before_departure_count=3,
        impacted_passenger_count=10,
        stale_data_case_count=2  # 2 stale sources
    )
    
    service = ExecutiveOverviewService(db_session)
    overview = service.get_overview_metrics(today, today, "DXB")
    
    assert overview["freshness_status"] == "mixed"


def test_freshness_status_fresh_with_no_stale_data(db_session):
    """Test freshness status when no stale data cases exist."""
    repo = ExecutiveMetricsRepository(db_session)
    today = date.today()
    
    # Metric with no stale data
    repo.aggregate_daily(
        metric_date=today,
        station_code="DXB",
        open_case_count=5,
        urgent_case_count=2,
        recovered_before_departure_count=4,
        impacted_passenger_count=10,
        stale_data_case_count=0  # No stale sources
    )
    
    service = ExecutiveOverviewService(db_session)
    overview = service.get_overview_metrics(today, today, "DXB")
    
    assert overview["freshness_status"] == "fresh"
