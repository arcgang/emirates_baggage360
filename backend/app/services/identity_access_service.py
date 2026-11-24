"""Identity and access control service for role-based authorization."""


class IdentityAccessService:
    """
    Resolves principal identity from JWT and enforces role-based access control.
    
    Implements REQ-SEC-002: role-based access control enforcement with differentiated
    permissions for operations, partner, passenger, and executive roles.
    
    Supports FR-019: access control by role and purpose with partner organization scoping.
    """
    
    def resolve_principal(self, jwt_payload: dict) -> dict:
        """
        Resolve principal context from JWT payload.
        
        Args:
            jwt_payload: Decoded JWT token payload with user_id, role, etc.
        
        Returns:
            Principal context dict with user_id, role, display_name, partner_org_code, station_scope
        """
        return {
            "user_id": jwt_payload.get("sub"),
            "role": jwt_payload.get("role"),
            "display_name": jwt_payload.get("display_name"),
            "partner_org_code": jwt_payload.get("partner_org_code"),
            "station_scope": jwt_payload.get("station_scope"),
        }
    
    def role_evaluation(self, principal: dict) -> str:
        """
        Evaluate the role of the current principal.
        
        Args:
            principal: Principal context dict
        
        Returns:
            Role code (operations, partner, passenger, executive)
        """
        return principal.get("role", "")
    
    def permitted_scopes(self, principal: dict) -> list[str]:
        """
        Get permitted scopes for the principal based on role.
        
        Args:
            principal: Principal context dict
        
        Returns:
            List of permitted scope strings
        """
        role = self.role_evaluation(principal)
        
        if role == "operations":
            return ["full_operational_case_visibility", "approve_recommendations", "view_audit_trail"]
        elif role == "partner":
            return ["task_limited_visibility", "submit_evidence", "acknowledge_tasks"]
        elif role == "passenger":
            return ["bag_status", "delayed_bag_case_status"]
        elif role == "executive":
            return ["aggregate_metrics"]
        else:
            return []
    
    def data_filter_rules(
        self,
        principal: dict,
        operation: str
    ) -> dict:
        """
        Get data filter rules for the principal based on role and operation.
        
        Implements least-privilege filtering:
        - Operations: full case visibility within station scope
        - Partner: task-limited visibility with partner org scoping
        - Passenger: bag and case status only for authorized references
        - Executive: aggregate metrics only
        
        Args:
            principal: Principal context dict
            operation: Operation type (e.g., "list_tasks", "get_case_detail")
        
        Returns:
            Filter rules dict with keys like partner_org_filter, mask_passenger_names, etc.
        """
        role = self.role_evaluation(principal)
        rules = {}
        
        if role == "operations":
            rules["station_filter"] = principal.get("station_scope")
            rules["mask_passenger_names"] = False
            rules["include_internal_notes"] = True
            rules["include_risk_scores"] = True
        elif role == "partner":
            rules["partner_org_filter"] = principal.get("partner_org_code")
            rules["station_filter"] = principal.get("station_scope")
            rules["mask_passenger_names"] = True
            rules["include_internal_notes"] = False
            rules["include_risk_scores"] = False
            rules["task_limited_visibility"] = True
        elif role == "passenger":
            rules["passenger_reference_filter"] = principal.get("passenger_reference")
            rules["mask_passenger_names"] = False
            rules["include_internal_notes"] = False
            rules["include_risk_scores"] = False
            rules["passenger_safe_only"] = True
        elif role == "executive":
            rules["aggregate_only"] = True
            rules["station_filter"] = principal.get("station_scope")
            rules["mask_passenger_names"] = True
            rules["include_internal_notes"] = False
            rules["include_risk_scores"] = False
        
        return rules
    
    def enforce_partner_org_scope(
        self,
        principal: dict,
        resource_partner_org: str | None
    ) -> bool:
        """
        Enforce partner organization scoping for a resource.
        
        Returns True if access is allowed, False if 403 FORBIDDEN_SCOPE should be raised.
        
        Args:
            principal: Principal context dict
            resource_partner_org: Partner org code of the resource being accessed
        
        Returns:
            True if access allowed, False if forbidden
        """
        role = self.role_evaluation(principal)
        
        # Non-partner roles don't have org scoping
        if role != "partner":
            return True
        
        # Partner users can only access resources assigned to their organization
        principal_org = principal.get("partner_org_code")
        
        if not principal_org:
            # Partner user without org code should not access any org-scoped resources
            return False
        
        return resource_partner_org == principal_org
