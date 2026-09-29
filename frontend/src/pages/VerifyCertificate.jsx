import React, { useState } from 'react';
import { Link } from 'react-router-dom';
import { certificatesAPI } from '../services/api';
import { Html5QrcodeScanner } from 'html5-qrcode';

function VerifyCertificate() {
  const [verifyMethod, setVerifyMethod] = useState('certificateId');
  const [certificateId, setCertificateId] = useState('');
  const [qrHash, setQrHash] = useState('');
  const [verificationResult, setVerificationResult] = useState(null);
  const [loading, setLoading] = useState(false);
  const [qrScanner, setQrScanner] = useState(null);

  const handleVerify = async (e) => {
    e.preventDefault();
    setLoading(true);
    setVerificationResult(null);

    try {
      let response;
      if (verifyMethod === 'certificateId') {
        response = await certificatesAPI.verify(certificateId);
      } else if (verifyMethod === 'qr') {
        response = await certificatesAPI.verifyByQR(qrHash);
      }

      setVerificationResult(response.data);
    } catch (error) {
      setVerificationResult({
        is_authentic: false,
        message: error.response?.data?.detail || 'Verification failed',
        lifecycle: [],
      });
    } finally {
      setLoading(false);
    }
  };

  const startQRScanner = () => {
    const scanner = new Html5QrcodeScanner('qr-reader', {
      fps: 10,
      qrbox: 250,
    });

    scanner.render(
      (decodedText) => {
        setQrHash(decodedText);
        scanner.clear();
        setQrScanner(null);
      },
      (error) => {
        console.warn('QR scan error:', error);
      }
    );

    setQrScanner(scanner);
  };

  return (
    <div className="verify-container">
      <div className="verify-card">
        <h1>Certificate Verification</h1>
        <p className="subtitle">Verify certificate authenticity using blockchain</p>

        <div className="verify-methods">
          <button
            className={verifyMethod === 'certificateId' ? 'method-btn active' : 'method-btn'}
            onClick={() => setVerifyMethod('certificateId')}
          >
            Certificate ID
          </button>
          <button
            className={verifyMethod === 'qr' ? 'method-btn active' : 'method-btn'}
            onClick={() => setVerifyMethod('qr')}
          >
            QR Code
          </button>
        </div>

        <form onSubmit={handleVerify} className="verify-form">
          {verifyMethod === 'certificateId' && (
            <div className="form-group">
              <label>Enter Certificate ID</label>
              <input
                type="text"
                value={certificateId}
                onChange={(e) => setCertificateId(e.target.value)}
                placeholder="e.g., CERT-001"
                required
              />
            </div>
          )}

          {verifyMethod === 'qr' && (
            <div className="form-group">
              <label>QR Code Hash</label>
              <input
                type="text"
                value={qrHash}
                onChange={(e) => setQrHash(e.target.value)}
                placeholder="Scan QR or enter hash"
                required
              />
              <button type="button" onClick={startQRScanner} className="btn-secondary scan-btn">
                {qrScanner ? 'Stop Scanner' : 'Scan QR Code'}
              </button>
              <div id="qr-reader" style={{ marginTop: '20px' }}></div>
            </div>
          )}

          <button type="submit" disabled={loading} className="btn-primary verify-btn">
            {loading ? 'Verifying on Blockchain...' : 'Verify Certificate'}
          </button>
        </form>

        {verificationResult && (
          <div className={`verification-result ${verificationResult.is_authentic ? 'authentic' : 'counterfeit'}`}>
            <div className="result-header">
              {verificationResult.is_authentic ? (
                <div className="status-icon success">✓</div>
              ) : (
                <div className="status-icon error">✗</div>
              )}
              <h2>{verificationResult.message}</h2>
            </div>

            {verificationResult.is_authentic && verificationResult.certificate_details && (
              <div className="certificate-details">
                <h3>Certificate Details</h3>
                <div className="details-grid">
                  <div className="detail-item">
                    <strong>Certificate ID:</strong> {verificationResult.certificate_details.certificate_id}
                  </div>
                  <div className="detail-item">
                    <strong>Holder Name:</strong> {verificationResult.certificate_details.holder_name}
                  </div>
                  <div className="detail-item">
                    <strong>Institution:</strong> {verificationResult.certificate_details.institution_name}
                  </div>
                  <div className="detail-item">
                    <strong>Qualification:</strong> {verificationResult.certificate_details.qualification_name}
                  </div>
                  <div className="detail-item">
                    <strong>Certificate Type:</strong> {verificationResult.certificate_details.certificate_type}
                  </div>
                  {verificationResult.certificate_details.expiry_date && (
                    <div className="detail-item">
                      <strong>Expiry Date:</strong> {new Date(verificationResult.certificate_details.expiry_date).toLocaleDateString()}
                    </div>
                  )}
                  <div className="detail-item">
                    <strong>Status:</strong>
                    {verificationResult.certificate_details.is_revoked ? (
                      <span className="badge badge-error"> REVOKED</span>
                    ) : verificationResult.certificate_details.is_expired ? (
                      <span className="badge badge-warning"> EXPIRED</span>
                    ) : (
                      <span className="badge badge-success"> VALID</span>
                    )}
                  </div>
                </div>

                {(verificationResult.certificate_details.is_revoked || verificationResult.certificate_details.is_expired) && (
                  <div className="warning-box">
                    <h4>Warning: Certificate Status Issue</h4>
                    {verificationResult.certificate_details.is_revoked && (
                      <p>This certificate has been revoked and is no longer valid.</p>
                    )}
                    {verificationResult.certificate_details.is_expired && (
                      <p>This certificate has expired and may no longer be valid.</p>
                    )}
                  </div>
                )}
              </div>
            )}

            {verificationResult.lifecycle && verificationResult.lifecycle.length > 0 && (
              <div className="lifecycle">
                <h3>Certificate Lifecycle</h3>
                <div className="timeline">
                  {verificationResult.lifecycle.map((transfer, index) => (
                    <div key={index} className="timeline-item">
                      <div className="timeline-marker"></div>
                      <div className="timeline-content">
                        <strong>{transfer.transfer_type.toUpperCase()}</strong>
                        <p>
                          From: {transfer.from === '0x0000000000000000000000000000000000000000' ? 'Issuer' : transfer.from}
                        </p>
                        <p>To: {transfer.to}</p>
                        <p className="timestamp">
                          {new Date(transfer.timestamp * 1000).toLocaleString()}
                        </p>
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            )}

            {!verificationResult.is_authentic && (
              <div className="warning-box">
                <h4>Warning: Invalid Certificate Detected</h4>
                <p>This certificate is not registered on the blockchain or has been flagged as invalid.</p>
                <p>Do not accept or trust this certificate.</p>
              </div>
            )}
          </div>
        )}

        <div className="auth-links">
          <Link to="/login">Login</Link> | <Link to="/register">Register</Link>
        </div>
      </div>
    </div>
  );
}

export default VerifyCertificate;
