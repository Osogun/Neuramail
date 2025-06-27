// src/components/ComposeMail.jsx
import React from 'react';
import ReactDOM from 'react-dom';
import './ComposeMail.css';

function ComposeMail({ onClose }) {
  const CloseIcon = () => (
    <svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round">
      <path d="M18 6 6 18"/><path d="m6 6 12 12"/>
    </svg>
  );

  return ReactDOM.createPortal(
    <div className="compose-mail-card glass-card">
      <div className="compose-content-wrapper">
        <header className="compose-header">
          <h3 className="compose-title">Nowa wiadomość</h3>
          <button className="compose-close-btn" onClick={onClose}>
            <CloseIcon />
          </button>
        </header>
        <form className="compose-form">
          <div className="compose-input-group">
            <label htmlFor="recipient">Do:</label>
            <input id="recipient" type="email" className="compose-input" />
          </div>
          <div className="compose-input-group">
            <label htmlFor="subject">Temat:</label>
            <input id="subject" type="text" className="compose-input" />
          </div>
          <textarea
            className="compose-body"
            placeholder="Napisz swoją wiadomość..."
          ></textarea>
          <div className="compose-actions">
            <button type="submit" className="compose-send-btn" onClick={(e) => { e.preventDefault(); onClose(); }}>
              Wyślij
            </button>
          </div>
        </form>
      </div>
    </div>,
    document.getElementById('compose-portal')
  );
}

export default ComposeMail;