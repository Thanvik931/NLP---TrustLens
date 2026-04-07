"""
TrustLens AI — SQLAlchemy ORM Models
All 8 tables: User, Dataset, MLModel, AuditRun, BiasFlag,
ExplainabilityResult, EthicsCheck, GovernanceRule, ModelCard
"""

import uuid
from datetime import datetime

from sqlalchemy import (
    Boolean,
    Column,
    DateTime,
    Enum,
    Float,
    ForeignKey,
    Integer,
    String,
    Text,
)
from sqlalchemy.dialects.postgresql import JSON, UUID
from sqlalchemy.orm import relationship

from app.db.base import Base


# ---------------------------------------------------------------------------
# Enums
# ---------------------------------------------------------------------------

class UserRole(str):
    ADMIN = "ADMIN"
    AUDITOR = "AUDITOR"
    VIEWER = "VIEWER"


class AuditStatus(str):
    RUNNING = "RUNNING"
    PASSED = "PASSED"
    FLAGGED = "FLAGGED"
    BLOCKED = "BLOCKED"


# ---------------------------------------------------------------------------
# User
# ---------------------------------------------------------------------------

class User(Base):
    __tablename__ = "users"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    email = Column(String(255), unique=True, nullable=False, index=True)
    password_hash = Column(String(255), nullable=False)
    role = Column(
        Enum("ADMIN", "AUDITOR", "VIEWER", name="user_role_enum"),
        nullable=False,
        default="VIEWER",
    )
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    # relationships
    datasets = relationship("Dataset", back_populates="creator", lazy="select")
    audit_runs = relationship("AuditRun", back_populates="triggered_by_user", lazy="select")

    def __repr__(self) -> str:
        return f"<User {self.email} [{self.role}]>"


# ---------------------------------------------------------------------------
# Dataset
# ---------------------------------------------------------------------------

class Dataset(Base):
    __tablename__ = "datasets"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    name = Column(String(255), nullable=False)
    domain = Column(String(100), nullable=False)          # finance | healthcare | public_services
    description = Column(Text, nullable=True)
    file_path = Column(String(512), nullable=True)        # uploaded CSV path on server
    row_count = Column(Integer, nullable=True)
    feature_count = Column(Integer, nullable=True)
    sensitive_cols = Column(JSON, nullable=True)          # list of column names
    target_col = Column(String(100), nullable=True)
    created_by = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    # relationships
    creator = relationship("User", back_populates="datasets")
    audits = relationship("AuditRun", back_populates="dataset", lazy="select")

    def __repr__(self) -> str:
        return f"<Dataset {self.name}>"


# ---------------------------------------------------------------------------
# MLModel
# ---------------------------------------------------------------------------

class MLModel(Base):
    __tablename__ = "ml_models"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    name = Column(String(255), nullable=False)
    framework = Column(String(100), nullable=False)       # sklearn | xgboost | tensorflow | pytorch | custom
    domain = Column(String(100), nullable=False)
    description = Column(Text, nullable=True)
    model_file = Column(String(512), nullable=True)       # serialized model path (.pkl / .h5)
    is_active = Column(Boolean, default=True, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    # relationships
    audits = relationship("AuditRun", back_populates="model", lazy="select")
    governance_rules = relationship("GovernanceRule", back_populates="model", lazy="select")

    def __repr__(self) -> str:
        return f"<MLModel {self.name} [{self.framework}]>"


# ---------------------------------------------------------------------------
# GovernanceRule
# ---------------------------------------------------------------------------

class GovernanceRule(Base):
    __tablename__ = "governance_rules"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    model_id = Column(UUID(as_uuid=True), ForeignKey("ml_models.id"), nullable=False, index=True)
    name = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    category = Column(String(100), nullable=False)        # fairness | legal | safety | explainability
    threshold = Column(Float, nullable=True)
    metric = Column(String(100), nullable=True)           # which metric this rule checks
    is_active = Column(Boolean, default=True, nullable=False)

    # relationships
    model = relationship("MLModel", back_populates="governance_rules")
    ethics_checks = relationship("EthicsCheck", back_populates="rule", lazy="select")

    def __repr__(self) -> str:
        return f"<GovernanceRule {self.name} [{self.category}]>"


# ---------------------------------------------------------------------------
# AuditRun
# ---------------------------------------------------------------------------

class AuditRun(Base):
    __tablename__ = "audit_runs"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    dataset_id = Column(UUID(as_uuid=True), ForeignKey("datasets.id"), nullable=False, index=True)
    model_id = Column(UUID(as_uuid=True), ForeignKey("ml_models.id"), nullable=False, index=True)
    triggered_by = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=True)
    status = Column(
        Enum("RUNNING", "PASSED", "FLAGGED", "BLOCKED", name="audit_status_enum"),
        nullable=False,
        default="RUNNING",
        index=True,
    )
    celery_task_id = Column(String(255), nullable=True)
    progress = Column(Integer, default=0, nullable=False)

    # Fairness metrics
    demographic_parity = Column(Float, nullable=True)
    equalized_odds_tpr = Column(Float, nullable=True)
    equalized_odds_fpr = Column(Float, nullable=True)
    disparate_impact = Column(Float, nullable=True)

    # Performance metrics
    overall_auroc = Column(Float, nullable=True)
    overall_accuracy = Column(Float, nullable=True)
    subgroup_divergence = Column(Float, nullable=True)

    # Output
    audit_report_path = Column(String(512), nullable=True)

    # Timestamps
    started_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    completed_at = Column(DateTime, nullable=True)

    # relationships
    dataset = relationship("Dataset", back_populates="audits")
    model = relationship("MLModel", back_populates="audits")
    triggered_by_user = relationship("User", back_populates="audit_runs")
    bias_flags = relationship("BiasFlag", back_populates="audit", cascade="all, delete-orphan", lazy="select")
    explainability_results = relationship("ExplainabilityResult", back_populates="audit", cascade="all, delete-orphan", lazy="select")
    ethics_checks = relationship("EthicsCheck", back_populates="audit", cascade="all, delete-orphan", lazy="select")
    model_card = relationship("ModelCard", back_populates="audit", uselist=False, cascade="all, delete-orphan", lazy="select")

    def __repr__(self) -> str:
        return f"<AuditRun {self.id} [{self.status}] {self.progress}%>"


