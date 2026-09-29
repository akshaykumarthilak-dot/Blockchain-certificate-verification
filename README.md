# Blockchain-Enabled Certificate Verification System

A comprehensive blockchain-based certificate verification system designed to ensure authenticity and track certificate lifecycle throughout the issuance and transfer process.

## Project Overview

This system provides an immutable, verifiable record of certificate authenticity using blockchain technology, QR codes, and simulated NFC tags. It enables issuers, institutions, and certificate holders to verify certificate authenticity at any point in the certificate lifecycle.

## Key Features

- **Blockchain Integration**: Ethereum-based smart contracts for immutable certificate registration
- **Multi-Role System**: Admin, Manager, and Seller dashboards with role-based access control
- **QR Code Verification**: Auto-generated QR codes linked to blockchain records
- **NFC Simulation**: Simulated NFC tag integration for demo purposes
- **Certificate Lifecycle Tracking**: Complete chain of custody from issuer to certificate holder
- **Certificate Revocation**: Real-time flagging and revocation of invalid certificates
- **Expiry Tracking**: Automatic tracking of certificate expiration dates
- **Session-Based Authentication**: Secure user authentication system

## Tech Stack

### Blockchain
- **Platform**: Ethereum (Ganache - Private Network)
- **Smart Contracts**: Solidity 0.8.19
- **Framework**: Truffle
- **Interaction**: Web3.py

### Backend
- **Framework**: FastAPI (Python)
- **Database**: SQLite3
- **Authentication**: Session-based with JWT
- **QR Generation**: qrcode library
- **Cryptography**: SHA-256 hashing

### Frontend
- **Framework**: React 18
- **Build Tool**: Vite
- **Routing**: React Router v6
- **HTTP Client**: Axios
- **QR Scanner**: html5-qrcode

## Project Structure

```
Certificate Verification/
├── blockchain/              # Smart contracts and Truffle configuration
│   ├── contracts/          # Solidity smart contracts
│   ├── migrations/         # Deployment scripts
│   ├── build/              # Compiled contracts (generated)
│   └── truffle-config.js   # Truffle configuration
│
├── backend/                # FastAPI backend application
│   ├── app/
│   │   ├── core/          # Database, security, dependencies
│   │   ├── models/        # SQLAlchemy models
│   │   ├── schemas/       # Pydantic schemas
│   │   ├── routers/       # API endpoints
│   │   ├── services/      # Business logic (blockchain, QR)
│   │   └── main.py        # FastAPI app entry point
│   ├── static/            # Generated QR codes
│   ├── requirements.txt   # Python dependencies
│   └── certificate_auth.db    # SQLite database (generated)
│
└── frontend/               # React frontend application
    ├── src/
    │   ├── components/    # Reusable components
    │   ├── pages/         # Page components
    │   ├── context/       # React context (Auth)
    │   ├── services/      # API service
    │   ├── App.jsx        # Main app component
    │   └── main.jsx       # Entry point
    ├── public/            # Static assets
    └── package.json       # Node dependencies
```

## Setup Instructions

### Prerequisites

- Node.js (v16 or higher)
- Python 3.8+
- Ganache (for local Ethereum blockchain)
- npm or yarn

### 1. Blockchain Setup

```bash
cd blockchain

# Install dependencies
npm install

# Start Ganache
# Open Ganache GUI and create a new workspace
# Or use ganache-cli: ganache-cli -p 7545

# Compile contracts
npx truffle compile

# Deploy contracts
npx truffle migrate --reset
```

### 2. Backend Setup

```bash
cd backend

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Run the server
python -m app.main
# Or: uvicorn app.main:app --reload
```

Backend will run on: `http://localhost:8000`

### 3. Frontend Setup

```bash
cd frontend

# Install dependencies
npm install

# Run development server
npm run dev
```

Frontend will run on: `http://localhost:3000`

## Usage Guide

### User Roles

1. **Admin**
   - Manage users (activate/deactivate)
   - Create and manage certificate categories
   - View system statistics

2. **Manager**
   - Issue certificates on blockchain
   - Generate QR codes and NFC tags
   - View all issued certificates
   - Revoke certificates when needed

3. **Seller**
   - Transfer certificate ownership
   - View owned certificates
   - Record transfers on blockchain

