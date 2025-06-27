import React, { useState, useEffect, useCallback } from 'react';
import Sidebar from './components/Sidebar';
import MailList from './components/MailList';
import MailDetail from './components/MailDetail';
import ComposeMail from './components/ComposeMail';
import ThemeSwitcher from './components/ThemeSwitcher';
import './App.css'; 

// Adres URL Twojego API backendu
const API_URL = 'http://127.0.0.1:8000/api';

function App() {
  const [folders, setFolders] = useState([]);
  const [mails, setMails] = useState([]);
  const [selectedMail, setSelectedMail] = useState(null);
  const [loading, setLoading] = useState(true);
  const [activeFolder, setActiveFolder] = useState('');
  const [isComposing, setIsComposing] = useState(false);
  const [theme, setTheme] = useState(() => localStorage.getItem('theme') || 'light');

  // Efekt do zmiany motywu
  useEffect(() => {
    document.body.className = '';
    document.body.classList.add(`${theme}-theme`);
    localStorage.setItem('theme', theme);
  }, [theme]);

  const toggleTheme = () => {
    setTheme(prevTheme => prevTheme === 'light' ? 'dark' : 'light');
  };

  // Pobieranie folderów przy pierwszym renderowaniu
  useEffect(() => {
    const fetchFolders = async () => {
      try {
        const response = await fetch(`${API_URL}/inboxes`);
        if (!response.ok) throw new Error('Network response was not ok');
        const data = await response.json();
        
        // Backend zwraca obiekt {"inboxes": [...]}, więc wyciągamy tablicę
        const folderList = data.inboxes || [];
        setFolders(folderList);

        if (folderList.length > 0) {
          setActiveFolder(folderList[0]); // Ustaw pierwszy folder jako aktywny
        }
      } catch (error) {
        console.error('Błąd podczas pobierania folderów:', error);
      }
    };
    fetchFolders();
  }, []);

  // Pobieranie maili, gdy zmienia się aktywny folder
  useEffect(() => {
    if (!activeFolder) return;

    const fetchEmails = async () => {
      setLoading(true);
      setSelectedMail(null); // Zresetuj wybranego maila
      try {
        const response = await fetch(`${API_URL}/emails`, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ inbox: activeFolder, filtr: 'UNSEEN' }),
        });
        if (!response.ok) throw new Error('Network response was not ok');
        
        const data = await response.json();
        setMails(data || []);
      } catch (error) {
        console.error(`Błąd podczas pobierania maili dla folderu ${activeFolder}:`, error);
        setMails([]); // Wyczyść maile w razie błędu
      } finally {
        setLoading(false);
      }
    };

    fetchEmails();
  }, [activeFolder]);

  // Pobieranie treści pojedynczego maila po kliknięciu
  const handleSelectMail = useCallback(async (mailId) => {
    if (!activeFolder || !mailId) return;

    // Znajdź podstawowe dane maila na liście, żeby nie pobierać ich ponownie
    const basicMailData = mails.find(m => m.id === mailId);
    if (!basicMailData) return;
    
    // Ustaw od razu podstawowe dane, aby użytkownik widział treść szybciej
    setSelectedMail(basicMailData);

    // Możesz dodać pobieranie pełnej treści maila, jeśli lista zwraca tylko skróty
    // W obecnej implementacji backendu, lista zwraca pełną treść, więc poniższy kod jest opcjonalny
    /*
    try {
      const response = await fetch(`${API_URL}/read`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ email_id: mailId, inbox: activeFolder }),
      });
      if (!response.ok) throw new Error('Network response was not ok');
      const mailContent = await response.json();
      setSelectedMail(mailContent);
    } catch(error) {
        console.error("Błąd podczas pobierania treści maila:", error);
    }
    */
  }, [activeFolder, mails]);

  const handleFolderChange = (folder) => setActiveFolder(folder);
  const handleBackToList = () => setSelectedMail(null);
  const handleToggleCompose = () => setIsComposing(!isComposing);

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
            // przekazujemy foldery do paska bocznego, jeśli ma je dynamicznie renderować
            // folders={folders} 
          />
          <main className="main-content">
            {selectedMail ? (
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