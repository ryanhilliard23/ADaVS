import React, { useState } from 'react';
import { MdOutlineEmail, MdOutlineLock } from 'react-icons/md';
import '../css/auth.css';

const Register = ({ onSwitchMode }) => {
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [confirmPassword, setConfirmPassword] = useState('');
  const [error, setError] = useState('');
  const [isLoading, setIsLoading] = useState(false);

  // API URL from the environment variable
  const API_BASE_URL = import.meta.env.VITE_API_BASE_URL;

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError('');

    if (password !== confirmPassword) {
      setError("Passwords don't match!");
      return;
    }

    setIsLoading(true);

    try {
      const response = await fetch(`https://adavs-backend.onrender.com/api/users/register`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ email, password }),
      });
      const data = await response.json();

      if (!response.ok) {
        if (response.status === 429) {
          throw new Error(data.error || "Too many attempts. Please wait a few minutes.");
        }
        throw new Error(data.detail || 'Registration failed.');
      }

      onSwitchMode('login');

    } catch (err) {
      setError(err.message);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="auth-form-container">
      <h2>Create an Account</h2>
      <p>Start your journey with us today.</p>
      <form onSubmit={handleSubmit} className="auth-form">
        {error && <p style={{ color: '#e53e3e', textAlign: 'center' }}>{error}</p>}
        <div className="form-group">
          <MdOutlineEmail className="auth-icon" />
          <label htmlFor="email">Email</label>
          <input
            type="email"
            id="email"
            value={email}
            onChange={(e) => setEmail(e.target.value)}
            placeholder="name@company.com"
            required
            disabled={isLoading}
          />
        </div>
        <div className="form-group">
          <MdOutlineLock className="auth-icon" />
          <label htmlFor="password">Password</label>
          <input
            type="password"
            id="password"
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            placeholder="••••••••"
            required
            disabled={isLoading}
          />
        </div>
        <div className="form-group">
          <MdOutlineLock className="auth-icon" />
          <label htmlFor="confirm-password">Confirm Password</label>
          <input
            type="password"
            id="confirm-password"
            value={confirmPassword}
            onChange={(e) => setConfirmPassword(e.target.value)}
            placeholder="••••••••"
            required
            disabled={isLoading}
          />
        </div>
        <button type="submit" className="auth-button" disabled={isLoading}>
          {isLoading ? 'Creating Account...' : 'Create Account'}
        </button>
      </form>
      <p className="switch-mode-text">
        Already have an account?{' '}
        <span onClick={() => onSwitchMode('login')} className="switch-mode-link">
          Sign in
        </span>
      </p>
    </div>
  );
};

export default Register;