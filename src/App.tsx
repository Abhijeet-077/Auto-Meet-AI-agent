
import React, { useState, useEffect, useCallback } from 'react';
import { Header } from './components/Header';
import { ChatWindow } from './components/ChatWindow';
import { ChatInput } from './components/ChatInput';
import { Message, Sender } from './types';
import * as backendService from './services/geminiService';
import { INITIAL_AI_GREETING } from './constants';

const App: React.FC = () => {
  const [messages, setMessages] = useState<Message[]>([]);
  const [isLoadingInitial, setIsLoadingInitial] = useState<boolean>(true); // For initial page load/setup
  const [isAiTyping, setIsAiTyping] = useState<boolean>(false); // For AI "thinking" state affecting input
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    setIsLoadingInitial(true);
    setError(null);
    setMessages([
      {
        id: `ai-greeting-${Date.now()}`,
        text: INITIAL_AI_GREETING,
        sender: Sender.AI,
        timestamp: new Date(),
      },
    ]);
    setIsLoadingInitial(false);
  }, []);

  const handleSendMessage = useCallback(async (inputText: string) => {
    if (!inputText.trim() || isAiTyping) return;

    const userMessage: Message = {
      id: `user-${Date.now()}`,
      text: inputText,
      sender: Sender.USER,
      timestamp: new Date(),
    };
    
    const aiResponseId = `ai-response-${Date.now()}`;
    // Add user message & AI typing placeholder
    setMessages((prevMessages) => [
      ...prevMessages,
      userMessage,
      {
        id: aiResponseId,
        text: '', // Empty text, MessageBubble will show typing dots
        sender: Sender.AI,
        timestamp: new Date(),
        isLoading: true, // This message is loading
      },
    ]);
    setIsAiTyping(true);
    setError(null);

    try {
      // Pass existing messages (excluding the new AI placeholder) as history
      const historyForBackend = messages; // messages state before adding the AI placeholder
      const aiResponseText = await backendService.getBackendResponse(inputText, historyForBackend);

      setMessages((prevMessages) =>
        prevMessages.map((msg) =>
          msg.id === aiResponseId 
            ? { ...msg, text: aiResponseText, timestamp: new Date(), isLoading: false } 
            : msg
        )
      );
    } catch (err) {
      console.error("Failed to send message or get response:", err);
      const errorMessage = err instanceof Error ? err.message : "An error occurred while communicating with the AI.";
      setError(errorMessage); // Set general error for banner
      setMessages((prevMessages) =>
        prevMessages.map((msg) =>
          msg.id === aiResponseId 
            ? { ...msg, text: `Error: ${errorMessage}`, error: true, isLoading: false, timestamp: new Date() } 
            : msg
        )
      );
    } finally {
      setIsAiTyping(false);
    }
  }, [messages, isAiTyping]);

  return (
    <div className="flex flex-col h-screen max-w-3xl mx-auto bg-white shadow-2xl">
      <Header />
      {error && !messages.some(msg => msg.error && msg.text.includes(error)) && (
        <div className="p-4 bg-red-100 text-red-700 text-center">
          <p><strong>Application Error:</strong> {error}</p>
        </div>
      )}
      <ChatWindow messages={messages} isLoadingInitial={isLoadingInitial && messages.length <= 1} />
      <ChatInput onSendMessage={handleSendMessage} isLoading={isAiTyping} disabled={isLoadingInitial} />
    </div>
  );
};

export default App;
