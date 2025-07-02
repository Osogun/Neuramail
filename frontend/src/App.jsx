// src/App.jsx - Wersja Ostateczna i Kompletna
import React, { useState, useEffect, useCallback } from 'react';
import Sidebar from './components/Sidebar';
import MailList from './components/MailList';
import MailDetail from './components/MailDetail';
import ComposeMail from './components/ComposeMail';
import ThemeSwitcher from './components/ThemeSwitcher';
import './App.css';

const API_URL = 'http://127.0.0.1:8000/api';

function App() {
  const [mails, setMails] = useState([]);
  const [selectedMail, setSelectedMail] = useState(null);
  const [loading, setLoading] = useState(false);
  const [activeFolder, setActiveFolder] = useState('inbox');
  const [view, setView] = useState('list'); // Zarządza widokiem: 'list', 'detail', 'compose'
  const [theme, setTheme] = useState(() => localStorage.getItem('theme') || 'light');

  // Efekt do zmiany klasy motywu w <body>
  useEffect(() => {
    document.body.className = '';
    document.body.classList.add(`${theme}-theme`);
    localStorage.setItem('theme', theme);
  }, [theme]);

  // Poprawnie zdefiniowana funkcja do przełączania motywu
  const toggleTheme = () => {
    setTheme(prevTheme => (prevTheme === 'light' ? 'dark' : 'light'));
  };

  // Efekt do pobierania maili
  useEffect(() => {
    // Pobieraj maile tylko, gdy jesteśmy w widoku listy
    if (view !== 'list' || !activeFolder) return;

    const fetchEmails = async () => {
      setLoading(true);
      try {
        const response = await fetch(`${API_URL}/metadata`, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ mailbox: activeFolder }),
        });
        if (!response.ok) {
          throw new Error(`Network response was not ok (status: ${response.status})`);
        }
        const data = await response.json();
        setMails(data || []);
      } catch (error) {
        console.error(`Błąd podczas pobierania maili dla folderu ${activeFolder}:`, error);
        setMails([]);
      } finally {
        setLoading(false);
      }
    };

    fetchEmails();
  }, [activeFolder, view]); // Uruchom ponownie, gdy zmieni się folder lub gdy wrócimy do widoku listy

  // --- Funkcje do zarządzania stanem i widokami ---

  const handleSelectMail = useCallback((mail) => {
    setSelectedMail(mail);
    setView('detail');
  }, []);

  const handleFolderChange = (folderName) => {
    setActiveFolder(folderName);
    setView('list');
  };

  const handleBackToList = () => {
    setSelectedMail(null);
    setView('list');
  };

  const handleShowCompose = () => {
    setView('compose');
  };



  const handleCloseCompose = () => {
    setView('list');
  };

  // Funkcja, która decyduje, który komponent renderować
  const renderCurrentView = () => {
    switch (view) {
      case 'compose':
        return <ComposeMail onClose={handleCloseCompose} />;
      case 'detail':
        return <MailDetail mail={selectedMail} onBack={handleBackToList} />;
      case 'list':
      default:
        return (
          <MailList
            mails={mails}
            loading={loading}
            onMailSelect={handleSelectMail}
            activeFolder={activeFolder}
          />
        );
    }
  };

  return (
    <div className="app-container">
      <header className="app-header">
        <div className="app-header-content">
          <h1 className="app-title">NeuraMail</h1>
          <ThemeSwitcher theme={theme} onToggle={toggleTheme} />
        </div>
      </header>
      <div className="app-content">
        <Sidebar
          onComposeClick={handleShowCompose}
          onFolderChange={handleFolderChange}
          activeFolder={activeFolder}
        />
        <main className="main-content">
          {renderCurrentView()}
        </main>
      </div>
    </div>
  );
}

export default App;