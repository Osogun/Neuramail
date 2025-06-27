// src/components/MailItem.jsx
import React from 'react';
import './MailItem.css';

function MailItem({ mail, onSelectMail }) {
  const bodySnippet = mail.body ? mail.body.substring(0, 100) + (mail.body.length > 100 ? '...' : '') : '';

  return (
    // ZMIANA: Usunięto klasę 'aurora-glass' z diva. To jest teraz prosty wiersz.
    <div className="mail-item" onClick={() => onSelectMail(mail.id)}>
      <div className="mail-item-content">
        <div className="mail-header-line">
          <h3 className="mail-subject">{mail.subject}</h3>
          <p className="mail-sender">{mail.sender}</p>
          <p className="mail-date">{mail.date}</p>
        </div>
        <p className="mail-body">{bodySnippet}</p>
      </div>
    </div>
  );
}

export default MailItem;