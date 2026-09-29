from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime
from app.core.database import get_db
from app.core.deps import get_current_user, require_role
from app.models.user import User
from app.models.certificate import Certificate
from app.schemas.certificate import CertificateCreate, CertificateResponse, CertificateVerification, TransferCertificate, RevokeCertificate
from app.services.blockchain import blockchain_service
from app.services.qr_service import qr_service
import hashlib
import os

router = APIRouter(prefix="/api/certificates", tags=["Certificates"])

@router.post("/issue", response_model=CertificateResponse)
def issue_certificate(
    certificate_data: CertificateCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role("teacher"))
):
    """Issue a new certificate (Teacher/Issuer only)"""
    # Check if certificate ID already exists
    if db.query(Certificate).filter(Certificate.certificate_id == certificate_data.certificate_id).first():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Certificate ID already exists"
        )

    # Generate image hash
    image_hash = hashlib.sha256(f"{certificate_data.certificate_id}{certificate_data.holder_name}".encode()).hexdigest()

    # Issue on blockchain
    if not current_user.wallet_address:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User wallet address not configured"
        )

    # Convert expiry_date to timestamp (0 if no expiry)
    expiry_timestamp = 0
    if certificate_data.expiry_date:
        expiry_timestamp = int(certificate_data.expiry_date.timestamp())

    tx_hash = blockchain_service.issue_certificate(
        certificate_data.certificate_id,
        certificate_data.certificate_type,
        certificate_data.holder_name,
        certificate_data.institution_name,
        certificate_data.qualification_name,
        image_hash,
        expiry_timestamp,
        current_user.wallet_address
    )

    if not tx_hash:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to issue certificate on blockchain"
        )

    # Generate QR code
    qr_hash = qr_service.generate_qr_hash(certificate_data.certificate_id)
    qr_path, _ = qr_service.create_qr_code(certificate_data.certificate_id, qr_hash)

    # Link QR code on blockchain
    blockchain_service.link_qr_code(certificate_data.certificate_id, qr_hash, current_user.wallet_address)

    # Save to database
    db_certificate = Certificate(
        certificate_id=certificate_data.certificate_id,
        certificate_type=certificate_data.certificate_type,
        holder_name=certificate_data.holder_name,
        institution_name=certificate_data.institution_name,
        qualification_name=certificate_data.qualification_name,
        category_id=certificate_data.category_id,
        description=certificate_data.description,
        image_hash=image_hash,
        blockchain_tx_hash=tx_hash,
        qr_code_hash=qr_hash,
        qr_code_path=qr_path,
        issued_by=current_user.id,
        current_holder=current_user.id,
        issued_at=datetime.utcnow(),
        expiry_date=certificate_data.expiry_date,
        is_revoked=False
    )

    db.add(db_certificate)
    db.commit()
    db.refresh(db_certificate)

    return db_certificate

@router.get("/", response_model=List[CertificateResponse])
def get_all_certificates(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get all certificates"""
    certificates = db.query(Certificate).offset(skip).limit(limit).all()
    return certificates

@router.get("/{certificate_id}", response_model=CertificateResponse)
def get_certificate(
    certificate_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get certificate by ID"""
    certificate = db.query(Certificate).filter(Certificate.certificate_id == certificate_id).first()
    if not certificate:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Certificate not found"
        )
    return certificate

