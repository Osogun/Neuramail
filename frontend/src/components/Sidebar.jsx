// src/components/Sidebar.jsx - Wersja Ostateczna
import React from 'react';
import './Sidebar.css'; 

function Sidebar({ onComposeClick, activeFolder, onFolderChange, folders = [] }) {
  const PenIcon = () => (
    <svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
      <path d="M17 3a2.85 2.83 0 1 1 4 4L7.5 20.5 2 22l1.5-5.5Z"/><path d="m15 5 4 4"/>
    </svg>
  );

  return (
    <aside className="sidebar">
      <div className="sidebar-card glass-card">
        <div className="sidebar-content">
          <button className="compose-button" onClick={onComposeClick}>
            <PenIcon />
            <span>Napisz</span>
          </button>
          <nav className="sidebar-nav">
            {folders.map((folder) => (
              <a 
                href="#" 
                // Kluczem powinna być unikalna właściwość, np. nazwa
                key={folder.name} 
                className={`nav-item ${activeFolder === folder.name ? 'active' : ''}`} 
                onClick={(e) => { 
                  e.preventDefault(); 
                  // Przekazujemy tylko nazwę folderu
                  onFolderChange(folder.name); 
                }}
              >
                {/* Wyświetlamy nazwę folderu z obiektu */}
                {folder.name.replace('INBOX', 'Odebrane').replace('[Gmail]/Wysłane', 'Wysłane')}
              </a>
            ))}
          </nav>
        </div>
      </div>
    </aside>
  );
}

export default Sidebar;