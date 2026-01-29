import React from 'react';
import { useTheme } from '../context/ThemeContext';
import './ThemeToggle.css';

const ThemeToggle = () => {
    const { theme, toggleTheme } = useTheme();

    return (
        <button
            className="theme-toggle"
            onClick={toggleTheme}
            title={`Switch to ${theme === 'dark' ? 'light' : 'dark'} mode`}
            aria-label={`Switch to ${theme === 'dark' ? 'light' : 'dark'} mode`}
        >
            <span className="theme-toggle-icon">
                {theme === 'dark' ? '☀️' : '🌙'}
            </span>
            <span className="theme-toggle-track">
                <span className="theme-toggle-thumb"></span>
            </span>
        </button>
    );
};

export default ThemeToggle;
