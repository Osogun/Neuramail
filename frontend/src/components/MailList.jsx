// src/components/MailList.jsx
import React from 'react';
import MailItem from './MailItem';
import './MailList.css';

function MailList({ mails, loading, onMailSelect, activeFolder }) {

  const getMailListHeading = () => {
    const folderNames = {
      inbox: 'Odebrane', sent: 'Wysłane', drafts: 'Wersje robocze', trash: 'Kosz'
    };
    return folderNames[activeFolder] || 'Maile';
  };

  return (
    // ZMIANA: Przywracamy wygląd pojedynczej karty dla całej listy.
    <div className="mail-list-card glass-card">
      <div className="mail-list-content">
        <h2 className="mail-list-heading">{getMailListHeading()}</h2>
        
        {loading ? (
          <div className="status-box"><p>Ładowanie maili...</p></div>
        ) : mails.length > 0 ? (
          <div className="mails-grid"> 
            {mails.map((mail) => (
              <MailItem key={mail.id} mail={mail} onSelectMail={onMailSelect} />
            ))}
          </div>
        ) : (
          <div className="status-box"><p>Brak maili do wyświetlenia.</p></div>
        )}
      </div>
    </div>
  );
}

export default MailList;