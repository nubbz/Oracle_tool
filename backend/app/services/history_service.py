from sqlalchemy.orm import Session
from app.models.history import History


class HistoryService:
    def list(self, db: Session, user_id: int, tool: str = None, page: int = 1, page_size: int = 20) -> tuple[list[History], int]:
        q = db.query(History).filter(History.user_id == user_id)
        if tool:
            q = q.filter(History.tool == tool)
        total = q.count()
        items = q.order_by(History.created_at.desc()).offset((page - 1) * page_size).limit(page_size).all()
        return items, total

    def get(self, db: Session, user_id: int, history_id: int) -> History | None:
        return db.query(History).filter(History.id == history_id, History.user_id == user_id).first()

    def delete(self, db: Session, user_id: int, history_id: int) -> bool:
        h = self.get(db, user_id, history_id)
        if not h:
            return False
        db.delete(h)
        db.commit()
        return True

    def delete_all(self, db: Session, user_id: int) -> int:
        count = db.query(History).filter(History.user_id == user_id).count()
        db.query(History).filter(History.user_id == user_id).delete()
        db.commit()
        return count
