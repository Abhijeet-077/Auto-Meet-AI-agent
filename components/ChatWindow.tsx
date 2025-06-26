
import React, { useEffect, useRef } from 'react';
import { Message } from '../types';
import { MessageBubble } from './MessageBubble';
import { LoadingIndicator } from './LoadingIndicator';

interface ChatWindowProps {
  messages: Message[];
  isLoadingInitial: boolean;
}

export const ChatWindow: React.FC<ChatWindowProps> = ({ messages, isLoadingInitial }) => {
  const messagesEndRef = useRef<null | HTMLDivElement>(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  if (isLoadingInitial) {
    return (
      <div className="flex-grow flex items-center justify-center p-4 bg-slate-50">
        <LoadingIndicator text="Initializing TailorTalk..." />
      </div>
    );
  }
  
  return (
    <div className="flex-grow overflow-y-auto p-6 space-y-4 bg-slate-50">
      {messages.map((msg) => (
        <MessageBubble key={msg.id} message={msg} />
      ))}
      <div ref={messagesEndRef} />
    </div>
  );
};
