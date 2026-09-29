import qrcode
import hashlib
import os
from typing import Tuple

class QRService:
    def __init__(self, output_dir: str = "static/qr_codes"):
        self.output_dir = output_dir
        os.makedirs(output_dir, exist_ok=True)

    def generate_qr_hash(self, product_id: str) -> str:
        """Generate a unique hash for QR code"""
        data = f"{product_id}-{os.urandom(16).hex()}"
        return hashlib.sha256(data.encode()).hexdigest()

    def create_qr_code(self, product_id: str, qr_hash: str) -> Tuple[str, str]:
        """Create QR code image and return file path and hash"""
        try:
            # Create QR code with product verification URL
            qr = qrcode.QRCode(
                version=1,
                error_correction=qrcode.constants.ERROR_CORRECT_L,
                box_size=10,
                border=4,
            )

            # QR code contains the hash for verification
            verification_data = {
                "type": "product_verification",
                "qr_hash": qr_hash,
                "product_id": product_id
            }

            qr.add_data(qr_hash)
            qr.make(fit=True)

            # Create image
            img = qr.make_image(fill_color="black", back_color="white")

            # Save image
            filename = f"{product_id}_{qr_hash[:8]}.png"
            filepath = os.path.join(self.output_dir, filename)
            img.save(filepath)

            return filepath, qr_hash

        except Exception as e:
            print(f"Error creating QR code: {str(e)}")
            return None, None

# Global QR service instance
qr_service = QRService()