@router.post("/transfer", response_model=dict)
def transfer_certificate(
    transfer_data: TransferCertificate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Transfer certificate ownership"""
    # Get certificate
    certificate = db.query(Certificate).filter(Certificate.certificate_id == transfer_data.certificate_id).first()
    if not certificate:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Certificate not found"
        )

    # Check if certificate is revoked
    if certificate.is_revoked:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot transfer revoked certificate"
        )

    # Check if current user holds the certificate
    if certificate.current_holder != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You don't hold this certificate"
        )

    # Find new holder
    new_holder = db.query(User).filter(User.wallet_address == transfer_data.new_holder_address).first()
    if not new_holder:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="New holder not found"
        )

    # Transfer on blockchain
    if not current_user.wallet_address:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User wallet address not configured"
        )

    success = blockchain_service.transfer_certificate(
        transfer_data.certificate_id,
        transfer_data.new_holder_address,
        current_user.wallet_address
    )

    if not success:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to transfer certificate on blockchain"
        )

    # Update database
    certificate.current_holder = new_holder.id
    db.commit()

    return {
        "message": "Certificate transferred successfully",
        "certificate_id": certificate.certificate_id,
        "from": current_user.username,
        "to": new_holder.username
    }

@router.post("/revoke", response_model=dict)
def revoke_certificate(
    revoke_data: RevokeCertificate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role("teacher"))
):
    """Revoke a certificate (Issuer/Admin only)"""
    # Get certificate
    certificate = db.query(Certificate).filter(Certificate.certificate_id == revoke_data.certificate_id).first()
    if not certificate:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Certificate not found"
        )

    # Check if already revoked
    if certificate.is_revoked:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Certificate already revoked"
        )

    # Check if current user is the issuer or admin
    if certificate.issued_by != current_user.id and current_user.role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only the issuer or admin can revoke this certificate"
        )

    # Revoke on blockchain
    if not current_user.wallet_address:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User wallet address not configured"
        )

    success = blockchain_service.revoke_certificate(
        revoke_data.certificate_id,
        current_user.wallet_address
    )

    if not success:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to revoke certificate on blockchain"
        )

    # Update database
    certificate.is_revoked = True
    db.commit()

    return {
        "message": "Certificate revoked successfully",
        "certificate_id": certificate.certificate_id,
        "revoked_by": current_user.username,
        "reason": revoke_data.reason
    }

@router.get("/verify/{certificate_id}", response_model=CertificateVerification)
def verify_certificate(
    certificate_id: str,
    db: Session = Depends(get_db)
):
    """Verify certificate authenticity (Public)"""
    # Get certificate from database
    certificate = db.query(Certificate).filter(Certificate.certificate_id == certificate_id).first()

    # Verify on blockchain
    default_account = blockchain_service.accounts[0] if blockchain_service.accounts else None
    if not default_account:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Blockchain not available"
        )

    verification_result = blockchain_service.verify_certificate(certificate_id, default_account)

    if "error" in verification_result:
        return CertificateVerification(
            certificate_id=certificate_id,
            is_valid=False,
            is_revoked=False,
            is_expired=False,
            certificate_details=None,
            lifecycle=[],
            message="Certificate not found on blockchain"
        )

    # Check expiry
    is_expired = False
    if certificate and certificate.expiry_date:
        is_expired = datetime.utcnow() > certificate.expiry_date

    is_valid = verification_result.get("is_valid", False) and not is_expired

    return CertificateVerification(
        certificate_id=certificate_id,
        is_valid=is_valid,
        is_revoked=verification_result.get("is_revoked", False),
        is_expired=is_expired,
        certificate_details=certificate,
        lifecycle=verification_result.get("lifecycle", []),
        message="Valid" if is_valid else ("Expired" if is_expired else "Revoked" if verification_result.get("is_revoked") else "Invalid")
    )

@router.get("/verify-qr/{qr_hash}", response_model=CertificateVerification)
def verify_by_qr_code(
    qr_hash: str,
    db: Session = Depends(get_db)
):
    """Verify certificate by QR code hash (Public)"""
    # Find certificate with this QR hash
    certificate = db.query(Certificate).filter(Certificate.qr_code_hash == qr_hash).first()

    # Verify on blockchain
    default_account = blockchain_service.accounts[0] if blockchain_service.accounts else None
    if not default_account:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Blockchain not available"
        )

    verification_result = blockchain_service.verify_by_qr(qr_hash, default_account)

    if "error" in verification_result or not verification_result.get("is_valid"):
        return CertificateVerification(
            certificate_id=verification_result.get("certificate_id", "unknown"),
            is_valid=False,
            is_revoked=False,
            is_expired=False,
            certificate_details=None,
            lifecycle=[],
            message="Invalid QR code or certificate not verified"
        )

    # Check expiry
    is_expired = False
    if certificate and certificate.expiry_date:
        is_expired = datetime.utcnow() > certificate.expiry_date

    is_valid = verification_result.get("is_valid", False) and not is_expired

    return CertificateVerification(
        certificate_id=verification_result.get("certificate_id"),
        is_valid=is_valid,
        is_revoked=verification_result.get("is_revoked", False),
        is_expired=is_expired,
        certificate_details=certificate,
        lifecycle=verification_result.get("lifecycle", []),
        message="Valid certificate" if is_valid else ("Expired" if is_expired else "Revoked" if verification_result.get("is_revoked") else "Invalid")
    )

