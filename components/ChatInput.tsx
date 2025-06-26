import React, { useState, useEffect, useRef } from 'react';
import { SendIcon } from './icons/SendIcon';
import { GOOGLE_CLIENT_ID } from '../constants'; // Import to check if Client ID is set

interface ChatInputProps {
  onSendMessage: (message: string) => void;
  isLoading: boolean;
  disabled?: boolean;
}

export const ChatInput: React.FC<ChatInputProps> = ({ onSendMessage, isLoading, disabled }) => {
  const [inputValue, setInputValue] = useState('');
  const textareaRef = useRef<HTMLTextAreaElement>(null);

  const isGClientIdSet = GOOGLE_CLIENT_ID && GOOGLE_CLIENT_ID !== 'YOUR_GOOGLE_CLIENT_ID_HERE';

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (inputValue.trim() && !isLoading && !disabled) {
      onSendMessage(inputValue);
      setInputValue('');
    }
  };

  const handleKeyPress = (e: React.KeyboardEvent<HTMLTextAreaElement>) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSubmit(e);
    }
  };
  
  useEffect(() => {
    if (textareaRef.current) {
      textareaRef.current.style.height = 'auto'; // Reset height
      textareaRef.current.style.height = `${textareaRef.current.scrollHeight}px`; // Set to scroll height
    }
  }, [inputValue]);

  const placeholderText = () => {
    if (!isGClientIdSet && !disabled) return "Google Client ID not set. Calendar features disabled.";
    if (disabled) return "Initializing or error occurred...";
    return "Type your message...";
  }
  
  const isEffectivelyDisabled = isLoading || disabled || (!isGClientIdSet && !disabled);


  return (
    <form onSubmit={handleSubmit} className="p-4 border-t border-slate-300 bg-slate-100 sticky bottom-0 z-10">
      <div className="flex items-start space-x-3 bg-white border border-slate-300 rounded-xl shadow-sm p-1 focus-within:ring-2 focus-within:ring-blue-500">
        <textarea
          ref={textareaRef}
          value={inputValue}
          onChange={(e) => setInputValue(e.target.value)}
          onKeyPress={handleKeyPress}
          placeholder={placeholderText()}
          className="flex-grow p-2.5 text-sm text-slate-700 bg-transparent border-none focus:ring-0 resize-none min-h-[2.5rem] max-h-32 leading-tight" // min-h for initial size, max-h for limit
          rows={1} // Start with one row, will expand
          disabled={isEffectivelyDisabled}
          style={{ overflowY: 'auto' }}
        />
        <button
          type="submit"
          disabled={isEffectivelyDisabled || !inputValue.trim()}
          className={`p-2.5 rounded-lg text-white transition-colors duration-150 ease-in-out self-end mb-1
            ${isEffectivelyDisabled || !inputValue.trim() ? 'bg-slate-400 cursor-not-allowed' : 'bg-blue-600 hover:bg-blue-700 focus:ring-2 focus:ring-blue-500 focus:ring-offset-1'}
          `}
          aria-label="Send message"
        >
          <SendIcon className="w-5 h-5" />
        </button>
      </div>
    </form>
  );
};
