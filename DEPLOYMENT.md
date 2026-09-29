# Deployment Guide

This guide covers deploying the Certificate Verification System to production or staging environments.

## Important Notes

- This project is configured for **local development and demonstration**
- **Blockchain deployment is NOT included** as per project requirements
- For production use, additional security measures are required

## Production Checklist

### Security Hardening

1. **Change Secret Keys**
   ```python
   # backend/app/core/security.py
   SECRET_KEY = "CHANGE-THIS-TO-RANDOM-SECRET"

   # backend/app/main.py
   SessionMiddleware(secret_key="CHANGE-THIS-SECRET")
   ```

2. **Use Environment Variables**
   Create `.env` file:
   ```env
   SECRET_KEY=your-production-secret-key
   DATABASE_URL=postgresql://user:pass@host/db
   BLOCKCHAIN_RPC_URL=http://your-blockchain-node:8545
   CONTRACT_ADDRESS=0x...
   ALLOWED_ORIGINS=https://your-domain.com
   ```

3. **Update CORS Settings**
   ```python
   # backend/app/main.py
   allow_origins=["https://your-domain.com"]
   ```

4. **Enable HTTPS**
   - Use SSL certificates (Let's Encrypt)
   - Configure reverse proxy (Nginx)
   - Force HTTPS redirects

5. **Database Security**
   - Use PostgreSQL instead of SQLite
   - Enable authentication
   - Regular backups
   - Encrypted connections

## Backend Deployment

### Option 1: Docker

Create `backend/Dockerfile`:
```dockerfile
FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 8000

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

Build and run:
```bash
docker build -t certificate-auth-backend .
docker run -p 8000:8000 certificate-auth-backend
```

### Option 2: Traditional Server

1. **Install Dependencies**
   ```bash
   sudo apt update
   sudo apt install python3 python3-venv nginx
   ```

2. **Setup Application**
   ```bash
   cd /var/www/certificate-auth-backend
   python3 -m venv venv
   source venv/bin/activate
   pip install -r requirements.txt
   ```

3. **Create Systemd Service**
   `/etc/systemd/system/certificate-auth.service`:
   ```ini
   [Unit]
   Description=Certificate Verification Backend
   After=network.target

   [Service]
   User=www-data
   WorkingDirectory=/var/www/certificate-auth-backend
   Environment="PATH=/var/www/certificate-auth-backend/venv/bin"
   ExecStart=/var/www/certificate-auth-backend/venv/bin/uvicorn app.main:app --host 0.0.0.0 --port 8000

   [Install]
   WantedBy=multi-user.target
   ```

4. **Start Service**
   ```bash
   sudo systemctl start certificate-auth
   sudo systemctl enable certificate-auth
   ```

5. **Configure Nginx**
   `/etc/nginx/sites-available/certificate-auth`:
   ```nginx
   server {
       listen 80;
       server_name api.your-domain.com;

       location / {
           proxy_pass http://localhost:8000;
           proxy_set_header Host $host;
           proxy_set_header X-Real-IP $remote_addr;
       }
   }
   ```

## Frontend Deployment

### Build for Production

```bash
cd frontend
npm run build
```

This creates a `dist/` folder with optimized static files.

### Option 1: Static Hosting (Netlify, Vercel)

1. Connect GitHub repository
2. Set build command: `npm run build`
3. Set publish directory: `dist`
4. Add environment variables:
   - `VITE_API_URL=https://api.your-domain.com`

### Option 2: Nginx Static Files

```nginx
server {
    listen 80;
    server_name your-domain.com;

    root /var/www/certificate-auth-frontend/dist;
    index index.html;

    location / {
        try_files $uri $uri/ /index.html;
    }

    location /api {
        proxy_pass http://localhost:8000;
        proxy_set_header Host $host;
    }
}
```

## Blockchain Considerations

### Local Development
- Uses Ganache on port 7545
- Private blockchain network
- Not persistent across restarts

### Production Options (Not Implemented)

If you need to deploy to production blockchain:

1. **Ethereum Testnet** (Sepolia, Goerli)
   - Free for testing
   - Requires test ETH
   - Public blockchain

2. **Ethereum Mainnet**
   - Real ETH required
   - High gas costs
   - Production-ready

3. **Private Network**
   - Hyperledger Fabric
   - Quorum
   - Full control

**Note**: Current implementation is designed for local demonstration only.

## Database Migration

### SQLite to PostgreSQL

1. **Install PostgreSQL**
   ```bash
   sudo apt install postgresql
   ```

2. **Update Backend Configuration**
   ```python
   # app/core/database.py
   SQLALCHEMY_DATABASE_URL = "postgresql://user:password@localhost/certificateauth"
   ```

3. **Create Database**
   ```bash
   sudo -u postgres createdb certificateauth
   sudo -u postgres createuser certificateauth_user
   ```

## Monitoring & Logging

### Application Logging

Add to `backend/app/main.py`:
```python
import logging

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('app.log'),
        logging.StreamHandler()
    ]
)
```

### Health Checks

Monitor:
- `GET /api/health` - Backend health
- Blockchain connection status
- Database connectivity

### Performance Monitoring

Consider adding:
- Application Performance Monitoring (APM)
- Error tracking (Sentry)
- Log aggregation (ELK Stack)

## Backup Strategy

### Database Backups

```bash
# SQLite
cp certificate_auth.db backup/certificate_auth_$(date +%Y%m%d).db

# PostgreSQL
pg_dump certificateauth > backup/certificateauth_$(date +%Y%m%d).sql
```

### Smart Contract Backups

- Keep contract source code in version control
- Document deployment addresses
- Backup contract ABIs

## Scaling Considerations

### Backend Scaling

1. **Horizontal Scaling**
   - Deploy multiple backend instances
   - Use load balancer (Nginx, HAProxy)
   - Session storage in Redis

2. **Caching**
   - Cache blockchain queries
   - Use Redis for session storage
   - CDN for static assets

### Database Scaling

- Read replicas for queries
- Connection pooling
- Query optimization
- Indexes on frequent lookups

## Security Best Practices

1. **API Security**
   - Rate limiting
   - Input validation
   - SQL injection prevention
   - XSS protection

2. **Authentication**
   - Strong password policies
   - Account lockout after failed attempts
   - Two-factor authentication (optional)

3. **Network Security**
   - Firewall rules
   - DDoS protection
   - VPN for admin access

4. **Regular Updates**
   - Keep dependencies updated
   - Security patches
   - Monitor CVE databases

## Testing Before Deployment

```bash
# Backend tests
cd backend
pytest

# Frontend tests
cd frontend
npm test

# Integration tests
# Test complete user flow
```

## Rollback Plan

1. Keep previous version deployed
2. Database migration rollback scripts
3. Smart contract upgrade mechanism
4. Quick revert procedure documented

## Support & Maintenance

- Monitor error logs daily
- Regular security audits
- Performance optimization
- User feedback integration

## Cost Estimation (Approximate)

For production deployment:

- Server (VPS): $10-50/month
- Database: $15-100/month (if using managed service)
- SSL Certificate: Free (Let's Encrypt)
- Domain: $10-20/year
- Monitoring tools: $0-50/month

**Note**: Blockchain deployment costs not included (gas fees variable)

## Contact

For deployment assistance:
- Email: dipti.qriocity@gmail.com
