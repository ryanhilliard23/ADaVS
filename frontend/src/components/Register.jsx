import React, { useState } from 'react';
import '../css/auth.css'; // Reusing the same CSS

const Register = ({ onSwitchMode }) => {
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [confirmPassword, setConfirmPassword] = useState('');

  const handleSubmit = (e) => {
    e.preventDefault();
    if (password !== confirmPassword) {
      alert("Passwords don't match!");
      return;
    }

    console.log('Registering with:', { email, password });
    alert('Registration functionality not yet implemented.');
  };

  return (
    <div className="auth-form-container">
      <h2>Create an Account</h2>
      <p>Start your journey with us today.</p>
      <form onSubmit={handleSubmit} className="auth-form">
        <div className="form-group">
          <label htmlFor="email">Email</label>
          <input
            type="email"
            id="email"
            value={email}
            onChange={(e) => setEmail(e.target.value)}
            placeholder="name@company.com"
            required
          />
        </div>
        <div className="form-group">
          <label htmlFor="password">Password</label>
          <input
            type="password"
            id="password"
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            placeholder="••••••••"
            required
          />
        </div>
        <div className="form-group">
          <label htmlFor="confirm-password">Confirm Password</label>
          <input
            type="password"
            id="confirm-password"
            value={confirmPassword}
            onChange={(e) => setConfirmPassword(e.target.value)}
            placeholder="••••••••"
            required
          />
        </div>
        <button type="submit" className="auth-button">
          Create Account
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