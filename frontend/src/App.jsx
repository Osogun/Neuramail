// src/App.jsx - Wersja Ostateczna
import React, { useState, useEffect, useCallback } from 'react';
import Sidebar from './components/Sidebar';
import MailList from './components/MailList';
import MailDetail from './components/MailDetail';
import ComposeMail from './components/ComposeMail';
import ThemeSwitcher from './components/ThemeSwitcher';
import './App.css';

const API_URL = 'http://127.0.0.1:8000/api';

function App() {
  const [folders, setFolders] = useState([]);
  const [mails, setMails] = useState([]);
  const [selectedMail, setSelectedMail] = useState(null);
  const [loading, setLoading] = useState(false);
  const [activeFolder, setActiveFolder] = useState('');
  const [view, setView] = useState('list');
  const [theme, setTheme] = useState(() => localStorage.getItem('theme') || 'light');

  useEffect(() => {
    document.body.className = '';
    document.body.classList.add(`${theme}-theme`);
    localStorage.setItem('theme', theme);
  }, [theme]);

  const toggleTheme = () => {
    setTheme(prevTheme => (prevTheme === 'light' ? 'dark' : 'light'));
  };

  useEffect(() => {
    const fetchFolders = async () => {
      try {
        const response = await fetch(`${API_URL}/inboxes`);
        if (!response.ok) throw new Error('Network response was not ok');
        const data = await response.json();
        
        const folderList = data.inboxes || [];
        setFolders(folderList);

        // Jeśli są foldery, ustaw NAZWĘ pierwszego jako aktywną
        if (folderList.length > 0 && folderList[0].name) {
          setActiveFolder(folderList[0].name);
        }
      } catch (error) {
        console.error('Błąd podczas pobierania folderów:', error);
      }
    };
    fetchFolders();
  }, []);

  useEffect(() => {
    if (view !== 'list' || !activeFolder) return;
    const fetchEmails = async () => {
      setLoading(true);
      try {
        const response = await fetch(`${API_URL}/metadata`, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ mailbox_name: activeFolder }),
        });
        if (!response.ok) throw new Error(`Network response was not ok (status: ${response.status})`);
        const data = await response.json();
        console.log(data);
        setMails(data || []);
      } catch (error) {
        console.error(`Błąd podczas pobierania maili dla folderu ${activeFolder}:`, error);
        setMails([]);
      } finally {
        setLoading(false);
      }
    };
    fetchEmails();
  }, [activeFolder, view]);

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

  const renderCurrentView = () => {
    switch (view) {
      case 'compose':
        return <ComposeMail onClose={handleCloseCompose} />;
      case 'detail':
        return <MailDetail mail={selectedMail} onBack={handleBackToList} />;
      case 'list':
      default:
        return <MailList mails={mails} loading={loading} onMailSelect={handleSelectMail} mailbox_name={activeFolder} />;
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
          folders={folders}
        />
        <main className="main-content">
          {renderCurrentView()}
        </main>
      </div>
    </div>
  );
}

export default App;