// src/App.jsx
import React, { useState, useEffect } from 'react';
import Sidebar from './components/Sidebar';
import MailList from './components/MailList';
import MailDetail from './components/MailDetail';
import ComposeMail from './components/ComposeMail';
import ThemeSwitcher from './components/ThemeSwitcher';
import './App.css'; 

const fakeMails = {
  inbox: [
    { id: 1, sender: 'Google', subject: 'Nowe logowanie na Twoim koncie', body: 'Wykryliśmy nowe logowanie na Twoim koncie w systemie Windows. Jeśli to nie Ty, natychmiast zabezpiecz swoje konto.', date: '10:15' },
    { id: 2, sender: 'GitHub', subject: 'Your pull request was merged!', body: 'Great news! Your pull request "feat: add new floating compose window" into the main repository has been successfully merged and deployed.', date: '09:30' },
  ],
  sent: [ { id: 4, sender: 'Do: Anna Nowak', subject: 'Re: Projekt XYZ', body: 'Cześć Aniu, dzięki za feedback! Przesyłam zaktualizowaną wersję projektu. Daj znać co myślisz.', date: 'Wczoraj' } ],
  drafts: [ { id: 5, sender: 'Do: Szef', subject: 'Raport kwartalny', body: 'Panie Prezesie, w załączniku przesyłam wstępną wersję...', date: '2 dni temu' } ],
  trash: [ { id: 6, sender: 'Spam King', subject: 'Wygrałeś MILIONY!!!', body: 'Kliknij tutaj, aby odebrać nagrodę!', date: '3 dni temu' } ]
};

function App() {
  const [mails, setMails] = useState([]);
  const [loading, setLoading] = useState(true);
  const [activeFolder, setActiveFolder] = useState('inbox');
  const [selectedMailId, setSelectedMailId] = useState(null);
  const [isComposing, setIsComposing] = useState(false);
  const [theme, setTheme] = useState(() => localStorage.getItem('theme') || 'light');

  useEffect(() => {
    document.body.className = '';
    document.body.classList.add(`${theme}-theme`);
    localStorage.setItem('theme', theme);
  }, [theme]);

  const toggleTheme = () => {
    setTheme(prevTheme => prevTheme === 'light' ? 'dark' : 'light');
  };

  useEffect(() => {
    setLoading(true);
    setSelectedMailId(null); 
    setTimeout(() => {
      setMails(fakeMails[activeFolder] || []);
      setLoading(false);
    }, 500);
  }, [activeFolder]);

  const handleFolderChange = (folder) => setActiveFolder(folder);
  const handleSelectMail = (id) => setSelectedMailId(id);
  const handleBackToList = () => setSelectedMailId(null);
  const handleToggleCompose = () => setIsComposing(!isComposing);

  const selectedMail = mails.find(mail => mail.id === selectedMailId);
  
  return (
    <>
      <div className="app-container">
        <header className="app-header">
          <div className="app-header-content">
            <h1 className="app-title">NeuraMail</h1>
            <ThemeSwitcher theme={theme} onToggle={toggleTheme} />
          </div>
        </header>
        <div className="app-content">
          <Sidebar 
            onComposeClick={handleToggleCompose} 
            onFolderChange={handleFolderChange} 
            activeFolder={activeFolder}
          />
          <main className="main-content">
            {selectedMailId ? (
              <MailDetail mail={selectedMail} onBack={handleBackToList} />
            ) : (
              <MailList 
                mails={mails}
                loading={loading}
                onMailSelect={handleSelectMail}
                activeFolder={activeFolder}
              />
            )}
          </main>
        </div>
      </div>
      {isComposing && <ComposeMail onClose={handleToggleCompose} />}
    </>
  );
}

export default App;