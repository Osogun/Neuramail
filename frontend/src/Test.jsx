import React, { useState } from "react";

const FetchButton = () => {
  const [mail, setMail] = useState(null);
  const [error, setError] = useState(null);

  const handleClick = async () => {
    try {
      const res = await fetch("http://localhost:8000/api/test", {
        method: "GET",
        headers: { "Content-Type": "application/json" },
      });

      const data = await res.json();

      if (data.message) {
        setMail(null);
        setError(data.message); // np. "No new emails found."
      } else {
        setMail(data);
        setError(null);
      }
    } catch {
      setError("Błąd: brak połączenia z serwerem");
      setMail(null);
    }
  };

  return (
    <div className="p-4 space-y-4 border border-gray-300 rounded-lg max-w-md">
      <button
        onClick={handleClick}
        className="bg-blue-600 hover:bg-blue-700 text-black font-semibold py-2 px-4 rounded-lg shadow"
      >
        Test API
      </button>

      {error && <p className="text-red-600">{error}</p>}

      {mail && (
        <div className="bg-gray-100 text-gray-800 p-4 rounded space-y-2 text-sm">
          <p><strong>Temat:</strong> {mail.subject}</p>
          <p><strong>Od:</strong> {mail.from}</p>
          <p><strong>Do:</strong> {mail.to}</p>
          <p><strong>Data:</strong> {mail.date}</p>
          <p><strong>Treść:</strong><br />{mail.body}</p>
        </div>
      )}
    </div>
  );
};

export default FetchButton;
