# Quick Start Guide

Get the Certificate Verification System running in 5 minutes!

## Prerequisites Check

Before starting, ensure you have:

- [ ] Node.js installed (v16+): `node --version`
- [ ] Python installed (3.8+): `python --version`
- [ ] npm installed: `npm --version`
- [ ] Ganache installed or ganache-cli

## Step-by-Step Setup

### Step 1: Start Ganache (Blockchain)

**Option A: Ganache GUI**
1. Open Ganache application
2. Create new workspace or quickstart
3. Ensure it's running on port **7545**

**Option B: Ganache CLI**
```bash
npm install -g ganache-cli
ganache-cli -p 7545
```

Keep this terminal running!

### Step 2: Deploy Smart Contracts

Open a new terminal:

```bash
# Navigate to blockchain folder
cd blockchain

# Install dependencies (first time only)
npm install

# Compile contracts
npx truffle compile

# Deploy to Ganache
npx truffle migrate --reset
```

You should see: ✅ "Contract deployed at: 0x..."

### Step 3: Start Backend

Open a new terminal:

```bash
# Navigate to backend folder
cd backend

# Create virtual environment (first time only)
python -m venv venv

# Activate virtual environment
# On macOS/Linux:
source venv/bin/activate
# On Windows:
venv\Scripts\activate

# Install dependencies (first time only)
pip install -r requirements.txt

# Start FastAPI server
python -m app.main
```

You should see: ✅ "Connected to Ganache" and "Contract loaded"

Backend running at: **http://localhost:8000**

### Step 4: Start Frontend

Open a new terminal:

```bash
# Navigate to frontend folder
cd frontend

# Install dependencies (first time only)
npm install

# Start development server
npm run dev
```

Frontend running at: **http://localhost:3000**

## First Steps

### 1. Register an Admin User

1. Open browser: http://localhost:3000
2. Click "Register"
3. Fill in:
   - Username: `admin`
   - Email: `admin@example.com`
   - Password: `admin123`
   - Role: `Admin`
4. Click "Register"

### 2. Login

1. Click "Login"
2. Enter username and password
3. You'll be redirected to Admin Dashboard

### 3. Create a Category (Optional)

1. In Admin Dashboard, go to "Categories" tab
2. Create a category (e.g., "Electronics")

### 4. Register a Manager

1. Logout (or open incognito window)
2. Register new user:
   - Username: `manager1`
   - Email: `manager@example.com`
   - Password: `manager123`
   - Role: `Manager`

### 5. Issue a Certificate

1. Login as Manager
2. Go to "Issue Certificate" tab
3. Fill in certificate details:
   - Certificate ID: `CERT-001`
   - Holder Name: `John Doe`
   - Institution Name: `University of Technology`
   - Qualification Name: `Bachelor of Computer Science`
   - Certificate Type: `Degree`
   - Expiry Date: `2030-12-31`
4. Click "Issue Certificate"
5. Wait for blockchain confirmation
6. Check "All Certificates" tab to see issued certificate with QR code

### 6. Verify Certificate (Public)

1. Open new incognito window or logout
2. Go to: http://localhost:3000/verify
3. Select "Certificate ID" method
4. Enter: `CERT-001`
5. Click "Verify Certificate"
6. See verification result with expiry status and lifecycle!

## Quick Commands Reference

### Start All Services

**Terminal 1 - Ganache:**
```bash
ganache-cli -p 7545
```

**Terminal 2 - Backend:**
```bash
cd backend
source venv/bin/activate  # or venv\Scripts\activate on Windows
python -m app.main
```

**Terminal 3 - Frontend:**
```bash
cd frontend
npm run dev
```

### Redeploy Smart Contracts

```bash
cd blockchain
npx truffle migrate --reset
# Then restart backend
```

### Reset Database

```bash
cd backend
rm certificate_auth.db
# Restart backend (will recreate database)
```

## Verification URLs

- Frontend: http://localhost:3000
- Backend API: http://localhost:8000
- API Docs: http://localhost:8000/docs
- Health Check: http://localhost:8000/api/health

## Common Issues

### Issue: "Contract not loaded"
**Solution**: Deploy smart contracts first (`truffle migrate --reset`)

### Issue: "Failed to connect to Ganache"
**Solution**: Ensure Ganache is running on port 7545

### Issue: Backend won't start
**Solution**:
1. Activate virtual environment
2. Install requirements: `pip install -r requirements.txt`

### Issue: Frontend shows connection error
**Solution**: Make sure backend is running on port 8000

## Test the Complete Flow

1. **Register users**: Admin, Manager, Seller
2. **Admin**: Create categories
3. **Manager**: Issue certificate → QR code generated
4. **Seller**: Transfer certificate to another user
5. **Public**: Verify certificate via QR code, check expiry status
6. **Check**: Lifecycle shows all transfers!
7. **Manager**: Revoke certificate if needed

## Next Steps

- Read full documentation: `README.md`
- Explore API documentation: http://localhost:8000/docs
- Test with multiple certificates
- Try NFC simulation in verification page
- View blockchain transactions in Ganache
- Test certificate expiry and revocation features

## Need Help?

- Check `README.md` for detailed documentation
- Review API docs at `/docs` endpoint
- Contact: dipti.qriocity@gmail.com

Happy testing!
