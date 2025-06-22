import React from 'react';

const EmailDisplay = ({ from, to, subject, date, body }) => (
  <div className="bg-gray-100 text-gray-800 p-4 rounded space-y-2 text-sm">
    <p><strong>Temat:</strong> {subject}</p>
    <p><strong>Od:</strong> {from}</p>
    <p><strong>Do:</strong> {to}</p>
    <p><strong>Data:</strong> {date}</p>
    <p><strong>Treść:</strong><br />{body}</p>
  </div>
);

export default EmailDisplay;
