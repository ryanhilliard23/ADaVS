import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { MdOutlineEmail, MdOutlineLock } from 'react-icons/md';
import '../css/auth.css';

const Login = ({ onSwitchMode }) => {
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const navigate = useNavigate();
  
  const API_BASE_URL = import.meta.env.VITE_API_BASE_URL;

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError('');
    setIsLoading(true);

    // OAuth2 form req x-www-form-urlencoded
    const formData = new URLSearchParams();
    formData.append('username', email); 
    formData.append('password', password);

    try {
      const response = await fetch(`${API_BASE_URL}/users/login`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/x-www-form-urlencoded',
        },
        body: formData,
      });

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.detail || 'Incorrect email or password.');
      }

      const data = await response.json();

      // Store the token in the browser local storage
      localStorage.setItem('accessToken', data.access_token);
      
      // Redirect to the dashboard on successful login
      navigate('/dashboard');

    } catch (err) {
      setError(err.message);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="auth-form-container">
      <h2>Welcome Back</h2>
      <p>Please enter your details to sign in.</p>
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
        <button type="submit" className="auth-button" disabled={isLoading}>
          {isLoading ? 'Signing In...' : 'Sign In'}
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