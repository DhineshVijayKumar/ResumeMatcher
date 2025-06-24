from sqlalchemy.orm import Session
from app.utils.exceptions import PostgressNoRowFound

class GenericDBService:
    def __init__(self, db: Session, model):
        self.db = db
        self.model = model

    def create(self, schema_obj):
        db_obj = self.model(**schema_obj.model_dump())
        self.db.add(db_obj)
        self.db.flush()
        self.db.refresh(db_obj)
        return db_obj

    def get_all(self):
        return self.db.query(self.model).all()

    def get_by_id(self, obj_id: int):
        result = self.db.query(self.model).filter(self.model.id == obj_id).first()
        if result is None:
            raise PostgressNoRowFound(name="PostgressNoRowFound", message="No such record")
        return result

    def update(self, obj_id: int, schema_obj):
        db_obj = self.db.query(self.model).filter(self.model.id == obj_id).first()
        if db_obj is None:
            raise PostgressNoRowFound(name="PostgressNoRowFound", message="No such record")
        for key, value in schema_obj.model_dump().items():
            setattr(db_obj, key, value)
        return db_obj

    def delete(self, obj_id: int):
        db_obj = self.db.query(self.model).filter(self.model.id == obj_id).first()
        if db_obj is None:
            raise PostgressNoRowFound(name="PostgressNoRowFound", message="No such record")
        self.db.delete(db_obj)
        return db_obj

    def commit(self):
        self.db.commit()

    def refresh(self, instance):
        self.db.refresh(instance)

    def rollback(self):
        self.db.rollback()
