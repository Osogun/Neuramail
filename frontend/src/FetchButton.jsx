import React, { useState } from "react";
import DOMPurify from "dompurify";

const FetchButton = () => {
  const [mail, setMail] = useState(null);
  const [error, setError] = useState(null);

  const handleGet = async () => {
    try {
      const res = await fetch("http://localhost:8000/api/inboxes", {
        method: "GET",
        headers: { "Content-Type": "application/json" },
      });

      const data = await res.json();

      console.log("📥 GET dane:", data);

      if (data.message) {
        setMail(null);
        setError(data.message);
      } else {
        setMail(data);
        setError(null);
      }
    } catch {
      setError("Błąd: brak połączenia z serwerem");
      setMail(null);
    }
  };

  const handlePost = async () => {
    try {
      const res = await fetch("http://localhost:8000/api/emails", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          Accept: "application/json",
        },
        body: JSON.stringify({
          inbox: "INBOX",
          filtr: "UNSEEN",
          //keyword: "szukana fraza", //fraza szukana w temacie lub treści e-maila
          //from_email: "jakiscwel@yolo.xd", //email nadawcy
          //to_email: "oskargum@gmail.com", //email odbiorcy
          //since: "26-06-2025", // format daty musi być DD-MM-YYYY
          //before: "30-06-2025", //format daty musi być DD-MM-YYYY
        }),
      });

      const data = await res.json();

      console.log("📥 POST dane:", data[0]);

      if (data.message) {
        setMail(null);
        setError(data.message);
      } else {
        setMail(data[0]);
        setError(null);
      }
    } catch {
      setError("Błąd: brak połączenia z serwerem");
      setMail(null);
    }
  };

  return (
    <div>
      <button onClick={handleGet}>Pobierz skrzynki pcoztowe (GET)</button>
      <button onClick={handlePost} style={{ marginLeft: "1rem" }}>
        Pobierz e-mail (POST z filtrem)
      </button>

      {error && <p style={{ color: "red" }}>{error}</p>}

      {mail && (
        <div style={{ border: "1px solid #ccc", padding: "1rem", marginTop: "1rem" }}>
          <h3>{mail.subject}</h3>
          <p>
            <strong>Od:</strong> {mail.from_}
            <br />
            <strong>Do:</strong> {mail.to_}
            <br />
            <strong>Data:</strong> {mail.date}
          </p>

          {mail.body_type === "html" ? (
            <div
              dangerouslySetInnerHTML={{ __html: DOMPurify.sanitize(mail.body) }}
            />
          ) : (
            <pre>{mail.body}</pre>
          )}
        </div>
      )}
    </div>
  );
};

export default FetchButton;
