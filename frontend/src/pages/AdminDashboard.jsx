import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import { adminAPI } from '../services/api';

function AdminDashboard() {
  const { user, logout } = useAuth();
  const navigate = useNavigate();
  const [stats, setStats] = useState(null);
  const [users, setUsers] = useState([]);
  const [categories, setCategories] = useState([]);
  const [newCategory, setNewCategory] = useState({ name: '', description: '' });
  const [activeTab, setActiveTab] = useState('overview');
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    loadData();
  }, []);

  const loadData = async () => {
    try {
      const [statsRes, usersRes, categoriesRes] = await Promise.all([
        adminAPI.getStats(),
        adminAPI.getAllUsers(),
        adminAPI.getAllCategories(),
      ]);

      setStats(statsRes.data);
      setUsers(usersRes.data);
      setCategories(categoriesRes.data);
    } catch (error) {
      console.error('Error loading data:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleLogout = async () => {
    await logout();
    navigate('/login');
  };

  const handleToggleUserStatus = async (userId, isActive) => {
    try {
      if (isActive) {
        await adminAPI.deactivateUser(userId);
      } else {
        await adminAPI.activateUser(userId);
      }
      loadData();
    } catch (error) {
      alert('Error updating user status');
    }
  };

  const handleCreateCategory = async (e) => {
    e.preventDefault();
    try {
      await adminAPI.createCategory(newCategory);
      setNewCategory({ name: '', description: '' });
      loadData();
      alert('Category created successfully');
    } catch (error) {
      alert('Error creating category');
    }
  };

  const handleDeleteCategory = async (categoryId) => {
    if (window.confirm('Are you sure you want to delete this category?')) {
      try {
        await adminAPI.deleteCategory(categoryId);
        loadData();
      } catch (error) {
        alert('Error deleting category');
      }
    }
  };

  if (loading) return <div className="loading">Loading...</div>;

  return (
    <div className="dashboard">
      <header className="dashboard-header">
        <h1>Admin Dashboard</h1>
        <div className="header-right">
          <span>Welcome, {user?.username} ({user?.role})</span>
          <button onClick={handleLogout} className="btn-secondary">Logout</button>
        </div>
      </header>

      <div className="tabs">
        <button
          className={activeTab === 'overview' ? 'tab active' : 'tab'}
          onClick={() => setActiveTab('overview')}
        >
          Overview
        </button>
        <button
          className={activeTab === 'users' ? 'tab active' : 'tab'}
          onClick={() => setActiveTab('users')}
        >
          Users
        </button>
        <button
          className={activeTab === 'categories' ? 'tab active' : 'tab'}
          onClick={() => setActiveTab('categories')}
        >
          Categories
        </button>
      </div>

      <div className="dashboard-content">
        {activeTab === 'overview' && stats && (
          <div className="overview-section">
            <h2>System Statistics</h2>
            <div className="stats-grid">
              <div className="stat-card">
                <h3>Total Users</h3>
                <p className="stat-value">{stats.total_users}</p>
              </div>
              <div className="stat-card">
                <h3>Total Certificates</h3>
                <p className="stat-value">{stats.total_certificates}</p>
              </div>
              <div className="stat-card">
                <h3>Categories</h3>
                <p className="stat-value">{stats.total_categories}</p>
              </div>
            </div>

            <div className="users-by-role">
              <h3>Users by Role</h3>
              <div className="role-stats">
                <div className="role-stat">
                  <strong>Admins:</strong> {stats.users_by_role.admin}
                </div>
                <div className="role-stat">
                  <strong>Teachers:</strong> {stats.users_by_role.teacher}
                </div>
                <div className="role-stat">
                  <strong>Students:</strong> {stats.users_by_role.student}
                </div>
              </div>
            </div>
          </div>
        )}

        {activeTab === 'users' && (
          <div className="users-section">
            <h2>Manage Users</h2>
            <table className="data-table">
              <thead>
                <tr>
                  <th>ID</th>
                  <th>Username</th>
                  <th>Email</th>
                  <th>Role</th>
                  <th>Wallet Address</th>
                  <th>Status</th>
                  <th>Actions</th>
                </tr>
              </thead>
              <tbody>
                {users.map((u) => (
                  <tr key={u.id}>
                    <td>{u.id}</td>
                    <td>{u.username}</td>
                    <td>{u.email}</td>
                    <td><span className={`badge badge-${u.role}`}>{u.role}</span></td>
                    <td className="wallet-address">{u.wallet_address || 'N/A'}</td>
                    <td>
                      <span className={`status ${u.is_active ? 'active' : 'inactive'}`}>
                        {u.is_active ? 'Active' : 'Inactive'}
                      </span>
                    </td>
                    <td>
                      {u.id !== user.id && (
                        <button
                          onClick={() => handleToggleUserStatus(u.id, u.is_active)}
                          className="btn-small"
                        >
                          {u.is_active ? 'Deactivate' : 'Activate'}
                        </button>
                      )}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}

        {activeTab === 'categories' && (
          <div className="categories-section">
            <h2>Manage Categories</h2>

            <div className="create-category-form">
              <h3>Create New Category</h3>
              <form onSubmit={handleCreateCategory}>
                <div className="form-row">
                  <input
                    type="text"
                    placeholder="Category Name"
                    value={newCategory.name}
                    onChange={(e) => setNewCategory({ ...newCategory, name: e.target.value })}
                    required
                  />
                  <input
                    type="text"
                    placeholder="Description"
                    value={newCategory.description}
                    onChange={(e) => setNewCategory({ ...newCategory, description: e.target.value })}
                  />
                  <button type="submit" className="btn-primary">Create</button>
                </div>
              </form>
            </div>

            <table className="data-table">
              <thead>
                <tr>
                  <th>ID</th>
                  <th>Name</th>
                  <th>Description</th>
                  <th>Created At</th>
                  <th>Actions</th>
                </tr>
              </thead>
              <tbody>
                {categories.map((cat) => (
                  <tr key={cat.id}>
                    <td>{cat.id}</td>
                    <td>{cat.name}</td>
                    <td>{cat.description || 'N/A'}</td>
                    <td>{new Date(cat.created_at).toLocaleDateString()}</td>
                    <td>
                      <button
                        onClick={() => handleDeleteCategory(cat.id)}
                        className="btn-danger btn-small"
                      >
                        Delete
                      </button>
                    </td>
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

export default AdminDashboard;
