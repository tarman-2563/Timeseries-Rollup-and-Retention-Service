from sqlalchemy.orm import Session

class QueryService:
    def __init__(self,db:Session):
        self.db=db
    