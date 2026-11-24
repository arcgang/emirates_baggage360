# TASK-4 Handoff: Source Freshness and Connection Risk

## Overview
Task 4 implemented source freshness labeling and connection risk assessment services for the Baggage360 demo. This establishes the foundation for FR-003 (source freshness and provenance) and FR-004 (connection risk assessment) features.

## Key Components Implemented

### 1. RiskAssessmentService (`backend/app/services/risk_assessment_service.py`)
Service for evaluating connection risk and urgency ranking.

**Key Methods:**
- `calculate_connection_risk(bag, case, latest_event)` - Main risk calculation method
- `evaluate_risk(bag_id, case_id)` - Convenience method for evaluating risk by IDs
- Internal helper methods for risk label evaluation, urgency ranking, and state summaries

**Risk Assessment Output Shape:**
```python
{
    "risk_label": str,           # e.g., "Connection at risk, late inbound"
    "urgency_rank": int,         # 1-5, with 1 being most urgent
    "observed_state_summary": str,   # Confirmed facts from observed events
    "predicted_state_summary": str,  # Predicted risk and outcome
    "time_to_cutoff_minutes": int    # Minutes until cutoff time (90 min before departure)
}
```

**Risk Labels:**
- `"Critical: transfer scan missing, approaching cutoff"` - Transfer scan missing with < 60 min to cutoff
- `"Transfer scan missing"` - No observed transfer scan
- `"Critical: approaching cutoff"` - < 45 min to cutoff
- `"Connection at risk, late inbound"` - 45-90 min to cutoff or inbound delay > 30 min
- `"Moderate: sufficient buffer"` - > 90 min to cutoff
- `"Normal: on track"` - Default state

**Urgency Ranking:**
- Rank 1 (most urgent): Critical risk labels, < 30 min to cutoff, or critical severity
- Rank 2: Connection at risk, < 60 min to cutoff, or high severity
- Rank 3: Transfer scan missing
- Rank 4: Moderate risk
- Rank 5: Normal/on track

### 2. BagEventRepository Freshness Calculation (`backend/app/repositories/bag_repository.py`)
Extended with freshness state calculation logic.

**New Method:**
- `calculate_freshness_state(event)` - Calculate freshness state for a bag event

**Freshness Thresholds:**
- `"fresh"` - < 10 minutes since ingested_at
- `"stale"` - >= 10 minutes since ingested_at
- `"awaiting_confirmation"` - Derived/estimated event (not observed)

### 3. Extended Schemas (`backend/app/schemas/operations_schemas.py`)
Added two new Pydantic schemas:

**FreshnessStatus:**
```python
{
    "state": str,                    # fresh, stale, or awaiting_confirmation
    "age_minutes": Optional[int],
    "source_system": Optional[str],
    "last_updated_at": Optional[datetime]
}
```

**RiskAssessment:**
```python
{
    "risk_label": str,
    "urgency_rank": int,
    "observed_state_summary": str,
    "predicted_state_summary": str,
    "time_to_cutoff_minutes": Optional[int]
}
```

### 4. Extended Seed Data (`backend/app/seed.py`)
Seed data now includes three scenarios with varying freshness ages and risk labels:

**Seed Case IDs with Known Risk States:**

| Case Reference | Bag Tag | Risk Label | Severity | Time to Cutoff | Freshness State | Ingested Age |
|----------------|---------|------------|----------|----------------|-----------------|--------------|
| CASE-20241101-001 | EK001234567 | Critical: transfer scan missing, approaching cutoff | critical | 36 min | fresh | 2 min |
| CASE-20241101-002 | EK001234568 | Connection at risk, late inbound | high | 52 min | stale | 14 min |
| CASE-20241101-003 | EK001234569 | Moderate: sufficient buffer | medium | 85 min | fresh | 6 min |

**Journey Legs Updated:**
- Journey 1: Inbound EK001 (arrived 1h15m ago), Onward EK101 (departs in 2h6m) → 36 min to cutoff
- Journey 2: Inbound EK002 (arrived 2h5m ago), Onward EK103 (departs in 2h55m) → 85 min to cutoff

**Bag Events Updated:**
- Bag 1 (EK001234567): Last event ingested 2 minutes ago (fresh)
- Bag 2 (EK001234568): Last event ingested 14 minutes ago (stale)
- Bag 3 (EK001234569): Last event ingested 6 minutes ago (fresh)

## Testing
Test suite `tests/test_risk_assessment_service.py` includes:
1. `test_calculate_connection_risk_critical` - Critical risk scenario
2. `test_calculate_connection_risk_late_inbound` - Late inbound scenario
3. `test_calculate_connection_risk_moderate` - Moderate risk scenario
4. `test_urgency_ranking` - Urgency ranking logic
5. `test_freshness_calculation` - Freshness state calculation
6. `test_evaluate_risk_integration` - Integration test

## Acceptance Criteria Coverage

### FR-003: Source Freshness and Provenance
- ✓ Freshness state calculation (fresh < 10 min, stale >= 10 min, awaiting_confirmation for derived)
- ✓ Source system labeling in BagEvent model
- ✓ Freshness indicators in seed data
- ✓ FreshnessStatus schema for API responses

### FR-004: Connection Risk Assessment
- ✓ Risk evaluation using bag event state and onward connection context
- ✓ Observed state separate from predicted risk state
- ✓ Urgency ranking based on time to cutoff and passenger impact (1-5 scale)
- ✓ Risk labels with actionable descriptions

## Integration Points

### For Operations Cockpit (Future Task):
- Call `RiskAssessmentService.evaluate_risk(bag_id, case_id)` for each case
- Display `risk_label` as badge on case cards
- Use `urgency_rank` for case prioritization
- Show `time_to_cutoff_minutes` for deadline pressure

### For Case Detail (Future Task):
- Display `observed_state_summary` in "Confirmed State" section
- Display `predicted_state_summary` in "Risk Assessment" section
- Use `FreshnessStatus` to show data age indicators
- Include freshness badges on bag timeline milestones

### For Bag Timeline (Already Implemented in TASK-3):
- BagJourneyService already composes bag timelines with freshness_state
- RiskAssessmentService complements this with risk labels

## Database Schema (No Changes)
No schema changes required. Task uses existing models:
- `BagEvent.ingested_at` for freshness calculation
- `BagEvent.fact_type` for distinguishing observed/derived/estimated
- `ExceptionCase.severity_code` for urgency adjustment
- `JourneyLeg.scheduled_departure_at` for cutoff calculation

## Notes for UI Implementation
- Display freshness badges: 🟢 Fresh, 🟡 Stale, ⏳ Awaiting Confirmation
- Display risk badges: 🔴 Critical, 🟠 High, 🟡 Medium, 🟢 Low
- Show time to cutoff as countdown timer when < 60 minutes
- Separate "What We Know" (observed) from "What We Predict" (risk assessment) in UI

## Seed Credentials (Unchanged)
Operations user can view all three risk scenarios:
- Email: mariam.alsuwaidi@baggage360.demo
- Password: Demo1234!

## Known Limitations
- Risk assessment is calculated on-demand, not cached
- Cutoff time is hardcoded to 90 minutes before departure (matches airline industry standard)
- Freshness calculation uses ingested_at timestamp (when system received the event)
- No real-time freshness updates (would require WebSocket or polling in production)
