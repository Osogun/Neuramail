// src/components/Sidebar.jsx
import React from 'react';
import './Sidebar.css'; 

function Sidebar({ onComposeClick, activeFolder, onFolderChange }) {
  const PenIcon = () => (
    <svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
      <path d="M17 3a2.85 2.83 0 1 1 4 4L7.5 20.5 2 22l1.5-5.5Z"/><path d="m15 5 4 4"/>
    </svg>
  );

  return (
    // ZMIANA: Dodajemy klasę 'glass-card' do panelu bocznego.
    <aside className="sidebar glass-card">
      <div className="sidebar-content">
        <button className="compose-button" onClick={onComposeClick}>
          <PenIcon />
          <span>Napisz</span>
        </button>
        <nav className="sidebar-nav">
          <a href="#" className={`nav-item ${activeFolder === 'inbox' ? 'active' : ''}`} onClick={(e) => { e.preventDefault(); onFolderChange('inbox'); }}>Odebrane</a>
          <a href="#" className={`nav-item ${activeFolder === 'sent' ? 'active' : ''}`} onClick={(e) => { e.preventDefault(); onFolderChange('sent'); }}>Wysłane</a>
          <a href="#" className={`nav-item ${activeFolder === 'drafts' ? 'active' : ''}`} onClick={(e) => { e.preventDefault(); onFolderChange('drafts'); }}>Wersje robocze</a>
          <a href="#" className={`nav-item ${activeFolder === 'trash' ? 'active' : ''}`} onClick={(e) => { e.preventDefault(); onFolderChange('trash'); }}>Kosz</a>
        </nav>
      </div>
    </aside>
  );
}

export default Sidebar;