4. **Consumer** (Public)
   - Verify certificate authenticity via QR/NFC
   - View certificate lifecycle
   - No authentication required

### Workflow

1. **Admin** creates categories and manages users
2. **Manager** issues a certificate:
   - Certificate details stored on blockchain (certificate_id, holder_name, institution_name, qualification_name, certificate_type, expiry_date)
   - QR code generated and linked
   - NFC UID simulated and linked
3. **Manager** transfers to certificate holder or revokes if needed
4. **Holder** can transfer certificate ownership to another party
5. **Public** scans QR/NFC to verify authenticity and check expiry status

## API Endpoints

### Authentication
- `POST /api/auth/register` - Register new user
- `POST /api/auth/login` - Login
- `POST /api/auth/logout` - Logout
- `GET /api/auth/me` - Get current user

### Certificates
- `POST /api/certificates/register` - Issue certificate (Manager)
- `GET /api/certificates/` - Get all certificates
- `GET /api/certificates/{certificate_id}` - Get certificate details
- `POST /api/certificates/transfer` - Transfer ownership (Seller)
- `POST /api/certificates/revoke` - Revoke certificate (Manager)
- `GET /api/certificates/verify/{certificate_id}` - Verify by ID
- `GET /api/certificates/verify-qr/{qr_hash}` - Verify by QR
- `GET /api/certificates/verify-nfc/{nfc_uid}` - Verify by NFC

### Admin
- `GET /api/admin/users` - Get all users
- `PUT /api/admin/users/{id}/activate` - Activate user
- `PUT /api/admin/users/{id}/deactivate` - Deactivate user
- `POST /api/admin/categories` - Create category
- `GET /api/admin/categories` - Get all categories
- `GET /api/admin/stats` - Get system statistics

## Smart Contract Functions

### CertificateAuthentication.sol

Key functions:
- `registerCertificate()` - Issue new certificate
- `linkQRCode()` - Link QR code to certificate
- `linkNFCTag()` - Link NFC tag to certificate
- `transferCertificate()` - Transfer ownership
- `revokeCertificate()` - Revoke certificate
- `recordTransfer()` - Record transfer transaction
- `verifyCertificate()` - Verify authenticity
- `verifyByQRCode()` - Verify via QR
- `verifyByNFC()` - Verify via NFC
- `getCertificate()` - Get certificate details
- `getTransferHistory()` - Get lifecycle
- `checkExpiry()` - Check if certificate is expired

## Security Features

- SHA-256 hashing for certificate data
- Blockchain immutability
- Smart contract access control
- Session-based authentication
- Role-based authorization
- Duplicate detection
- Certificate revocation system
- Expiry date enforcement

## Testing

### Test User Accounts

After registration, you can create test accounts:

```
Admin:
- Username: admin
- Role: admin

Manager:
- Username: manager1
- Role: manager

Seller:
- Username: seller1
- Role: seller
```

### Test Certificate Issuance

1. Login as Manager
2. Navigate to "Issue Certificate"
3. Fill in details:
   - Certificate ID: CERT-001
   - Holder Name: John Doe
   - Institution Name: University of Technology
   - Qualification Name: Bachelor of Computer Science
   - Certificate Type: Degree
   - Expiry Date: 2030-12-31
4. Submit to register on blockchain

### Test Verification

1. Go to verification page (public)
2. Enter certificate ID or scan QR code
3. View verification result, expiry status, and lifecycle

## Troubleshooting

### Blockchain Connection Issues
- Ensure Ganache is running on port 7545
- Check truffle-config.js network settings
- Redeploy contracts if needed

### Backend Issues
- Verify Python dependencies installed
- Check if SQLite database created
- Ensure blockchain contract deployed

### Frontend Issues
- Clear browser cache
- Check API proxy configuration
- Verify backend is running

## Project Timeline

- **Deadline**: 12/14/2025
- **Status**: Development Complete

## Contact Information

- **Support/Sales**: dipti.qriocity@gmail.com
- **Client**: dipti@qriocity.com

## License

This project is developed for Qriocity.

## Acknowledgments

Built with Ethereum, FastAPI, and React for blockchain-enabled certificate verification.
