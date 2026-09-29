from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Text, Boolean
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.core.database import Base

class Certificate(Base):
    __tablename__ = "certificates"

    id = Column(Integer, primary_key=True, index=True)
    certificate_id = Column(String, unique=True, index=True, nullable=False)
    certificate_type = Column(String, nullable=False)  # educational, professional, achievement, license, etc.
    holder_name = Column(String, nullable=False)
    institution_name = Column(String, nullable=False)
    qualification_name = Column(String, nullable=False)
    category_id = Column(Integer, ForeignKey("categories.id"), nullable=True)
    image_path = Column(String, nullable=True)
    image_hash = Column(String, nullable=True)
    description = Column(Text, nullable=True)

    # Certificate specific fields
    issued_at = Column(DateTime(timezone=True), nullable=True)
    expiry_date = Column(DateTime(timezone=True), nullable=True)
    is_revoked = Column(Boolean, default=False, nullable=False)

    # Blockchain related
    blockchain_tx_hash = Column(String, nullable=True)
    qr_code_hash = Column(String, unique=True, nullable=True)
    qr_code_path = Column(String, nullable=True)

    # Ownership
    issued_by = Column(Integer, ForeignKey("users.id"), nullable=False)
    current_holder = Column(Integer, ForeignKey("users.id"), nullable=True)

    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relationships
    category = relationship("Category", back_populates="certificates")
