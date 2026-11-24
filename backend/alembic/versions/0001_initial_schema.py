"""initial_schema

Revision ID: 0001
Revises: 
Create Date: 2024-01-01 00:00:00.000000

"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = '0001'
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Users table
    op.create_table(
        'users',
        sa.Column('id', sa.String(36), primary_key=True),
        sa.Column('external_subject', sa.String(255), nullable=False),
        sa.Column('role_code', sa.String(50), nullable=False),
        sa.Column('display_name', sa.String(255), nullable=False),
        sa.Column('partner_org_code', sa.String(50), nullable=True),
        sa.Column('station_scope', sa.String(10), nullable=True),
        sa.Column('passenger_reference', sa.String(255), nullable=True),
        sa.Column('active_flag', sa.Boolean(), nullable=False, server_default='1'),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
    )

    # Passenger journeys table
    op.create_table(
        'passenger_journeys',
        sa.Column('id', sa.String(36), primary_key=True),
        sa.Column('passenger_reference', sa.String(255), nullable=False),
        sa.Column('pnr_reference', sa.String(50), nullable=False),
        sa.Column('itinerary_status', sa.String(50), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
    )

    # Journey legs table
    op.create_table(
        'journey_legs',
        sa.Column('id', sa.String(36), primary_key=True),
        sa.Column('journey_id', sa.String(36), nullable=False),
        sa.Column('sequence_number', sa.Integer(), nullable=False),
        sa.Column('flight_number', sa.String(20), nullable=False),
        sa.Column('departure_station', sa.String(10), nullable=False),
        sa.Column('arrival_station', sa.String(10), nullable=False),
        sa.Column('scheduled_departure_at', sa.DateTime(), nullable=False),
        sa.Column('scheduled_arrival_at', sa.DateTime(), nullable=False),
        sa.Column('actual_arrival_at', sa.DateTime(), nullable=True),
        sa.Column('gate_code', sa.String(10), nullable=True),
        sa.Column('stand_code', sa.String(10), nullable=True),
        sa.Column('aircraft_registration', sa.String(20), nullable=True),
        sa.Column('leg_status', sa.String(50), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(['journey_id'], ['passenger_journeys.id']),
    )
    op.create_index('ix_journey_legs_journey_id', 'journey_legs', ['journey_id'])

    # Bags table
    op.create_table(
        'bags',
        sa.Column('id', sa.String(36), primary_key=True),
        sa.Column('bag_tag', sa.String(50), nullable=False),
        sa.Column('journey_id', sa.String(36), nullable=False),
        sa.Column('latest_confirmed_event_id', sa.String(36), nullable=True),
        sa.Column('current_case_id', sa.String(36), nullable=True),
        sa.Column('current_status_code', sa.String(50), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(['journey_id'], ['passenger_journeys.id']),
        sa.UniqueConstraint('bag_tag'),
    )
    op.create_index('ix_bags_bag_tag', 'bags', ['bag_tag'], unique=True)
    op.create_index('ix_bags_journey_id', 'bags', ['journey_id'])

    # Bag events table
    op.create_table(
        'bag_events',
        sa.Column('id', sa.String(36), primary_key=True),
        sa.Column('bag_id', sa.String(36), nullable=False),
        sa.Column('source_event_key', sa.String(255), nullable=False),
        sa.Column('source_system', sa.String(100), nullable=False),
        sa.Column('event_type', sa.String(50), nullable=False),
        sa.Column('event_station', sa.String(10), nullable=True),
        sa.Column('observed_at', sa.DateTime(), nullable=False),
        sa.Column('ingested_at', sa.DateTime(), nullable=False),
        sa.Column('fact_type', sa.String(50), nullable=False),
        sa.Column('freshness_state', sa.String(50), nullable=False),
        sa.Column('confidence_score', sa.Numeric(5, 2), nullable=True),
        sa.Column('payload_json', sa.Text(), nullable=False),
        sa.ForeignKeyConstraint(['bag_id'], ['bags.id']),
        sa.UniqueConstraint('source_event_key'),
    )
    op.create_index('ix_bag_events_bag_id', 'bag_events', ['bag_id'])
    op.create_index('ix_bag_events_source_event_key', 'bag_events', ['source_event_key'], unique=True)
    op.create_index('ix_bag_events_observed_at', 'bag_events', ['observed_at'])

    # Exception cases table
    op.create_table(
        'exception_cases',
        sa.Column('id', sa.String(36), primary_key=True),
        sa.Column('case_reference', sa.String(50), nullable=False),
        sa.Column('exception_type', sa.String(50), nullable=False),
        sa.Column('severity_code', sa.String(50), nullable=False),
        sa.Column('deadline_at', sa.DateTime(), nullable=False),
        sa.Column('status_code', sa.String(50), nullable=False),
        sa.Column('observed_state_summary', sa.Text(), nullable=False),
        sa.Column('predicted_state_summary', sa.Text(), nullable=False),
        sa.Column('created_by_user_id', sa.String(36), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.Column('closed_at', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['created_by_user_id'], ['users.id']),
        sa.UniqueConstraint('case_reference'),
    )
    op.create_index('ix_exception_cases_case_reference', 'exception_cases', ['case_reference'], unique=True)
    op.create_index('ix_exception_cases_deadline_at', 'exception_cases', ['deadline_at'])
    op.create_index('ix_exception_cases_status_code', 'exception_cases', ['status_code'])
    op.create_index('ix_exception_cases_created_by_user_id', 'exception_cases', ['created_by_user_id'])

    # Case bags table
    op.create_table(
        'case_bags',
        sa.Column('case_id', sa.String(36), primary_key=True),
        sa.Column('bag_id', sa.String(36), primary_key=True),
        sa.Column('primary_flag', sa.Boolean(), nullable=False, server_default='0'),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(['case_id'], ['exception_cases.id']),
        sa.ForeignKeyConstraint(['bag_id'], ['bags.id']),
        sa.PrimaryKeyConstraint('case_id', 'bag_id'),
    )
    op.create_index('ix_case_bags_case_id', 'case_bags', ['case_id'])
    op.create_index('ix_case_bags_bag_id', 'case_bags', ['bag_id'])

    # Recommendations table
    op.create_table(
        'recommendations',
        sa.Column('id', sa.String(36), primary_key=True),
        sa.Column('case_id', sa.String(36), nullable=False),
        sa.Column('action_code', sa.String(50), nullable=False),
        sa.Column('action_label', sa.String(255), nullable=False),
        sa.Column('reason_text', sa.Text(), nullable=False),
        sa.Column('confidence_score', sa.Numeric(5, 2), nullable=False),
        sa.Column('freshness_state', sa.String(50), nullable=False),
        sa.Column('evidence_json', sa.Text(), nullable=False),
        sa.Column('generated_at', sa.DateTime(), nullable=False),
        sa.Column('superseded_at', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['case_id'], ['exception_cases.id']),
    )
    op.create_index('ix_recommendations_case_id', 'recommendations', ['case_id'])

    # Approval decisions table
    op.create_table(
        'approval_decisions',
        sa.Column('id', sa.String(36), primary_key=True),
        sa.Column('case_id', sa.String(36), nullable=False),
        sa.Column('recommendation_id', sa.String(36), nullable=False),
        sa.Column('decided_by_user_id', sa.String(36), nullable=False),
        sa.Column('decision_code', sa.String(50), nullable=False),
        sa.Column('rationale_text', sa.Text(), nullable=True),
        sa.Column('decided_at', sa.DateTime(), nullable=False),
        sa.Column('decision_version', sa.Integer(), nullable=False, server_default='1'),
        sa.ForeignKeyConstraint(['case_id'], ['exception_cases.id']),
        sa.ForeignKeyConstraint(['recommendation_id'], ['recommendations.id']),
        sa.ForeignKeyConstraint(['decided_by_user_id'], ['users.id']),
        sa.UniqueConstraint('case_id', 'recommendation_id', 'decision_version', name='uq_approval_version'),
    )
    op.create_index('ix_approval_decisions_case_id', 'approval_decisions', ['case_id'])
    op.create_index('ix_approval_decisions_recommendation_id', 'approval_decisions', ['recommendation_id'])
    op.create_index('ix_approval_decisions_decided_by_user_id', 'approval_decisions', ['decided_by_user_id'])

    # Tasks table
    op.create_table(
        'tasks',
        sa.Column('id', sa.String(36), primary_key=True),
        sa.Column('case_id', sa.String(36), nullable=False),
        sa.Column('recommendation_id', sa.String(36), nullable=False),
        sa.Column('assigned_role_code', sa.String(50), nullable=False),
        sa.Column('assigned_partner_org_code', sa.String(50), nullable=True),
        sa.Column('bag_reference', sa.String(50), nullable=False),
        sa.Column('station_code', sa.String(10), nullable=False),
        sa.Column('flight_context_text', sa.Text(), nullable=False),
        sa.Column('instruction_text', sa.Text(), nullable=False),
        sa.Column('evidence_links_json', sa.Text(), nullable=False),
        sa.Column('deadline_at', sa.DateTime(), nullable=False),
        sa.Column('status_code', sa.String(50), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(['case_id'], ['exception_cases.id']),
        sa.ForeignKeyConstraint(['recommendation_id'], ['recommendations.id']),
    )
    op.create_index('ix_tasks_case_id', 'tasks', ['case_id'])
    op.create_index('ix_tasks_recommendation_id', 'tasks', ['recommendation_id'])
    op.create_index('ix_tasks_assigned_role_code', 'tasks', ['assigned_role_code'])
    op.create_index('ix_tasks_assigned_partner_org_code', 'tasks', ['assigned_partner_org_code'])
    op.create_index('ix_tasks_station_code', 'tasks', ['station_code'])
    op.create_index('ix_tasks_deadline_at', 'tasks', ['deadline_at'])
    op.create_index('ix_tasks_status_code', 'tasks', ['status_code'])

    # Task evidence table
    op.create_table(
        'task_evidence',
        sa.Column('id', sa.String(36), primary_key=True),
        sa.Column('task_id', sa.String(36), nullable=False),
        sa.Column('actor_user_id', sa.String(36), nullable=False),
        sa.Column('event_type', sa.String(50), nullable=False),
        sa.Column('note_text', sa.Text(), nullable=True),
        sa.Column('evidence_type', sa.String(50), nullable=True),
        sa.Column('evidence_reference', sa.String(255), nullable=True),
        sa.Column('client_event_id', sa.String(255), nullable=False),
        sa.Column('recorded_at', sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(['task_id'], ['tasks.id']),
        sa.ForeignKeyConstraint(['actor_user_id'], ['users.id']),
        sa.UniqueConstraint('client_event_id', name='uq_client_event_id'),
    )
    op.create_index('ix_task_evidence_task_id', 'task_evidence', ['task_id'])
    op.create_index('ix_task_evidence_actor_user_id', 'task_evidence', ['actor_user_id'])

    # Passenger case views table
    op.create_table(
        'passenger_case_views',
        sa.Column('id', sa.String(36), primary_key=True),
        sa.Column('case_id', sa.String(36), nullable=False),
        sa.Column('case_reference', sa.String(50), nullable=False),
        sa.Column('latest_confirmed_status', sa.String(255), nullable=False),
        sa.Column('estimated_notice', sa.Text(), nullable=True),
        sa.Column('next_expected_update', sa.String(255), nullable=False),
        sa.Column('passenger_safe_payload_json', sa.Text(), nullable=False),
        sa.Column('refreshed_at', sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(['case_id'], ['exception_cases.id']),
        sa.UniqueConstraint('case_id', name='uq_case_view'),
        sa.UniqueConstraint('case_reference', name='uq_case_reference_view'),
    )
    op.create_index('ix_passenger_case_views_case_id', 'passenger_case_views', ['case_id'])
    op.create_index('ix_passenger_case_views_case_reference', 'passenger_case_views', ['case_reference'])

    # Executive daily metrics table
    op.create_table(
        'executive_daily_metrics',
        sa.Column('id', sa.String(36), primary_key=True),
        sa.Column('metric_date', sa.Date(), nullable=False),
        sa.Column('station_code', sa.String(10), nullable=False),
        sa.Column('open_case_count', sa.Integer(), nullable=False),
        sa.Column('urgent_case_count', sa.Integer(), nullable=False),
        sa.Column('recovered_before_departure_count', sa.Integer(), nullable=False),
        sa.Column('impacted_passenger_count', sa.Integer(), nullable=False),
        sa.Column('stale_data_case_count', sa.Integer(), nullable=False),
        sa.Column('snapshot_generated_at', sa.DateTime(), nullable=False),
        sa.UniqueConstraint('metric_date', 'station_code', name='uq_daily_station_metric'),
    )
    op.create_index('ix_executive_daily_metrics_metric_date', 'executive_daily_metrics', ['metric_date'])
    op.create_index('ix_executive_daily_metrics_station_code', 'executive_daily_metrics', ['station_code'])

    # Audit events table
    op.create_table(
        'audit_events',
        sa.Column('id', sa.String(36), primary_key=True),
        sa.Column('actor_user_id', sa.String(36), nullable=True),
        sa.Column('action_type', sa.String(100), nullable=False),
        sa.Column('entity_type', sa.String(100), nullable=False),
        sa.Column('entity_id', sa.String(255), nullable=False),
        sa.Column('correlation_id', sa.String(255), nullable=False),
        sa.Column('outcome_code', sa.String(50), nullable=False),
        sa.Column('detail_json', sa.Text(), nullable=False),
        sa.Column('occurred_at', sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(['actor_user_id'], ['users.id']),
    )
    op.create_index('ix_audit_events_actor_user_id', 'audit_events', ['actor_user_id'])
    op.create_index('ix_audit_events_action_type', 'audit_events', ['action_type'])
    op.create_index('ix_audit_events_entity_id', 'audit_events', ['entity_id'])
    op.create_index('ix_audit_events_correlation_id', 'audit_events', ['correlation_id'])
    op.create_index('ix_audit_events_occurred_at', 'audit_events', ['occurred_at'])

    # Session access log table
    op.create_table(
        'session_access_log',
        sa.Column('id', sa.String(36), primary_key=True),
        sa.Column('actor_user_id', sa.String(36), nullable=False),
        sa.Column('access_purpose', sa.String(255), nullable=False),
        sa.Column('resource_type', sa.String(100), nullable=False),
        sa.Column('resource_id', sa.String(255), nullable=False),
        sa.Column('decision_code', sa.String(50), nullable=False),
        sa.Column('correlation_id', sa.String(255), nullable=False),
        sa.Column('occurred_at', sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(['actor_user_id'], ['users.id']),
    )
    op.create_index('ix_session_access_log_actor_user_id', 'session_access_log', ['actor_user_id'])
    op.create_index('ix_session_access_log_resource_id', 'session_access_log', ['resource_id'])
    op.create_index('ix_session_access_log_correlation_id', 'session_access_log', ['correlation_id'])
    op.create_index('ix_session_access_log_occurred_at', 'session_access_log', ['occurred_at'])


def downgrade() -> None:
    op.drop_table('session_access_log')
    op.drop_table('audit_events')
    op.drop_table('executive_daily_metrics')
    op.drop_table('passenger_case_views')
    op.drop_table('task_evidence')
    op.drop_table('tasks')
    op.drop_table('approval_decisions')
    op.drop_table('recommendations')
    op.drop_table('case_bags')
    op.drop_table('exception_cases')
    op.drop_table('bag_events')
    op.drop_table('bags')
    op.drop_table('journey_legs')
    op.drop_table('passenger_journeys')
    op.drop_table('users')
