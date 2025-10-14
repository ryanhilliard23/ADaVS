import React, { useState } from 'react';
import '../css/auth.css'; 

const Login = ({ onSwitchMode }) => {
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');

  const handleSubmit = (e) => {
    e.preventDefault();
    console.log('Logging in with:', { email, password });
    alert('Login functionality not yet implemented.');
  };

  return (
    <div className="auth-form-container">
      <h2>Welcome Back</h2>
      <p>Please enter your details to sign in.</p>
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
        <button type="submit" className="auth-button">
          Sign In
        </button>
      </form>
      <p className="switch-mode-text">
        Don't have an account?{' '}
        <span onClick={() => onSwitchMode('register')} className="switch-mode-link">
          Sign up
        </span>
      </p>
    </div>
  );
};

export default Login;