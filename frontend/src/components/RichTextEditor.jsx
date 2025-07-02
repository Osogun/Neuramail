// src/components/RichTextEditor.jsx

import React from 'react';
import { useEditor, EditorContent } from '@tiptap/react';
import StarterKit from '@tiptap/starter-kit';
import './RichTextEditor.css'; // Dodamy style w następnym kroku

// Komponent paska narzędzi
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
      <button type="button" onClick={() => editor.chain().focus().setParagraph().run()} className={editor.isActive('paragraph') ? 'is-active' : ''}>
        ¶
      </button>
    </div>
  );
};

const RichTextEditor = ({ value, onChange, placeholder }) => {
  const editor = useEditor({
    extensions: [
      StarterKit.configure({
        // Możemy wyłączyć opcje, których nie potrzebujemy
        heading: false,
        bulletList: false,
        orderedList: false,
      }),
    ],
    content: value,
    onUpdate: ({ editor }) => {
      onChange(editor.getHTML());
    },
    editorProps: {
      attributes: {
        class: 'tiptap-editor-prose',
      },
    },
  });

  return (
    <div className="tiptap-editor-wrapper">
      <MenuBar editor={editor} />
      <EditorContent editor={editor} placeholder={placeholder} />
    </div>
  );
};

export default RichTextEditor;