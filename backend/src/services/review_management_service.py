"""
Review management service for handling uncertain business matches.
Implements flagging system, manual review workflow, and status tracking.
"""

from typing import List, Any, Optional
from datetime import datetime
import uuid
from ..core.base_service import BaseService
from ..schemas.business_matching import BusinessSourceData, ConfidenceLevel
from ..schemas.business_merging import MergedBusinessData, MergeConflict
from ..schemas.review_management import (
    ReviewStatus,
    ReviewPriority,
    ReviewFlag,
    ReviewWorkflow,
)


class ReviewManagementService(BaseService):
    """Service for managing manual review workflow for uncertain business matches."""

    def __init__(self):
        super().__init__("ReviewManagementService")
        self.logger.info("ReviewManagementService initialized")

        # Confidence thresholds for flagging - adjusted for hybrid scoring
        self.LOW_CONFIDENCE_THRESHOLD = 0.6
        self.UNCERTAIN_MATCH_THRESHOLD = (
            0.5  # Lowered to catch medium confidence + conflicts
        )

        # Review workflow steps
        self.WORKFLOW_STEPS = [
            "initial_assessment",
            "data_verification",
            "conflict_resolution",
            "final_approval",
        ]

    def validate_input(self, data: Any) -> bool:
        """Validate input data for the service."""
        return data is not None

    def flag_uncertain_matches(
        self,
        merged_business: MergedBusinessData,
        conflicts_resolved: List[MergeConflict],
        source_data: List[BusinessSourceData],
    ) -> Optional[ReviewFlag]:
        """
        Flag uncertain matches for manual review.

        Args:
            merged_business: Merged business data
            conflicts_resolved: List of resolved conflicts
            source_data: Source data used for merging

        Returns:
            ReviewFlag if flagging is needed, None otherwise
        """
        try:
            if not self.validate_input(merged_business):
                return None

            self.log_operation(
                "flag_uncertain_matches", getattr(merged_business, "run_id", None)
            )

            # Check if flagging is needed
            should_flag = self._should_flag_for_review(
                merged_business, conflicts_resolved
            )

            if not should_flag:
                self.logger.debug(
                    f"No flagging needed for business {merged_business.business_id}"
                )
                return None

            # Create review flag
            flag = ReviewFlag(
                flag_id=str(uuid.uuid4()),
                business_id=merged_business.business_id,
                flag_type=self._determine_flag_type(
                    merged_business, conflicts_resolved
                ),
                priority=self._determine_priority(merged_business, conflicts_resolved),
                status=ReviewStatus.PENDING,
                reason=self._generate_flag_reason(merged_business, conflicts_resolved),
                confidence_score=self._confidence_level_to_score(
                    merged_business.confidence_level
                ),
                source_data=source_data,
                conflicts=conflicts_resolved,
                created_at=datetime.now().isoformat(),
                run_id=getattr(merged_business, "run_id", None),
            )

            self.logger.info(
                f"Created review flag {flag.flag_id} for business {merged_business.business_id}"
            )
            return flag

        except Exception as e:
            self.logger.error(f"Error flagging uncertain matches: {str(e)}")
            return None

    def create_review_workflow(self, review_flag: ReviewFlag) -> List[ReviewWorkflow]:
        """
        Create review workflow for a flagged business.

        Args:
            review_flag: Review flag to create workflow for

        Returns:
            List of workflow steps
        """
        try:
            if not self.validate_input(review_flag):
                return []

            self.log_operation("create_review_workflow", review_flag.run_id)

            workflow_steps = []

            for i, step_name in enumerate(self.WORKFLOW_STEPS, 1):
                workflow_step = ReviewWorkflow(
                    workflow_id=str(uuid.uuid4()),
                    flag_id=review_flag.flag_id,
                    step_number=i,
                    step_name=step_name,
                    status="pending",
                    created_at=datetime.now().isoformat(),
                )
                workflow_steps.append(workflow_step)

            self.logger.info(
                f"Created review workflow with {len(workflow_steps)} steps for flag {review_flag.flag_id}"
            )
            return workflow_steps

        except Exception as e:
            self.logger.error(f"Error creating review workflow: {str(e)}")
            return []

    def assign_review(self, review_flag: ReviewFlag, user_id: str) -> bool:
        """
        Assign review to a specific user.

        Args:
            review_flag: Review flag to assign
            user_id: User ID to assign the review to

        Returns:
            True if assignment successful, False otherwise
        """
        try:
            if not self.validate_input(review_flag) or not user_id:
                return False

            self.log_operation("assign_review", review_flag.run_id)

            # Update flag assignment
            review_flag.assigned_to = user_id
            review_flag.assigned_at = datetime.now().isoformat()
            review_flag.status = ReviewStatus.IN_REVIEW

            self.logger.info(
                f"Assigned review flag {review_flag.flag_id} to user {user_id}"
            )
            return True

        except Exception as e:
            self.logger.error(f"Error assigning review: {str(e)}")
            return False

    def update_review_status(
        self,
        review_flag: ReviewFlag,
        new_status: ReviewStatus,
        review_notes: Optional[str] = None,
        resolution: Optional[str] = None,
    ) -> bool:
        """
        Update review status and add review notes.

        Args:
            review_flag: Review flag to update
            new_status: New review status
            review_notes: Optional notes from reviewer
            resolution: Optional resolution action

        Returns:
            True if update successful, False otherwise
        """
        try:
            if not self.validate_input(review_flag):
                return False

            self.log_operation("update_review_status", review_flag.run_id)

            # Update flag status
            review_flag.status = new_status
            review_flag.reviewed_at = datetime.now().isoformat()

            if review_notes:
                review_flag.review_notes = review_notes

            if resolution:
                review_flag.resolution = resolution

            self.logger.info(
                f"Updated review flag {review_flag.flag_id} status to {new_status}"
            )
            return True

        except Exception as e:
            self.logger.error(f"Error updating review status: {str(e)}")
            return False

    def get_pending_reviews(
        self,
        priority: Optional[ReviewPriority] = None,
        assigned_to: Optional[str] = None,
    ) -> List[ReviewFlag]:
        """
        Get list of pending reviews with optional filtering.

        Args:
            priority: Optional priority filter
            assigned_to: Optional user filter

        Returns:
            List of pending review flags
        """
        try:
            self.log_operation("get_pending_reviews", None)

            # This would typically query a database
            # For now, return empty list as placeholder
            pending_reviews = []

            self.logger.debug(f"Retrieved {len(pending_reviews)} pending reviews")
            return pending_reviews

        except Exception as e:
            self.logger.error(f"Error getting pending reviews: {str(e)}")
            return []

    def resolve_review_flag(
        self, review_flag: ReviewFlag, resolution_action: str, resolution_notes: str
    ) -> bool:
        """
        Resolve a review flag with final action and notes.

        Args:
            review_flag: Review flag to resolve
            resolution_action: Action taken to resolve the flag
            resolution_notes: Notes about the resolution

        Returns:
            True if resolution successful, False otherwise
        """
        try:
            if not self.validate_input(review_flag):
                return False

            self.log_operation("resolve_review_flag", review_flag.run_id)

            # Update flag with resolution
            review_flag.status = ReviewStatus.RESOLVED
            review_flag.resolution = resolution_action
            review_flag.review_notes = resolution_notes
            review_flag.reviewed_at = datetime.now().isoformat()

            self.logger.info(
                f"Resolved review flag {review_flag.flag_id} with action: {resolution_action}"
            )
            return True

        except Exception as e:
            self.logger.error(f"Error resolving review flag: {str(e)}")
            return False

    def _should_flag_for_review(
        self,
        merged_business: MergedBusinessData,
        conflicts_resolved: List[MergeConflict],
    ) -> bool:
        """Determine if business should be flagged for review using hybrid scoring."""
        # Always flag if business already marked for review
        if merged_business.needs_review:
            return True

        # Always flag if confidence is low
        if merged_business.confidence_level == ConfidenceLevel.LOW:
            return True

        # Use hybrid scoring for medium/high confidence businesses with conflicts
        if conflicts_resolved:
            # For medium confidence businesses, only flag if conflicts have low confidence
            if merged_business.confidence_level == ConfidenceLevel.MEDIUM:
                # Check if conflicts have low confidence (need review)
                low_confidence_conflicts = [
                    c for c in conflicts_resolved if c.confidence < 0.7
                ]
                return len(low_confidence_conflicts) > 0

            # For high confidence businesses, use scoring
            review_score = self._calculate_review_score(
                merged_business, conflicts_resolved
            )
            return review_score >= 0.5

        return False

    def _determine_flag_type(
        self,
        merged_business: MergedBusinessData,
        conflicts_resolved: List[MergeConflict],
    ) -> str:
        """Determine the type of flag needed."""
        if merged_business.confidence_level == ConfidenceLevel.LOW:
            return "low_confidence"
        elif conflicts_resolved:
            return "data_conflict"
        elif merged_business.needs_review:
            return "manual_review_required"
        else:
            return "uncertain_match"

    def _determine_priority(
        self,
        merged_business: MergedBusinessData,
        conflicts_resolved: List[MergeConflict],
    ) -> ReviewPriority:
        """Determine review priority using hybrid scoring system."""
        # High priority for low confidence
        if merged_business.confidence_level == ConfidenceLevel.LOW:
            return ReviewPriority.HIGH

        # Use hybrid scoring for priority determination
        if conflicts_resolved:
            # High priority for many conflicts regardless of confidence level
            if len(conflicts_resolved) > 3:
                return ReviewPriority.HIGH

            # For medium confidence businesses, priority depends on conflict confidence
            if merged_business.confidence_level == ConfidenceLevel.MEDIUM:
                # High priority for low confidence conflicts
                low_confidence_conflicts = [
                    c for c in conflicts_resolved if c.confidence < 0.7
                ]
                if len(low_confidence_conflicts) >= 2:
                    return ReviewPriority.HIGH
                elif len(low_confidence_conflicts) == 1:
                    return ReviewPriority.MEDIUM
                else:
                    return (
                        ReviewPriority.LOW
                    )  # High confidence conflicts don't need high priority

            priority_score = self._calculate_priority_score(
                merged_business, conflicts_resolved
            )

            if priority_score >= 0.8:
                return ReviewPriority.HIGH
            elif priority_score >= 0.6:
                return ReviewPriority.MEDIUM
            else:
                return ReviewPriority.LOW

        return ReviewPriority.LOW

    def _generate_flag_reason(
        self,
        merged_business: MergedBusinessData,
        conflicts_resolved: List[MergeConflict],
    ) -> str:
        """Generate intelligent flag reason based on hybrid scoring analysis."""
        reasons = []

        # Business confidence reason
        if merged_business.confidence_level == ConfidenceLevel.LOW:
            reasons.append("Low confidence in merged data")
        elif merged_business.confidence_level == ConfidenceLevel.MEDIUM:
            reasons.append("Medium confidence requiring validation")

        # Conflict analysis reason
        if conflicts_resolved:
            conflict_count = len(conflicts_resolved)
            avg_confidence = sum(c.confidence for c in conflicts_resolved) / len(
                conflicts_resolved
            )

            if conflict_count == 1:
                if avg_confidence < 0.6:
                    reasons.append("1 low-confidence data conflict detected")
                else:
                    reasons.append("1 data conflict requiring review")
            elif conflict_count == 2:
                if avg_confidence < 0.6:
                    reasons.append("2 low-confidence data conflicts detected")
                else:
                    reasons.append("2 data conflicts requiring review")
            else:
                reasons.append(f"{conflict_count} data conflicts detected")

            # Add field-specific details for critical conflicts
            critical_fields = ["phone", "website", "email", "address"]
            critical_conflicts = [
                c for c in conflicts_resolved if c.field_name in critical_fields
            ]
            if critical_conflicts:
                field_names = [c.field_name for c in critical_conflicts]
                reasons.append(f"Critical field conflicts: {', '.join(field_names)}")

        # Manual review flag reason
        if merged_business.needs_review:
            reasons.append("Manual review required")

        # Hybrid scoring reason
        if (
            conflicts_resolved
            and merged_business.confidence_level != ConfidenceLevel.LOW
        ):
            review_score = self._calculate_review_score(
                merged_business, conflicts_resolved
            )
            if review_score >= 0.8:
                reasons.append("High review score based on conflict complexity")
            elif review_score >= 0.6:
                reasons.append("Medium review score based on conflict analysis")

        if not reasons:
            reasons.append("Uncertain match requiring review")

        return "; ".join(reasons)

    def _confidence_level_to_score(self, confidence_level: ConfidenceLevel) -> float:
        """Convert confidence level to numeric score."""
        level_scores = {
            ConfidenceLevel.HIGH: 0.9,
            ConfidenceLevel.MEDIUM: 0.7,
            ConfidenceLevel.LOW: 0.4,
        }
        return level_scores.get(confidence_level, 0.5)

    def _calculate_review_score(
        self,
        merged_business: MergedBusinessData,
        conflicts_resolved: List[MergeConflict],
    ) -> float:
        """
        Calculate hybrid review score considering both conflict count and confidence.

        Returns:
            Score between 0.0 and 1.0, where higher scores indicate higher likelihood of needing review
        """
        if not conflicts_resolved:
            return 0.0

        # Base score from business confidence (lower confidence = higher review likelihood)
        confidence_score = self._confidence_level_to_score(
            merged_business.confidence_level
        )
        base_score = 1.0 - confidence_score  # Invert so lower confidence = higher score

        # Conflict complexity score (considers both count and individual confidence)
        conflict_score = self._calculate_conflict_complexity_score(conflicts_resolved)

        # Weighted combination: 40% business confidence, 60% conflict complexity
        # Increased conflict weight to ensure conflicts drive flagging decisions
        weights = {"confidence": 0.4, "conflict": 0.6}

        hybrid_score = (
            base_score * weights["confidence"] + conflict_score * weights["conflict"]
        )

        return min(hybrid_score, 1.0)

    def _calculate_priority_score(
        self,
        merged_business: MergedBusinessData,
        conflicts_resolved: List[MergeConflict],
    ) -> float:
        """
        Calculate hybrid priority score for determining review priority level.

        Returns:
            Score between 0.0 and 1.0, where higher scores indicate higher priority
        """
        if not conflicts_resolved:
            return 0.0

        # Business confidence factor (lower confidence = higher priority)
        confidence_factor = 1.0 - self._confidence_level_to_score(
            merged_business.confidence_level
        )

        # Conflict severity factor (considers count, confidence, and complexity)
        conflict_severity = self._calculate_conflict_severity_score(conflicts_resolved)

        # Weighted combination: 40% confidence, 60% conflict severity
        # Increased conflict weight to make conflicts drive priority decisions
        weights = {"confidence": 0.4, "conflict": 0.6}

        priority_score = (
            confidence_factor * weights["confidence"]
            + conflict_severity * weights["conflict"]
        )

        # Boost priority for multiple conflicts
        if len(conflicts_resolved) >= 2:
            priority_score = min(priority_score * 1.3, 1.0)

        return min(priority_score, 1.0)

    def _calculate_conflict_complexity_score(
        self, conflicts_resolved: List[MergeConflict]
    ) -> float:
        """
        Calculate conflict complexity score considering both count and individual confidence.

        Returns:
            Score between 0.0 and 1.0 indicating overall conflict complexity
        """
        if not conflicts_resolved:
            return 0.0

        # Count factor: more conflicts = higher complexity (increased sensitivity)
        count_factor = min(
            len(conflicts_resolved) / 3.0, 1.0
        )  # Cap at 3 conflicts, increased sensitivity

        # Confidence factor: lower confidence conflicts = higher complexity (increased sensitivity)
        avg_confidence = sum(c.confidence for c in conflicts_resolved) / len(
            conflicts_resolved
        )
        confidence_factor = (
            1.0 - avg_confidence
        )  # Invert so lower confidence = higher complexity

        # Complexity factor: consider field importance and resolution strategy
        complexity_factors = []
        for conflict in conflicts_resolved:
            # Critical fields get higher weight
            field_weight = self._get_field_importance_weight(conflict.field_name)
            # Resolution strategy affects complexity
            strategy_weight = self._get_resolution_strategy_weight(
                conflict.resolution_strategy
            )

            field_complexity = (
                (1.0 - conflict.confidence) * field_weight * strategy_weight
            )
            complexity_factors.append(field_complexity)

        avg_complexity = (
            sum(complexity_factors) / len(complexity_factors)
            if complexity_factors
            else 0.0
        )

        # Weighted combination: 40% count, 30% confidence, 30% complexity
        # Increased count weight to make conflict count more significant
        weights = {"count": 0.4, "confidence": 0.3, "complexity": 0.3}

        complexity_score = (
            count_factor * weights["count"]
            + confidence_factor * weights["confidence"]
            + avg_complexity * weights["complexity"]
        )

        # Boost score for multiple conflicts to ensure flagging
        if len(conflicts_resolved) >= 2:
            complexity_score = min(complexity_score * 1.5, 1.0)

        return min(complexity_score, 1.0)

    def _calculate_conflict_severity_score(
        self, conflicts_resolved: List[MergeConflict]
    ) -> float:
        """
        Calculate conflict severity score for priority determination.

        Returns:
            Score between 0.0 and 1.0 indicating conflict severity
        """
        if not conflicts_resolved:
            return 0.0

        # Count severity: increased sensitivity for multiple conflicts
        count_severity = min(
            len(conflicts_resolved) / 2.0, 1.0
        )  # Cap at 2 conflicts for severity

        # Confidence severity: lower confidence = higher severity
        # Handle both real MergeConflict objects and Mock objects safely
        confidence_values = []
        for c in conflicts_resolved:
            if hasattr(c, "confidence") and c.confidence is not None:
                confidence_values.append(c.confidence)

        if confidence_values:
            avg_confidence = sum(confidence_values) / len(confidence_values)
            confidence_severity = 1.0 - avg_confidence
        else:
            confidence_severity = 0.5  # Default severity for Mock objects

        # Field criticality: some fields are more critical than others
        critical_fields = ["phone", "website", "email", "address", "name"]
        critical_conflicts = [
            c for c in conflicts_resolved if c.field_name in critical_fields
        ]
        criticality_factor = (
            len(critical_conflicts) / len(conflicts_resolved)
            if conflicts_resolved
            else 0.0
        )

        # Weighted combination: 50% count, 30% confidence, 20% criticality
        # Increased count weight to make conflict count drive severity
        weights = {"count": 0.5, "confidence": 0.3, "criticality": 0.2}

        severity_score = (
            count_severity * weights["count"]
            + confidence_severity * weights["confidence"]
            + criticality_factor * weights["criticality"]
        )

        # Boost severity for multiple conflicts
        if len(conflicts_resolved) >= 2:
            severity_score = min(severity_score * 1.4, 1.0)

        return min(severity_score, 1.0)

    def _get_field_importance_weight(self, field_name: str) -> float:
        """Get importance weight for a field based on business criticality."""
        field_weights = {
            "name": 1.0,  # Most critical
            "phone": 0.9,  # Very critical
            "website": 0.8,  # Important
            "email": 0.8,  # Important
            "address": 0.7,  # Important
            "rating": 0.5,  # Medium importance
            "categories": 0.4,  # Lower importance
            "hours": 0.3,  # Lower importance
            "photos": 0.2,  # Least critical
        }
        return field_weights.get(field_name, 0.5)

    def _get_resolution_strategy_weight(self, strategy: str) -> float:
        """Get complexity weight for resolution strategy."""
        strategy_weights = {
            "completeness": 0.8,  # Medium complexity
            "accuracy": 0.9,  # High complexity
            "recency": 0.7,  # Lower complexity
            "manual": 1.0,  # Highest complexity
            "default": 0.6,  # Default complexity
        }
        return strategy_weights.get(strategy, 0.6)