# ---------------------------------------------------------------------------
# BiasFlag
# ---------------------------------------------------------------------------

class BiasFlag(Base):
    __tablename__ = "bias_flags"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    audit_id = Column(UUID(as_uuid=True), ForeignKey("audit_runs.id"), nullable=False, index=True)
    bias_type = Column(String(100), nullable=False)       # demographic | proxy_variable | distributional
    affected_group = Column(String(255), nullable=True)
    severity = Column(String(50), nullable=False)         # low | medium | high | critical
    metric_name = Column(String(100), nullable=True)
    metric_value = Column(Float, nullable=True)
    threshold = Column(Float, nullable=True)
    description = Column(Text, nullable=True)
    mitigation_applied = Column(Boolean, default=False, nullable=False)
    mitigation_type = Column(String(100), nullable=True)  # reweighing | constraint | postprocessing
    before_value = Column(Float, nullable=True)
    after_value = Column(Float, nullable=True)
    detected_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    # relationships
    audit = relationship("AuditRun", back_populates="bias_flags")

    def __repr__(self) -> str:
        return f"<BiasFlag {self.bias_type} [{self.severity}] on audit {self.audit_id}>"


# ---------------------------------------------------------------------------
# ExplainabilityResult
# ---------------------------------------------------------------------------

class ExplainabilityResult(Base):
    __tablename__ = "explainability_results"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    audit_id = Column(UUID(as_uuid=True), ForeignKey("audit_runs.id"), nullable=False, index=True)
    method = Column(String(50), nullable=False)           # SHAP | LIME
    scope = Column(String(50), nullable=False)            # global | local
    feature_scores = Column(JSON, nullable=True)          # {feature_name: importance_score}
    prediction_id = Column(String(100), nullable=True)    # row index for local explanations
    fidelity_score = Column(Float, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    # relationships
    audit = relationship("AuditRun", back_populates="explainability_results")

    def __repr__(self) -> str:
        return f"<ExplainabilityResult {self.method} [{self.scope}] on audit {self.audit_id}>"


# ---------------------------------------------------------------------------
# EthicsCheck
# ---------------------------------------------------------------------------

class EthicsCheck(Base):
    __tablename__ = "ethics_checks"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    audit_id = Column(UUID(as_uuid=True), ForeignKey("audit_runs.id"), nullable=False, index=True)
    rule_id = Column(UUID(as_uuid=True), ForeignKey("governance_rules.id"), nullable=False, index=True)
    passed = Column(Boolean, nullable=False)
    reason = Column(Text, nullable=True)
    checked_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    # relationships
    audit = relationship("AuditRun", back_populates="ethics_checks")
    rule = relationship("GovernanceRule", back_populates="ethics_checks")

    def __repr__(self) -> str:
        return f"<EthicsCheck rule={self.rule_id} passed={self.passed}>"


# ---------------------------------------------------------------------------
# ModelCard
# ---------------------------------------------------------------------------

class ModelCard(Base):
    __tablename__ = "model_cards"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    audit_id = Column(UUID(as_uuid=True), ForeignKey("audit_runs.id"), unique=True, nullable=False, index=True)
    model_name = Column(String(255), nullable=True)
    intended_use = Column(Text, nullable=True)
    out_of_scope_use = Column(Text, nullable=True)
    training_data_desc = Column(Text, nullable=True)
    evaluation_data = Column(Text, nullable=True)
    performance_summary = Column(JSON, nullable=True)
    fairness_summary = Column(JSON, nullable=True)
    limitations = Column(Text, nullable=True)
    recommendations = Column(Text, nullable=True)
    generated_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    # relationships
    audit = relationship("AuditRun", back_populates="model_card")

    def __repr__(self) -> str:
        return f"<ModelCard for audit {self.audit_id}>"
