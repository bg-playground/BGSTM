import React, { useEffect } from 'react';

interface KeyboardShortcutsHelpProps {
  isOpen: boolean;
  onClose: () => void;
}

const shortcuts = [
  { key: '↑ / ↓', description: 'Navigate between suggestions' },
  { key: 'Enter', description: 'Open preview modal for focused suggestion' },
  { key: 'A', description: 'Accept focused suggestion' },
  { key: 'R', description: 'Reject focused suggestion' },
  { key: 'Space', description: 'Toggle selection checkbox' },
  { key: 'Shift + A', description: 'Accept all selected' },
  { key: 'Shift + R', description: 'Reject all selected' },
  { key: 'Ctrl/Cmd + A', description: 'Select all' },
  { key: 'Esc', description: 'Clear selection / Close modal' },
  { key: '?', description: 'Toggle this help panel' },
];

export const KeyboardShortcutsHelp: React.FC<KeyboardShortcutsHelpProps> = ({ isOpen, onClose }) => {
  useEffect(() => {
    const handleEscape = (e: KeyboardEvent) => {
      if (e.key === 'Escape') onClose();
    };

    if (isOpen) {
      document.addEventListener('keydown', handleEscape);
    }

    return () => {
      document.removeEventListener('keydown', handleEscape);
    };
  }, [isOpen, onClose]);

  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 z-50 overflow-y-auto" onClick={onClose}>
      <div className="flex items-center justify-center min-h-screen px-4 pt-4 pb-20 text-center sm:block sm:p-0">
        {/* Background overlay */}
        <div className="fixed inset-0 transition-opacity bg-gray-500 bg-opacity-75" />

        {/* Modal panel */}
        <div
          className="inline-block w-full max-w-2xl my-8 overflow-hidden text-left align-middle transition-all transform bg-white shadow-xl rounded-lg"
          onClick={(e) => e.stopPropagation()}
        >
          {/* Header */}
          <div className="flex items-center justify-between px-6 py-4 border-b bg-gray-50">
            <h2 className="text-2xl font-bold text-gray-900">Keyboard Shortcuts</h2>
            <button
              onClick={onClose}
              className="text-gray-400 hover:text-gray-600 transition-colors"
              aria-label="Close modal"
            >
              <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  strokeWidth={2}
                  d="M6 18L18 6M6 6l12 12"
                />
              </svg>
            </button>
          </div>

          {/* Content */}
          <div className="px-6 py-6">
            <p className="text-gray-600 mb-6">
              Use these keyboard shortcuts to review suggestions faster:
            </p>

            <div className="space-y-3">
              {shortcuts.map((shortcut, index) => (
                <div
                  key={index}
                  className="flex items-center justify-between p-3 bg-gray-50 rounded-lg hover:bg-gray-100 transition-colors"
                >
                  <span className="text-gray-900">{shortcut.description}</span>
                  <kbd className="px-3 py-1 text-sm font-semibold text-gray-800 bg-white border border-gray-300 rounded-lg shadow-sm">
                    {shortcut.key}
                  </kbd>
                </div>
              ))}
            </div>
          </div>

          {/* Footer */}
          <div className="flex items-center justify-end px-6 py-4 border-t bg-gray-50">
            <button
              onClick={onClose}
              className="px-6 py-2 bg-primary-600 text-white rounded-lg hover:bg-primary-700 transition-colors font-medium"
            >
              Got it!
            </button>
          </div>
        </div>
      </div>
    </div>
  );
};
