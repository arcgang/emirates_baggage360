# TASK-3 Handoff: Bag Journey Visibility and Context Correlation

## Overview
Backend Feature B1 provides baggage journey visibility and journey context correlation services, repositories, and seed data for operations cockpit and case detail views.

## Data Models Created

### BagTimeline Schema
Complete bag timeline with milestones and journey context returned by `BagJourneyService.compose_bag_timeline()`.

```python
{
  "bag_id": str,  # UUID
  "bag_tag": str,  # e.g., "EK001234567"
  "passenger_name_masked": str,  # e.g., "PAX-***-001"
  "journey_context": JourneyContext | None,
  "milestones": list[BagMilestone]
}
```

### JourneyContext Schema
Journey context showing inbound/onward flights, connection window, and operational changes.

```python
{
  "journey_id": str,  # UUID
  "inbound_flight": str,  # e.g., "EK001 LHR-DXB"
  "onward_flight": str,  # e.g., "EK101 DXB-SYD"
  "connection_window_minutes": int,
  "gate_change": str | None,  # e.g., "Changed to B05"
  "stand_change": str | None,
  "aircraft_change": str | None
}
```

### BagMilestone Schema
Individual bag milestone event with source, fact type, and freshness state.

```python
{
  "event_type": str,  # e.g., "acceptance", "loaded", "arrived", "transfer_pending"
  "observed_at": datetime,
  "source_system": str,  # "Wasla", "BHS", "BRS", "flight_ops"
  "fact_type": str,  # "observed", "derived", or "estimated"
  "freshness_state": str,  # "fresh", "stale", or "awaiting_confirmation"
  "location_code": str | None  # e.g., "JFK", "DXB"
}
```

## Service Interface

### BagJourneyService
Main service for composing bag timelines with journey context.

**Constructor:**
```python
BagJourneyService(db: Session)
```

**Methods:**
- `compose_bag_timeline(bag_id: str) -> BagTimeline | None`
  - Returns complete bag timeline with milestones and journey context
  - Marks milestones as observed/derived/estimated
  - Labels source system for each milestone
  - Calculates freshness state based on observed_at timestamp (>30 min = stale)
  - Correlates journey context (inbound/onward flights, connection window)
  - Masks passenger name for privacy

## Repository Interfaces

### BagRepository
Access to bag aggregates.

**Methods:**
- `get_by_tag(bag_tag: str) -> Bag | None`
- `get_by_id(bag_id: str) -> Bag | None`
- `list_by_case(case_id: str) -> list[Bag]`

### BagEventRepository
Access to bag events.

**Methods:**
- `get_by_bag(bag_id: str) -> list[BagEvent]` - Returns events ordered by observed_at
- `create(bag_event: BagEvent) -> BagEvent`
- `list_latest_by_bags(bag_ids: list[str]) -> dict[str, BagEvent]` - Returns latest event per bag with freshness calculation

### JourneyRepository
Access to passenger journeys and legs.

**Methods:**
- `get_by_id(journey_id: str) -> PassengerJourney | None`
- `get_legs_by_journey(journey_id: str) -> list[JourneyLeg]` - Returns legs ordered by sequence number

## Seed Data Test Scenarios

### Scenario 1: At-Risk Connection (bag1)
**Bag Tag:** `EK001234567`  
**Journey ID:** `00000000-0000-0000-0000-000000000065` (journey1)  
**Status:** `in_transfer`

**Events:**
1. Acceptance at JFK (Wasla, observed, 14h ago)
2. Loaded on EK0201 at JFK (BHS, observed, 13h ago)
3. Arrived at DXB (BRS, observed, 1h15m ago)
4. Transfer pending to gate B05 (flight_ops, derived, 45m ago, **stale**)

**Journey Context:**
- Inbound: EK0201 JFK-DXB (arrived 1h15m ago)
- Onward: EK101 DXB-SYD (departure in 2h)
- Connection window: ~105 minutes (tight)

### Scenario 2: At-Risk with Stale Transfer (bag2)
**Bag Tag:** `EK001234568`  
**Journey ID:** `00000000-0000-0000-0000-000000000065` (journey1)  
**Status:** `at_risk`

**Events:**
1. Acceptance at JFK (Wasla, observed, 14h10m ago)
2. Loaded on EK0201 at JFK (BHS, observed, 13h5m ago)
3. Arrived at DXB (BRS, observed, 1h20m ago)
4. Transfer pending to gate B05 (flight_ops, derived, 1h ago, **stale**)

**Journey Context:**
- Same as scenario 1 (shared journey)
- Last event is older/staler than bag1

### Scenario 3: On-Time Connection (bag3)
**Bag Tag:** `EK001234569`  
**Journey ID:** `00000000-0000-0000-0000-000000000066` (journey2)  
**Status:** `on_time`

**Events:**
1. Acceptance at LHR (Wasla, observed, 8h ago)
2. Loaded on EK002 at LHR (BHS, observed, 7h ago)
3. Arrived at DXB (BRS, observed, 2h ago)
4. Transfer confirmed to gate C10 (Wasla, observed, 30m ago, **fresh**)

**Journey Context:**
- Inbound: EK002 LHR-DXB
- Onward: EK103 DXB-destination
- Connection window: comfortable
- All events confirmed (observed), no stale/derived events

## Usage in Future Operations Endpoints

The `BagJourneyService.compose_bag_timeline()` method is designed to be called from future operations endpoints such as:
- Operations case detail endpoints to populate bag timeline arrays
- Operations cockpit endpoints needing bag journey context

**Note:** This task provides the service layer only. API endpoints will be implemented in subsequent tasks.

## Freshness Calculation Logic
- Events observed within last 30 minutes → `freshness_state = "fresh"`
- Events older than 30 minutes → `freshness_state = "stale"`
- Freshness is calculated at query time, not stored
- Used to highlight data staleness in operations views

## Source System Labels
- **Wasla:** Baggage scan intake system (acceptance, transfer confirmations)
- **BHS:** Baggage Handling System (loading events)
- **BRS:** Baggage Reconciliation System (arrival events)
- **flight_ops:** Flight operations context (derived transfer status)

## Fact Type Semantics
- **observed:** Directly scanned/captured event from source system (high confidence)
- **derived:** Computed from other events or flight context (medium confidence)
- **estimated:** Predicted based on models (lower confidence, not used in seed data)

## Next Steps for Frontend
When implementing the operations cockpit and case detail views, use the `BagTimeline` schema to:
1. Display bag milestones in chronological order
2. Show source system and fact type for each milestone
3. Highlight stale events with visual indicators
4. Display journey context showing connection window and operational changes
5. Use masked passenger names (do not display raw passenger_reference)

## Test Coverage
See `/repos/emirates_baggage360/backend/tests/test_bag_journey_service.py` for:
- Timeline composition for at-risk and on-time scenarios
- Freshness labeling validation
- Journey correlation verification
- Passenger name masking
- Source system and fact type labeling
