# TASK-5 Handoff: Backend Feature B3 - Exception Grouping and Recommendations

## Implementation Summary

This task implemented exception case grouping and explainable recommendation services for the Baggage360 application. The implementation covers FR-005 (exception grouping and triage) and FR-006 (explainable recovery recommendations).

## Data Shapes

### ExceptionCase Schema
```python
{
    "case_id": str (UUID),
    "case_reference": str (e.g., "BC-DXB-240611"),
    "exception_type": str (e.g., "short_connection_risk", "transfer_monitoring"),
    "severity_code": str ("critical", "high", "medium", "low"),
    "deadline_at": datetime (ISO 8601),
    "status_code": str ("open", "under_review", "approved", "tasked", "in_recovery", "closed"),
    "observed_state_summary": str (confirmed facts from bag events),
    "predicted_state_summary": str (risk assessment and predicted outcome),
    "bag_count": int (number of bags in case),
    "created_at": datetime,
    "updated_at": datetime,
    "closed_at": datetime | None
}
```

### Recommendation Schema
```python
{
    "recommendation_id": str (UUID),
    "case_id": str (UUID, FK to exception_cases),
    "action_code": str ("PRIORITY_TRANSFER", "RESCHEDULE_CONNECTION", "LOCATE_BAG", "MONITOR"),
    "action_label": str (human-readable action description),
    "reason_text": str (explanation of why this action is recommended),
    "confidence_score": float (0.00-1.00),
    "freshness_state": str ("fresh", "stale", "awaiting_confirmation"),
    "evidence": list[str] (evidence summary items extracted from evidence_json),
    "generated_at": datetime,
    "superseded_at": datetime | None
}
```

## Seed Case References

The seed data includes 4 exception cases for testing and demo purposes:

### BC-DXB-240611 (Critical, 3 bags)
- **Severity**: critical
- **Bags**: EK001234567, EK001234568, EK001234569
- **Status**: open
- **Deadline**: ~36 minutes to cutoff
- **Observed State**: "3 bags arrived DXB, transfer scans missing, 36 minutes to cutoff"
- **Predicted State**: "Critical: approaching cutoff, requires immediate expedited handling"
- **Recommendations**: 
  - Top recommendation: PRIORITY_TRANSFER (confidence 0.85)
  - Alternative: MONITOR (confidence 0.72)
  - Superseded older: LOCATE_BAG (confidence 0.78, superseded)

### BC-DXB-240612 (High, 2 bags)
- **Severity**: high
- **Bags**: EK001234567, EK001234568
- **Status**: open
- **Deadline**: ~52 minutes to cutoff
- **Observed State**: "2 bags arrived DXB, transfer scan stale (14 min old), 52 minutes to cutoff"
- **Predicted State**: "Connection at risk, late inbound detected"
- **Recommendations**: PRIORITY_TRANSFER (confidence 0.80)

### BC-DXB-240613 (High, 2 bags)
- **Severity**: high
- **Bags**: EK001234568, EK001234569
- **Status**: open
- **Deadline**: ~1 hour 25 minutes to cutoff
- **Observed State**: "2 bags transfer confirmed, monitoring tight connection window"
- **Predicted State**: "High: adequate buffer but requires monitoring"

### BC-DXB-240614 (Medium, 1 bag)
- **Severity**: medium
- **Bags**: EK001234569
- **Status**: open
- **Deadline**: ~3 hours 30 minutes to cutoff
- **Observed State**: "1 bag transfer confirmed, sufficient connection window"
- **Predicted State**: "Moderate: sufficient buffer, continue monitoring"

## Recommendation Action Codes

### PRIORITY_TRANSFER
- **Action Label**: "Expedite Transfer to [Gate]"
- **When Generated**: Critical or high severity cases with < 90 minutes to deadline
- **Typical Confidence**: 0.75-0.92
- **Evidence Includes**: bag tags, time to deadline, severity, target gate, target flight

