// src/components/MailDetail.jsx
import React from 'react';
import './MailDetail.css';

function MailDetail({ mail, onBack }) {
  const BackArrowIcon = () => (
    <svg xmlns="http://www.w3.org/2000/svg" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round"><path d="m15 18-6-6 6-6"/></svg>
  );

  if (!mail) return null;

  return (
    <div className="mail-detail-card aurora-glass">
      <div className="mail-detail-content">
        <button onClick={onBack} className="back-button"><BackArrowIcon/> Wróć</button>
        <h2 className="detail-subject">{mail.subject}</h2>
        <div className="detail-meta">
          <p className="detail-sender"><span>Od:</span> {mail.sender}</p>
          <p className="detail-date">{mail.date}</p>
        </div>
        <hr className="detail-divider" />
        <div className="detail-body-content"><p>{mail.body}</p></div>
      </div>
    </div>
  );
}

export default MailDetail;