import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import { certificatesAPI, adminAPI, authAPI } from '../services/api';

function TeacherDashboard() {
  const { user, logout } = useAuth();
  const navigate = useNavigate();
  const [certificates, setCertificates] = useState([]);
  const [categories, setCategories] = useState([]);
  const [students, setStudents] = useState([]);
  const [activeTab, setActiveTab] = useState('register');
  const [loading, setLoading] = useState(false);
  const [formData, setFormData] = useState({
    certificate_id: '',
    holder_name: '',
    institution_name: '',
    qualification_name: '',
    certificate_type: '',
    expiry_date: '',
    category_id: '',
    description: '',
  });
  const [transferForm, setTransferForm] = useState({
    certificate_id: '',
    new_holder_address: '',
  });

  useEffect(() => {
    loadData();
  }, []);

  const loadData = async () => {
    try {
      const [certificatesRes, categoriesRes, studentsRes] = await Promise.all([
        certificatesAPI.getAll(),
        adminAPI.getAllCategories(),
        authAPI.getStudents().catch(() => ({ data: [] })),
      ]);
      setCertificates(certificatesRes.data);
      setCategories(categoriesRes.data);
      setStudents(studentsRes.data);
    } catch (error) {
      console.error('Error loading data:', error);
    }
  };

  const handleLogout = async () => {
    await logout();
    navigate('/login');
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);

    try {
      // Format expiry_date to ISO datetime if provided
      const submissionData = {
        ...formData,
        expiry_date: formData.expiry_date ? `${formData.expiry_date}T00:00:00` : null,
      };

      await certificatesAPI.issue(submissionData);
      alert('Certificate issued successfully!');
      setFormData({
        certificate_id: '',
        holder_name: '',
        institution_name: '',
        qualification_name: '',
        certificate_type: '',
        expiry_date: '',
        category_id: '',
        description: '',
      });
      loadData();
      setActiveTab('certificates');
    } catch (error) {
      alert(error.response?.data?.detail || 'Error issuing certificate');
    } finally {
      setLoading(false);
    }
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
        <h1>Teacher Dashboard</h1>
        <div className="header-right">
          <span>Welcome, {user?.username} ({user?.role})</span>
          <button onClick={handleLogout} className="btn-secondary">Logout</button>
        </div>
      </header>

      <div className="tabs">
        <button
          className={activeTab === 'register' ? 'tab active' : 'tab'}
          onClick={() => setActiveTab('register')}
        >
          Issue Certificate
        </button>
        <button
          className={activeTab === 'transfer' ? 'tab active' : 'tab'}
          onClick={() => setActiveTab('transfer')}
        >
          Transfer Certificate
        </button>
        <button
          className={activeTab === 'certificates' ? 'tab active' : 'tab'}
          onClick={() => setActiveTab('certificates')}
        >
          All Certificates
        </button>
      </div>

      <div className="dashboard-content">
        {activeTab === 'register' && (
          <div className="register-certificate-section">
            <h2>Issue New Certificate on Blockchain</h2>
            <form onSubmit={handleSubmit} className="certificate-form">
              <div className="form-group">
                <label>Certificate ID *</label>
                <input
                  type="text"
                  value={formData.certificate_id}
                  onChange={(e) => setFormData({ ...formData, certificate_id: e.target.value })}
                  required
                  placeholder="e.g., CERT-001"
                />
              </div>

              <div className="form-group">
                <label>Holder Name *</label>
                <input
                  type="text"
                  value={formData.holder_name}
                  onChange={(e) => setFormData({ ...formData, holder_name: e.target.value })}
                  required
                  placeholder="e.g., John Doe"
                />
              </div>

              <div className="form-group">
                <label>Institution Name *</label>
                <input
                  type="text"
                  value={formData.institution_name}
                  onChange={(e) => setFormData({ ...formData, institution_name: e.target.value })}
                  required
                  placeholder="e.g., University of Technology"
                />
              </div>

              <div className="form-group">
                <label>Qualification Name *</label>
                <input
                  type="text"
                  value={formData.qualification_name}
                  onChange={(e) => setFormData({ ...formData, qualification_name: e.target.value })}
                  required
                  placeholder="e.g., Bachelor of Science in Computer Science"
                />
              </div>

              <div className="form-group">
                <label>Certificate Type *</label>
                <select
                  value={formData.certificate_type}
                  onChange={(e) => setFormData({ ...formData, certificate_type: e.target.value })}
                  required
                >
                  <option value="">Select Type</option>
                  <option value="academic">Academic</option>
                  <option value="professional">Professional</option>
                  <option value="training">Training</option>
                  <option value="achievement">Achievement</option>
                </select>
              </div>

              <div className="form-group">
                <label>Expiry Date</label>
                <input
                  type="date"
                  value={formData.expiry_date}
                  onChange={(e) => setFormData({ ...formData, expiry_date: e.target.value })}
                  placeholder="Leave blank if no expiry"
                />
              </div>

              <div className="form-group">
                <label>Category</label>
                <select
                  value={formData.category_id}
                  onChange={(e) => setFormData({ ...formData, category_id: e.target.value })}
                >
                  <option value="">Select Category</option>
                  {categories.map((cat) => (
                    <option key={cat.id} value={cat.id}>
                      {cat.name}
                    </option>
                  ))}
                </select>
              </div>

              <div className="form-group">
                <label>Description</label>
                <textarea
                  value={formData.description}
                  onChange={(e) => setFormData({ ...formData, description: e.target.value })}
                  placeholder="Certificate description..."
                  rows="4"
                />
              </div>

              <button type="submit" disabled={loading} className="btn-primary">
                {loading ? 'Issuing on Blockchain...' : 'Issue Certificate'}
              </button>
            </form>

            <div className="info-box">
              <h4>What happens when you issue a certificate?</h4>
              <ul>
                <li>Certificate details are stored on the blockchain</li>
                <li>A unique QR code is generated</li>
                <li>Certificate ownership is assigned to you</li>
              </ul>
            </div>
          </div>
        )}

        {activeTab === 'transfer' && (
          <div className="transfer-section">
            <h2>Assign/Transfer Certificate to Holder</h2>

            {certificates.filter((c) => c.current_holder === user?.id).length === 0 ? (
              <div className="info-box">
                <h4>No Certificates Available for Transfer</h4>
                <p>You don't currently own any certificates to transfer.</p>
                <p>Issue a certificate first, and it will appear here for transfer to students.</p>
                {certificates.length > 0 && (
                  <div style={{ marginTop: '15px', padding: '10px', background: '#f0f0f0', borderRadius: '5px' }}>
                    <p><strong>Debug Info:</strong></p>
                    <p>Total certificates in system: {certificates.length}</p>
                    <p>Your user ID: {user?.id}</p>
                    <p>Certificates ownership:</p>
                    <ul style={{ fontSize: '12px', marginTop: '10px' }}>
                      {certificates.slice(0, 5).map(cert => (
                        <li key={cert.id}>
                          {cert.certificate_id}: owner_id={cert.current_holder}, matches={cert.current_holder === user?.id ? 'YES' : 'NO'}
                        </li>
                      ))}
                    </ul>
                  </div>
                )}
              </div>
            ) : (
              <>
                <div className="info-box" style={{ marginBottom: '20px' }}>
                  <p>You have <strong>{certificates.filter((c) => c.current_holder === user?.id).length}</strong> certificate(s) available for transfer.</p>
                </div>

                <form onSubmit={handleTransfer} className="transfer-form">
                  <div className="form-group">
                    <label>Select Certificate (Owned by You) *</label>
                    <select
                      value={transferForm.certificate_id}
                      onChange={(e) => setTransferForm({ ...transferForm, certificate_id: e.target.value })}
                      required
                    >
                      <option value="">Choose a certificate</option>
                      {certificates
                        .filter((c) => c.current_holder === user?.id)
                        .map((certificate) => (
                          <option key={certificate.id} value={certificate.certificate_id}>
                            {certificate.certificate_id} - {certificate.holder_name}
                          </option>
                        ))}
                    </select>
                  </div>

                  <div className="form-group">
                    <label>Select Holder (New Owner) *</label>
                    {students.filter((u) => u.wallet_address).length === 0 ? (
                      <div className="info-box">
                        <p>No students available. Students need to register first.</p>
                      </div>
                    ) : (
                      <select
                        value={transferForm.new_holder_address}
                        onChange={(e) => setTransferForm({ ...transferForm, new_holder_address: e.target.value })}
                        required
                      >
                        <option value="">Select holder ({students.filter((u) => u.wallet_address).length} available)</option>
                        {students
                          .filter((u) => u.wallet_address)
                          .map((u) => (
                            <option key={u.id} value={u.wallet_address}>
                              {u.username} ({u.wallet_address?.substring(0, 10)}...)
                            </option>
                          ))}
                      </select>
                    )}
                  </div>

                  <button type="submit" disabled={loading} className="btn-primary">
                    {loading ? 'Transferring on Blockchain...' : 'Transfer Certificate'}
                  </button>
                </form>
              </>
            )}
          </div>
        )}

        {activeTab === 'certificates' && (
          <div className="certificates-section">
            <h2>All Issued Certificates</h2>
            <table className="data-table">
              <thead>
                <tr>
                  <th>Certificate ID</th>
                  <th>Holder Name</th>
                  <th>Institution</th>
                  <th>Qualification</th>
                  <th>Type</th>
                  <th>QR Code</th>
                  <th>Blockchain TX</th>
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
                    <td>{certificate.certificate_type}</td>
                    <td>
                      {certificate.qr_code_path && (
                        <a href={`http://localhost:8000/${certificate.qr_code_path}`} target="_blank" rel="noreferrer">
                          View QR
                        </a>
                      )}
                    </td>
                    <td className="tx-hash">{certificate.blockchain_tx_hash?.substring(0, 10)}...</td>
                    <td>
                      <span className={certificate.current_holder === user?.id ? 'badge badge-success' : 'badge badge-secondary'}>
                        {certificate.current_holder === user?.id ? 'You' : 'Holder/Other'}
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

export default TeacherDashboard;
