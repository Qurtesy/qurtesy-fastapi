from sqlalchemy.orm import Session

class CRUDBase:
    def __init__(self, model):
        self.model = model

    def get(self, db: Session, id: int):
        return db.query(self.model).filter(self.model.id == id).first()

    def get_all(self, db: Session):
        return db.query(self.model).all()

    def create(self, db: Session, obj_in):
        db_obj = self.model(**obj_in.dict())
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj

    def update(self, db: Session, obj_in):
        db_obj = db.query(self.model).filter(self.model.id == obj_in.id).first()
        for field, value in obj_in.dict().items():
            setattr(db_obj, field, value)
        db.commit()
        db.refresh(db_obj)
        return db_obj

    def delete(self, db: Session, id: int):
        obj = db.query(self.model).filter(self.model.id == id).first()
        db.delete(obj)
        db.commit()
        return obj

    def bulk_upsert(self, db: Session, objs_in):
        db_objs = [self.model(**obj.dict()) for obj in objs_in]
        db.bulk_save_objects(db_objs)
        db.commit()
        return db_objs
