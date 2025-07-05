// src/components/MailItem.jsx
import React from 'react';
import './MailItem.css';

function MailItem({ mail, onSelectMail }) {
  const bodySnippet = mail.content_preview ? mail.content_preview.substring(0, 100) + (mail.content_preview.length > 100 ? '...' : '') : '';

  return (
    <div className="mail-item" onClick={() => onSelectMail(mail)}>
      <div className="mail-item-content">
        <div className="mail-header-line">
          <h3 className="mail-subject">{mail.subject || 'Bez tematu'}</h3>
          <p className="mail-sender">{mail.sender_name || 'Nieznany nadawca'}</p>
          <p className="mail-date">{mail.date || ''}</p>
        </div>
        <p className="mail-body">{bodySnippet}</p>
      </div>
    </div>
  );
}

export default MailItem;