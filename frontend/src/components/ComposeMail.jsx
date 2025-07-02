// src/components/ComposeMail.jsx - Wersja Ostateczna z Edytorem Tiptap
import React, { useState } from 'react';
import { useEditor, EditorContent } from '@tiptap/react';
import StarterKit from '@tiptap/starter-kit';
import './ComposeMail.css'; // Upewnij się, że masz też plik ze stylami
import './RichTextEditor.css'; // Style dla edytora, które stworzyliśmy wcześniej

// Komponent paska narzędzi edytora
const MenuBar = ({ editor }) => {
  if (!editor) {
    return null;
  }

  return (
    <div className="editor-menu-bar">
      <button type="button" onClick={() => editor.chain().focus().toggleBold().run()} className={editor.isActive('bold') ? 'is-active' : ''}>
        B
      </button>
      <button type="button" onClick={() => editor.chain().focus().toggleItalic().run()} className={editor.isActive('italic') ? 'is-active' : ''}>
        I
      </button>
      <button type="button" onClick={() => editor.chain().focus().toggleStrike().run()} className={editor.isActive('strike') ? 'is-active' : ''}>
        S
      </button>
    </div>
  );
};


function ComposeMail({ onClose }) {
  const [body, setBody] = useState('');

  const editor = useEditor({
    extensions: [StarterKit],
    content: body,
    onUpdate: ({ editor }) => {
      setBody(editor.getHTML());
    },
    editorProps: {
      attributes: {
        class: 'tiptap-editor-prose',
      },
    },
  });


  return (
    <div className="compose-mail-card glass-card">
      <div className="compose-content-wrapper">
        <header className="compose-header">
          <h3 className="compose-title">Nowa wiadomość</h3>
          <button className="compose-close-btn" onClick={onClose}>&times;</button>
        </header>
        <div className="compose-editor-area">
          <form className="compose-form">
            <div className="compose-input-group">
              <label htmlFor="recipient">Do:</label>
              <input id="recipient" type="email" className="compose-input" />
            </div>
            <div className="compose-input-group">
              <label htmlFor="subject">Temat:</label>
              <input id="subject" type="text" className="compose-input" />
            </div>
          </form>
          {/* Nowoczesny edytor Tiptap */}
          <div className="tiptap-editor-wrapper">
            <MenuBar editor={editor} />
            <EditorContent editor={editor} placeholder="Napisz swoją wiadomość..." />
          </div>
        </div>
        <div className="compose-actions">
          <button type="submit" className="compose-send-btn" onClick={(e) => { e.preventDefault(); onClose(); }}>
            Wyślij
          </button>
        </div>
      </div>
    </div>
  );
}

export default ComposeMail;