
from sqlalchemy import Column, String
from sqlalchemy.orm import relationship

from .base import Base

class ParentDir(Base):
    path = Column(String)