### MONITOR
- **Action Label**: "Continue Monitoring Connection"
- **When Generated**: Medium or low severity cases, or when buffer > 60 minutes
- **Typical Confidence**: 0.72-0.80
- **Evidence Includes**: bag tags, time to deadline, current status, connection window

### LOCATE_BAG (not currently generated, but supported)
- **Action Label**: "Initiate Bag Search"
- **When Generated**: When bag location unknown
- **Evidence Includes**: bag tags, last known location

### RESCHEDULE_CONNECTION (not currently generated, but supported)
- **Action Label**: "Move to Alternative Flight"
- **When Generated**: When original connection cannot be made
- **Evidence Includes**: original flight, alternative options

## Confidence Ranges

- **High Confidence (0.85-1.00)**: Fresh data, urgent time pressure, clear action path
- **Moderate Confidence (0.70-0.84)**: Adequate data quality, moderate urgency
- **Low Confidence (< 0.70)**: Stale data, uncertain conditions, speculative recommendations

Confidence is adjusted based on:
- Data freshness (fresh vs stale events)
- Time pressure (minutes to deadline)
- Severity of the case
- Quality of supporting evidence

## Service Behavior

### ExceptionCaseService

**create_case(bag_ids, exception_type, created_by_user_id)**
- Groups related bags into an exception case
- Calculates severity based on time to deadline and risk assessment
- Sets deadline to 90 minutes before onward flight departure
- Generates observed state summary from confirmed bag events
- Generates predicted state summary from risk assessment
- Automatically generates unique case reference (BC-DXB-YYYYMMDD-HHMMSS)

**list_prioritized_cases(severity, station_scope, status_code)**
- Returns cases ordered by deadline (most urgent first)
- Supports filtering by severity, station, and status
- Default filter: status_code="open"

**update_case_status(case_id, new_status)**
- Updates case status and updated_at timestamp
- Automatically sets closed_at when status changes to "closed"

### RecommendationService

**generate_recommendations(case_id)**
- Generates 1-2 recommendations per case based on severity and time to deadline
- Each recommendation includes:
  - Action code and human-readable label
  - Reason text explaining why this action is recommended
  - Confidence score (0.00-1.00) based on data quality and urgency
  - Freshness state calculated from latest event age
  - Evidence JSON with supporting bag events and journey context
- Priority transfer recommendations for critical/high severity with < 90 min to deadline
- Monitoring recommendations for medium/low severity or adequate buffer

**supersede_recommendation(recommendation_id)**
- Marks a recommendation as superseded by setting superseded_at
- Used when generating new recommendations to replace old ones

**get_recommendations_for_case(case_id, include_superseded)**
- Returns active recommendations by default (include_superseded=False)
- Can return all recommendations including superseded ones

## Repositories

### ExceptionCaseRepository
- get_by_id(case_id) - with relationships loaded
- get_by_reference(case_reference)
- list_prioritized(severity, station_scope, status_code, order_by_deadline)
- create(case)
- update_status(case_id, new_status)
- get_bags_by_case(case_id)
- add_bag_to_case(case_id, bag_id, primary_flag)
- get_case_bag_count(case_id)

### RecommendationRepository
- get_by_id(recommendation_id)
- get_by_case(case_id, include_superseded)
- create(recommendation)
- supersede(recommendation_id)
- supersede_all_for_case(case_id)

## Integration Points

### Depends On
- **BagRepository** - for bag and event access
- **JourneyRepository** - for journey and leg access
- **RiskAssessmentService** - for predicted state generation

### Used By
- Future API routers will use these services to expose operations cockpit and case detail views
- Future approval and task orchestration features will build on these services

## Testing

Test coverage includes:
- Case creation with severity calculation
- Deadline calculation from onward flight
- Case prioritization and ordering
- Severity filtering
- Status updates and closed_at handling
- Bag count tracking
- Recommendation generation with confidence scores
- Reason text and evidence structure
- Freshness state calculation
- Superseding recommendations

All tests use the shared conftest.py fixture for database setup.
