import time
import os
import sys

# Add backend directory to sys.path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.db.session import SessionLocal
from app.db.models import Dataset, MLModel, AuditRun, AuditStatus, User
from app.worker import run_full_audit_task

def trigger_limit_break_audit():
    db = SessionLocal()
    try:
        dataset = db.query(Dataset).first()
        model = db.query(MLModel).first()
        user = db.query(User).first()
        
        if not dataset or not model:
            print("❌ Cannot find Dataset or Model in DB!")
            return
            
        print(f"✅ Found Dataset: {dataset.name}")
        print(f"✅ Found ML Model: {model.name}")
        print("🚀 Triggering Hyperparameter Tuning ML Task (RandomizedSearchCV)...")

        # Create Audit Run
        audit = AuditRun(
            dataset_id=dataset.id,
            model_id=model.id,
            triggered_by=user.id if user else None,
            status=AuditStatus.RUNNING,
            progress=0
        )
        db.add(audit)
        db.commit()
        db.refresh(audit)
        
        audit_id_str = str(audit.id)
        
        # Dispatch Celery
        run_full_audit_task.delay(audit_id_str)
        
        print("🕒 Waiting for Celery to finish (Your CPU will hit 100% for a bit!)...")
        
        while True:
            db.expire(audit)
            if audit.status in [AuditStatus.PASSED, AuditStatus.FLAGGED, AuditStatus.BLOCKED]:
                print(f"\n🎉 Task Completed! Final Status: {audit.status}")
                print(f"📊 Overall Accuracy:      {audit.overall_accuracy}")
                print(f"⚖️  Demographic Parity:   {audit.demographic_parity}")
                print(f"⚠️  Disparate Impact:     {audit.disparate_impact}")
                print(f"🔍 Equalized Odds TPR:   {audit.equalized_odds_tpr}")
                print(f"🏁 Finished at:          {audit.completed_at}")
                break
                
            print(f"   ... Progress: {audit.progress}%", end='\r')
            time.sleep(3)
            
    finally:
        db.close()

if __name__ == "__main__":
    trigger_limit_break_audit()
