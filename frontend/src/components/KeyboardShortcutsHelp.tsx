import React from 'react';

export const KeyboardShortcutsHelp: React.FC = () => {
  return (
    <div className="text-sm text-gray-600 mb-4 bg-gray-50 p-3 rounded">
      <strong>Keyboard Shortcuts:</strong>
      <kbd className="ml-2 px-2 py-1 bg-white border rounded">↑/↓</kbd> Navigate •{' '}
      <kbd className="ml-2 px-2 py-1 bg-white border rounded">Enter</kbd> Preview focused •{' '}
      <kbd className="ml-2 px-2 py-1 bg-white border rounded">Space</kbd> Toggle selection •{' '}
      <kbd className="ml-2 px-2 py-1 bg-white border rounded">A</kbd> Accept focused / Select all •{' '}
      <kbd className="ml-2 px-2 py-1 bg-white border rounded">R</kbd> Reject focused •{' '}
      <kbd className="ml-2 px-2 py-1 bg-white border rounded">C</kbd> Clear •{' '}
      <kbd className="ml-2 px-2 py-1 bg-white border rounded">Shift+Delete</kbd> Reject selected
    </div>
  );
};
