from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class CertificateBase(BaseModel):
    certificate_type: str
    holder_name: str
    institution_name: str
    qualification_name: str
    category_id: Optional[int] = None
    description: Optional[str] = None
    expiry_date: Optional[datetime] = None

class CertificateCreate(CertificateBase):
    certificate_id: str

class CertificateResponse(CertificateBase):
    id: int
    certificate_id: str
    image_path: Optional[str]
    image_hash: Optional[str]
    blockchain_tx_hash: Optional[str]
    qr_code_hash: Optional[str]
    qr_code_path: Optional[str]
    issued_by: int
    current_holder: Optional[int]
    issued_at: Optional[datetime]
    is_revoked: bool
    created_at: datetime

    class Config:
        from_attributes = True

class CertificateVerification(BaseModel):
    certificate_id: str
    is_valid: bool
    is_revoked: bool
    is_expired: bool
    certificate_details: Optional[CertificateResponse]
    lifecycle: list
    message: str

class TransferCertificate(BaseModel):
    certificate_id: str
    new_holder_address: str

class RevokeCertificate(BaseModel):
    certificate_id: str
    reason: Optional[str] = None
