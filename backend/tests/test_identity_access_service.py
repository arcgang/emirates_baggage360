"""Tests for IdentityAccessService covering role evaluation, partner scoping, and 403 enforcement."""
import pytest
from app.services.identity_access_service import IdentityAccessService


@pytest.fixture
def service():
    """Fixture providing IdentityAccessService instance."""
    return IdentityAccessService()


def test_resolve_principal_extracts_jwt_payload(service):
    """Test that resolve_principal extracts user context from JWT payload."""
    jwt_payload = {
        "sub": "00000000-0000-0000-0000-000000000001",
        "role": "operations",
        "display_name": "Mariam Al Suwaidi",
        "station_scope": "DXB",
    }
    
    principal = service.resolve_principal(jwt_payload)
    
    assert principal["user_id"] == "00000000-0000-0000-0000-000000000001"
    assert principal["role"] == "operations"
    assert principal["display_name"] == "Mariam Al Suwaidi"
    assert principal["station_scope"] == "DXB"


def test_role_evaluation_returns_role_code(service):
    """Test that role_evaluation returns the principal's role."""
    principal = {"role": "partner", "user_id": "user-123"}
    
    role = service.role_evaluation(principal)
    
    assert role == "partner"


def test_permitted_scopes_for_operations_role(service):
    """Test that operations role gets full operational permissions."""
    principal = {"role": "operations", "station_scope": "DXB"}
    
    scopes = service.permitted_scopes(principal)
    
    assert "full_operational_case_visibility" in scopes
    assert "approve_recommendations" in scopes
    assert "view_audit_trail" in scopes


def test_permitted_scopes_for_partner_role(service):
    """Test that partner role gets task-limited permissions."""
    principal = {"role": "partner", "partner_org_code": "DNATA"}
    
    scopes = service.permitted_scopes(principal)
    
    assert "task_limited_visibility" in scopes
    assert "submit_evidence" in scopes
    assert "acknowledge_tasks" in scopes
    assert "approve_recommendations" not in scopes


def test_permitted_scopes_for_passenger_role(service):
    """Test that passenger role gets bag/case status permissions only."""
    principal = {"role": "passenger", "passenger_reference": "PAX-001"}
    
    scopes = service.permitted_scopes(principal)
    
    assert "bag_status" in scopes
    assert "delayed_bag_case_status" in scopes
    assert "approve_recommendations" not in scopes


def test_permitted_scopes_for_executive_role(service):
    """Test that executive role gets aggregate metrics permissions only."""
    principal = {"role": "executive", "station_scope": "DXB"}
    
    scopes = service.permitted_scopes(principal)
    
    assert "aggregate_metrics" in scopes
    assert "approve_recommendations" not in scopes


def test_data_filter_rules_for_operations(service):
    """Test that operations role gets full visibility filter rules."""
    principal = {
        "role": "operations",
        "station_scope": "DXB",
    }
    
    rules = service.data_filter_rules(principal, "get_case_detail")
    
    assert rules["station_filter"] == "DXB"
    assert rules["mask_passenger_names"] is False
    assert rules["include_internal_notes"] is True
    assert rules["include_risk_scores"] is True


def test_data_filter_rules_for_partner(service):
    """Test that partner role gets least-privilege filter rules."""
    principal = {
        "role": "partner",
        "partner_org_code": "DNATA",
        "station_scope": "DXB",
    }
    
    rules = service.data_filter_rules(principal, "list_tasks")
    
    assert rules["partner_org_filter"] == "DNATA"
    assert rules["station_filter"] == "DXB"
    assert rules["mask_passenger_names"] is True
    assert rules["include_internal_notes"] is False
    assert rules["include_risk_scores"] is False
    assert rules["task_limited_visibility"] is True


def test_data_filter_rules_for_passenger(service):
    """Test that passenger role gets passenger-safe filter rules."""
    principal = {
        "role": "passenger",
        "passenger_reference": "PAX-001",
    }
    
    rules = service.data_filter_rules(principal, "get_bag_status")
    
    assert rules["passenger_reference_filter"] == "PAX-001"
    assert rules["mask_passenger_names"] is False
    assert rules["include_internal_notes"] is False
    assert rules["include_risk_scores"] is False
    assert rules["passenger_safe_only"] is True


def test_enforce_partner_org_scope_allows_matching_org(service):
    """Test that partner users can access tasks from their own organization."""
    principal = {
        "role": "partner",
        "partner_org_code": "DNATA",
    }
    
    allowed = service.enforce_partner_org_scope(principal, "DNATA")
    
    assert allowed is True


def test_enforce_partner_org_scope_denies_different_org(service):
    """Test that partner users cannot access tasks from other organizations (403)."""
    principal = {
        "role": "partner",
        "partner_org_code": "DNATA",
    }
    
    allowed = service.enforce_partner_org_scope(principal, "Menzies")
    
    assert allowed is False


def test_enforce_partner_org_scope_allows_non_partner_roles(service):
    """Test that operations role is not subject to partner org scoping."""
    principal = {
        "role": "operations",
        "station_scope": "DXB",
    }
    
    allowed = service.enforce_partner_org_scope(principal, "DNATA")
    
    assert allowed is True


def test_enforce_partner_org_scope_denies_partner_without_org_code(service):
    """Test that partner user without org code cannot access any org-scoped resources."""
    principal = {
        "role": "partner",
        "partner_org_code": None,
    }
    
    allowed = service.enforce_partner_org_scope(principal, "DNATA")
    
    assert allowed is False
