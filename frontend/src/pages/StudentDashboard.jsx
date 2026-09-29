import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import { certificatesAPI, adminAPI } from '../services/api';

function StudentDashboard() {
  const { user, logout } = useAuth();
  const navigate = useNavigate();
  const [certificates, setCertificates] = useState([]);
  const [myCertificates, setMyCertificates] = useState([]);
  const [users, setUsers] = useState([]);
  const [activeTab, setActiveTab] = useState('myCertificates');
  const [transferForm, setTransferForm] = useState({
    certificate_id: '',
    new_holder_address: '',
  });
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    loadData();
  }, []);

  const loadData = async () => {
    try {
      const [certificatesRes, usersRes] = await Promise.all([
        certificatesAPI.getAll(),
        adminAPI.getAllUsers().catch(() => ({ data: [] })),
      ]);

      setCertificates(certificatesRes.data);

      // Filter certificates owned by current user
      const owned = certificatesRes.data.filter((c) => c.current_holder === user?.id);
      setMyCertificates(owned);

      setUsers(usersRes.data);
    } catch (error) {
      console.error('Error loading data:', error);
    }
  };

  const handleLogout = async () => {
    await logout();
    navigate('/login');
  };

  const handleTransfer = async (e) => {
    e.preventDefault();
    setLoading(true);

    try {
      await certificatesAPI.transfer(transferForm);
      alert('Certificate transferred successfully!');
      setTransferForm({ certificate_id: '', new_holder_address: '' });
      loadData();
    } catch (error) {
      alert(error.response?.data?.detail || 'Error transferring certificate');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="dashboard">
      <header className="dashboard-header">
        <h1>Student Dashboard</h1>
        <div className="header-right">
          <span>Welcome, {user?.username} ({user?.role})</span>
          <span className="wallet">Wallet: {user?.wallet_address?.substring(0, 8)}...</span>
          <button onClick={handleLogout} className="btn-secondary">Logout</button>
        </div>
      </header>

      <div className="tabs">
        <button
          className={activeTab === 'myCertificates' ? 'tab active' : 'tab'}
          onClick={() => setActiveTab('myCertificates')}
        >
          My Certificates
        </button>
        <button
          className={activeTab === 'transfer' ? 'tab active' : 'tab'}
          onClick={() => setActiveTab('transfer')}
        >
          Transfer Certificate
        </button>
        <button
          className={activeTab === 'allCertificates' ? 'tab active' : 'tab'}
          onClick={() => setActiveTab('allCertificates')}
        >
          All Certificates
        </button>
      </div>

      <div className="dashboard-content">
        {activeTab === 'myCertificates' && (
          <div className="my-certificates-section">
            <h2>Certificates I Own</h2>
            {myCertificates.length === 0 ? (
              <p className="no-data">You don't own any certificates yet.</p>
            ) : (
              <table className="data-table">
                <thead>
                  <tr>
                    <th>Certificate ID</th>
                    <th>Holder Name</th>
                    <th>Institution</th>
                    <th>Qualification</th>
                    <th>QR Code</th>
                    <th>Actions</th>
                  </tr>
                </thead>
                <tbody>
                  {myCertificates.map((certificate) => (
                    <tr key={certificate.id}>
                      <td>{certificate.certificate_id}</td>
                      <td>{certificate.holder_name}</td>
                      <td>{certificate.institution_name}</td>
                      <td>{certificate.qualification_name}</td>
                      <td>
                        {certificate.qr_code_path && (
                          <a href={`http://localhost:8000/${certificate.qr_code_path}`} target="_blank" rel="noreferrer">
                            View QR
                          </a>
                        )}
                      </td>
                      <td>
                        <button
                          onClick={() => {
                            setActiveTab('transfer');
                            setTransferForm({ ...transferForm, certificate_id: certificate.certificate_id });
                          }}
                          className="btn-small btn-primary"
                        >
                          Transfer
                        </button>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            )}
          </div>
        )}

        {activeTab === 'transfer' && (
          <div className="transfer-section">
            <h2>Transfer Certificate Ownership</h2>
            <form onSubmit={handleTransfer} className="transfer-form">
              <div className="form-group">
                <label>Select Certificate *</label>
                <select
                  value={transferForm.certificate_id}
                  onChange={(e) => setTransferForm({ ...transferForm, certificate_id: e.target.value })}
                  required
                >
                  <option value="">Choose a certificate</option>
                  {myCertificates.map((certificate) => (
                    <option key={certificate.id} value={certificate.certificate_id}>
                      {certificate.certificate_id} - {certificate.holder_name}
                    </option>
                  ))}
                </select>
              </div>

              <div className="form-group">
                <label>New Owner (Wallet Address) *</label>
                <select
                  value={transferForm.new_holder_address}
                  onChange={(e) => setTransferForm({ ...transferForm, new_holder_address: e.target.value })}
                  required
                >
                  <option value="">Select new owner</option>
                  {users
                    .filter((u) => u.wallet_address && u.id !== user?.id)
                    .map((u) => (
                      <option key={u.id} value={u.wallet_address}>
                        {u.username} ({u.wallet_address?.substring(0, 10)}...)
                      </option>
                    ))}
                </select>
              </div>

              <button type="submit" disabled={loading} className="btn-primary">
                {loading ? 'Transferring on Blockchain...' : 'Transfer Certificate'}
              </button>
            </form>

            <div className="info-box">
              <h4>Transfer Process</h4>
              <ul>
                <li>Ownership is transferred on the blockchain</li>
                <li>Transfer history is recorded immutably</li>
                <li>You will no longer have access to this certificate</li>
                <li>New owner can verify authenticity</li>
              </ul>
            </div>
          </div>
        )}

        {activeTab === 'allCertificates' && (
          <div className="all-certificates-section">
            <h2>All Certificates in System</h2>
            <table className="data-table">
              <thead>
                <tr>
                  <th>Certificate ID</th>
                  <th>Holder Name</th>
                  <th>Institution</th>
                  <th>Qualification</th>
                  <th>Ownership</th>
                  <th>Issued At</th>
                </tr>
              </thead>
              <tbody>
                {certificates.map((certificate) => (
                  <tr key={certificate.id}>
                    <td>{certificate.certificate_id}</td>
                    <td>{certificate.holder_name}</td>
                    <td>{certificate.institution_name}</td>
                    <td>{certificate.qualification_name}</td>
                    <td>
                      <span className={certificate.current_holder === user?.id ? 'badge badge-success' : 'badge badge-secondary'}>
                        {certificate.current_holder === user?.id ? 'You' : 'Other'}
                      </span>
                    </td>
                    <td>{new Date(certificate.created_at).toLocaleDateString()}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>
    </div>
  );
}

export default StudentDashboard;
