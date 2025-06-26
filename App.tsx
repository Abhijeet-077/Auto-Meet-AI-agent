
import React, { useState, useEffect, useCallback, useRef } from 'react';
import { Chat } from "@google/genai";
import { Header } from './components/Header';
import { ChatWindow } from './components/ChatWindow';
import { ChatInput } from './components/ChatInput';
import { Message, Sender } from './types';
import * as geminiService from './services/geminiService';
import * as calendarService from './services/googleCalendarService';
import { 
  INITIAL_AI_GREETING, 
  NOT_CONNECTED_MESSAGE, 
  GOOGLE_CLIENT_ID,
  PROMPT_FOR_CALENDAR_ACTION_CONFIRMATION,
  CALENDAR_CHECKING_MESSAGE,
  CALENDAR_BOOKING_MESSAGE
} from './constants';

// Helper to add a message to the chat
const addMessageToList = (
  text: string,
  sender: Sender,
  error: boolean = false,
  isLoading: boolean = false
): Message => ({
  id: `${sender.toLowerCase()}-${Date.now()}`,
  text,
  sender,
  timestamp: new Date(),
  error,
  isLoading,
});


const App: React.FC = () => {
  const [messages, setMessages] = useState<Message[]>([]);
  const [isLoading, setIsLoading] = useState<boolean>(true); // For AI responses
  const [error, setError] = useState<string | null>(null);
  const [chatSession, setChatSession] = useState<Chat | null>(null);

  // Google Calendar State
  const [googleUser, setGoogleUser] = useState<calendarService.GoogleUser | null>(null);
  const [isGoogleCalendarConnected, setIsGoogleCalendarConnected] = useState<boolean>(false);
  const [googleAccessToken, setGoogleAccessToken] = useState<string | null>(null);
  const [isInitializingGis, setIsInitializingGis] = useState<boolean>(true);
  const [pendingCalendarAction, setPendingCalendarAction] = useState<{type: 'check_availability' | 'create_event', details?: any} | null>(null);

  const isGClientIdSet = GOOGLE_CLIENT_ID && GOOGLE_CLIENT_ID !== 'YOUR_GOOGLE_CLIENT_ID_HERE';

  // Initialize Chat and Google Services
  useEffect(() => {
    const initApp = async () => {
      setIsLoading(true); // Overall app loading
      setError(null);
      try {
        const session = await geminiService.initializeChat();
        setChatSession(session);
        setMessages([addMessageToList(INITIAL_AI_GREETING, Sender.AI)]);
      } catch (err) {
        console.error("Failed to initialize chat:", err);
        const errorMessage = err instanceof Error ? err.message : "Failed to initialize chat. Ensure API_KEY is set.";
        setError(errorMessage);
        setMessages([addMessageToList(`Error: ${errorMessage}`, Sender.SYSTEM, true)]);
      } finally {
        setIsLoading(false); // Done with chat init
      }

      if (!isGClientIdSet) {
        const gcalError = "Google Client ID not configured. Calendar features disabled.";
        console.warn(gcalError);
        setMessages(prev => [...prev, addMessageToList(gcalError, Sender.SYSTEM, true)]);
        setIsInitializingGis(false);
        return;
      }
      
      try {
        await calendarService.initializeTokenClient(
          async (tokenResponse) => { // On success
            setGoogleAccessToken(tokenResponse.access_token);
            setIsGoogleCalendarConnected(true);
            const profile = await calendarService.getGoogleUserProfile(tokenResponse.access_token);
            if (profile) setGoogleUser(profile);
            setMessages(prev => [...prev, addMessageToList(`Connected to Google Calendar as ${profile?.email || 'your account'}.`, Sender.SYSTEM)]);
            if (pendingCalendarAction) { // If an action was pending user login
              handleConfirmedCalendarAction(pendingCalendarAction.type, pendingCalendarAction.details);
              setPendingCalendarAction(null);
            }
          },
          (errorResponse) => { // On error
            console.error('Google Calendar auth error response object:', errorResponse);
            
            let specificErrorMessage = "Authentication failed.";
            if (typeof errorResponse === 'string') {
              specificErrorMessage = errorResponse;
            } else if (errorResponse && typeof errorResponse === 'object') {
              // GIS often returns error in errorResponse.error or errorResponse.details
              specificErrorMessage = errorResponse.details || errorResponse.error || (errorResponse.message || "Authentication failed.");
            }

            if (specificErrorMessage.toLowerCase().includes('popup_closed') || specificErrorMessage.toLowerCase().includes('popup window closed')) {
              console.warn('Google Sign-In popup was closed by the user or failed to open.');
              setMessages(prev => [...prev, addMessageToList("Google Sign-In was cancelled or the popup was blocked. Please try connecting again if you wish to use calendar features.", Sender.SYSTEM, false)]);
            } else {
              setError(`Google Calendar Error: ${specificErrorMessage}`);
              setMessages(prev => [...prev, addMessageToList(`Failed to connect to Google Calendar: ${specificErrorMessage}`, Sender.SYSTEM, true)]);
            }
            setIsGoogleCalendarConnected(false);
            setGoogleUser(null);
            setGoogleAccessToken(null);
          }
        );
      } catch (e) {
         console.error("Error setting up Google Calendar service:", e);
         const initErrorMsg = e instanceof Error ? e.message : "Could not initialize Google Calendar services.";
         setError(initErrorMsg);
         setMessages(prev => [...prev, addMessageToList(`Error initializing Google Calendar: ${initErrorMsg}`, Sender.SYSTEM, true)]);
      } finally {
        setIsInitializingGis(false);
      }
    };
    initApp();
  }, [isGClientIdSet]); // Removed pendingCalendarAction from deps as it's handled inside the success callback


  const handleConnectGoogleCalendar = () => {
    if (!isGClientIdSet) {
       setMessages(prev => [...prev, addMessageToList("Google Client ID is not configured. Cannot connect.", Sender.SYSTEM, true)]);
       return;
    }
    if (isInitializingGis || !calendarService.requestGoogleAccessToken) {
        setMessages(prev => [...prev, addMessageToList("Google services are still initializing. Please wait a moment.", Sender.SYSTEM, true)]);
        return;
    }
    try {
        // Clear previous transient errors before attempting to connect
        setError(null); 
        calendarService.requestGoogleAccessToken();
    } catch (e) {
        const errMessage = e instanceof Error ? e.message : "Could not start Google Sign-In.";
        setMessages(prev => [...prev, addMessageToList(errMessage, Sender.SYSTEM, true)]);
        setError(errMessage); // Also set general error if request itself fails
    }
  };

  const handleDisconnectGoogleCalendar = async () => {
    if (googleAccessToken) {
      try {
        await calendarService.revokeGoogleAccessToken(googleAccessToken);
      } catch (e) {
        console.warn("Error revoking token (might be already invalid):", e);
      }
    }
    setGoogleAccessToken(null);
    setGoogleUser(null);
    setIsGoogleCalendarConnected(false);
    setMessages(prev => [...prev, addMessageToList("Disconnected from Google Calendar.", Sender.SYSTEM)]);
  };
  
  // This function would be called after AI suggests an action and user confirms (e.g. by typing "yes")
  const handleConfirmedCalendarAction = async (actionType: 'check_availability' | 'create_event', details?: any) => {
    if (!isGoogleCalendarConnected || !googleAccessToken) {
      setMessages(prev => [...prev, addMessageToList(NOT_CONNECTED_MESSAGE, Sender.AI)]);
      setPendingCalendarAction({ type: actionType, details });
      // Suggest connection, but don't auto-trigger popup if user explicitly denied/closed before.
      // User can click connect button.
      // handleConnectGoogleCalendar(); // Reconsider auto-popup
      return;
    }

    setIsLoading(true); // Show general loading for calendar action
    let systemMessageText = '';
    let actionSuccess = false;
    let newAiPromptContext = '';

    // Remove any previous "loading" system messages before adding a new one
    setMessages(prev => prev.filter(m => !(m.sender === Sender.SYSTEM && m.isLoading)));

    try {
      if (actionType === 'check_availability') {
        setMessages(prev => [...prev, addMessageToList(CALENDAR_CHECKING_MESSAGE, Sender.SYSTEM, false, true)]);
        const { timeMin, timeMax } = details || { 
          timeMin: new Date().toISOString(), 
          timeMax: new Date(Date.now() + 7 * 24 * 60 * 60 * 1000).toISOString() 
        };
        const events = await calendarService.listCalendarEvents(googleAccessToken, timeMin, timeMax);
        systemMessageText = `Found ${events.length} event(s) between ${new Date(timeMin).toLocaleDateString()} and ${new Date(timeMax).toLocaleDateString()}.`;
        if (events.length > 0) {
          systemMessageText += ` Busy slots: ${events.map(e => `${e.summary || '(No title)'} on ${new Date(e.start.dateTime || e.start.date).toLocaleString()}`).join(', ')}.`;
        } else {
          systemMessageText += " No busy slots found in this period.";
        }
        newAiPromptContext = `System check of calendar for ${timeMin} to ${timeMax}: ${systemMessageText}. Now advise user.`;
        actionSuccess = true;
      } else if (actionType === 'create_event') {
         setMessages(prev => [...prev, addMessageToList(CALENDAR_BOOKING_MESSAGE, Sender.SYSTEM, false, true)]);
        if (!details || !details.summary || !details.start || !details.end) {
          throw new Error("Missing details for creating event. Please ensure the AI provides summary, start, and end times.");
        }
        const createdEvent = await calendarService.createCalendarEvent(googleAccessToken, details);
        systemMessageText = `Appointment "${createdEvent.summary}" booked successfully from ${new Date(createdEvent.start.dateTime).toLocaleString()} to ${new Date(createdEvent.end.dateTime).toLocaleString()}. Link: ${createdEvent.htmlLink}`;
        newAiPromptContext = `System successfully booked event: ${details.summary} for ${details.start.dateTime}. Confirm with user.`;
        actionSuccess = true;
      }
    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : "An error occurred with Google Calendar.";
      systemMessageText = `Google Calendar Error: ${errorMessage}`;
      newAiPromptContext = `System encountered an error with Google Calendar action (${actionType}): ${errorMessage}. Inform the user and ask how to proceed.`;
      actionSuccess = false;
    } finally {
      setMessages(prev => prev.filter(m => !(m.sender === Sender.SYSTEM && m.isLoading)));
      setMessages(prev => [...prev, addMessageToList(systemMessageText, Sender.SYSTEM, !actionSuccess)]);
      setIsLoading(false);
      setPendingCalendarAction(null);

      if (newAiPromptContext && chatSession) {
        await sendInternalMessageToAI(newAiPromptContext);
      }
    }
  };
  
  const sendInternalMessageToAI = async (internalText: string) => {
    if (!chatSession || !internalText) return;
    setIsLoading(true);
    const aiResponseId = `ai-internal-response-${Date.now()}`;
    setMessages((prevMessages) => [
      ...prevMessages,
      addMessageToList('', Sender.AI, false, true), 
    ]);
    
    try {
      const stream = await geminiService.sendMessageStream(chatSession, `System context: ${internalText}`);
      let currentAiText = '';
      for await (const chunk of stream) {
        currentAiText += chunk.text;
        setMessages((prevMessages) =>
          prevMessages.map((msg) =>
            msg.isLoading && msg.sender === Sender.AI && msg.text === '' // Find the latest empty AI loading bubble
              ? { ...msg, text: currentAiText, id: aiResponseId } 
              : msg
          )
        );
      }
       setMessages((prevMessages) => prevMessages.map(m => m.id === aiResponseId ? {...m, isLoading: false} : m));
    } catch (err) {
       console.error("Failed to send internal message to AI:", err);
       const errorMessage = err instanceof Error ? err.message : "An error occurred with AI.";
       setMessages((prevMessages) =>
        prevMessages.map((msg) =>
          msg.isLoading && msg.sender === Sender.AI && msg.id === aiResponseId
            ? { ...msg, text: `Error processing system context: ${errorMessage}`, error: true, isLoading: false }
            : msg
        )
      );
    } finally {
      setIsLoading(false);
    }
  };

  const handleSendMessage = useCallback(async (inputText: string) => {
    if (!inputText.trim() || isLoading || !chatSession) return;

    const userMessage = addMessageToList(inputText, Sender.USER);
    setMessages((prevMessages) => [...prevMessages, userMessage]);
    setIsLoading(true);
    setError(null); 

    if (pendingCalendarAction && (inputText.toLowerCase().includes('yes') || inputText.toLowerCase().includes('ok') || inputText.toLowerCase().includes('proceed') || inputText.toLowerCase().includes('alright'))) {
      const actionToConfirm = pendingCalendarAction; // Capture before clearing
      setPendingCalendarAction(null); // Clear pending action first
      await handleConfirmedCalendarAction(actionToConfirm.type, actionToConfirm.details);
      setIsLoading(false); 
      return;
    }
    
    // Reset pending action if user says "no" or something unrelated
    if (pendingCalendarAction) {
        setPendingCalendarAction(null); 
    }

    const aiResponseId = `ai-user-response-${Date.now()}`;
    setMessages((prevMessages) => [
      ...prevMessages,
      addMessageToList('', Sender.AI, false, true),
    ]);

    try {
      const stream = await geminiService.sendMessageStream(chatSession, inputText);
      let currentAiText = '';
      for await (const chunk of stream) {
        currentAiText += chunk.text;
        setMessages((prevMessages) =>
          prevMessages.map((msg) =>
            msg.isLoading && msg.sender === Sender.AI && msg.text === ''
              ? { ...msg, text: currentAiText, id: aiResponseId }
              : msg
          )
        );
      }
      setMessages((prevMessages) => prevMessages.map(m => m.id === aiResponseId ? {...m, isLoading: false} : m));

      // Basic intent parsing from AI response to set pendingCalendarAction
      const lowerAiText = currentAiText.toLowerCase();
      if ((lowerAiText.includes("shall i check your availability") || lowerAiText.includes("check your calendar")) && isGoogleCalendarConnected) {
         setPendingCalendarAction({ type: 'check_availability', details: { /* TODO: parse date/time from AI/user context for details */ } });
         // Optionally add system message: "AI is asking to check availability. Type 'yes' to confirm."
      } else if ((lowerAiText.includes("should i go ahead and book") || lowerAiText.includes("confirm booking")) && isGoogleCalendarConnected) {
         setPendingCalendarAction({ type: 'create_event', details: { /* TODO: parse event details from AI/user context */ } });
      } else if (lowerAiText.includes("please connect it using the button") || lowerAiText.includes("connect your google calendar")) {
        // If AI asks to connect, and user is already connected, this might be a misinterpretation by AI.
        // Or if user is NOT connected, this is correct. No specific pending action here.
      }


    } catch (err) {
      console.error("Failed to send message or get response:", err);
      const errorMessage = err instanceof Error ? err.message : "An error occurred while communicating with the AI.";
      setError(errorMessage);
      setMessages((prevMessages) =>
        prevMessages.map((msg) =>
          msg.isLoading && msg.sender === Sender.AI && msg.id === aiResponseId
            ? { ...msg, text: `Error: ${errorMessage}`, error: true, isLoading: false }
            : msg
        )
      );
    } finally {
      setIsLoading(false);
    }
  }, [isLoading, chatSession, messages, isGoogleCalendarConnected, pendingCalendarAction, googleAccessToken]); // Added googleAccessToken as it's used in handleConfirmedCalendarAction

  return (
    <div className="flex flex-col h-screen max-w-3xl mx-auto bg-white shadow-2xl">
      <Header
        googleUser={googleUser}
        isGoogleCalendarConnected={isGoogleCalendarConnected}
        onConnectGoogleCalendar={handleConnectGoogleCalendar}
        onDisconnectGoogleCalendar={handleDisconnectGoogleCalendar}
        isInitializingGis={isInitializingGis || (isLoading && !chatSession)}
      />
      {error && !messages.some(msg => msg.sender === Sender.SYSTEM && msg.error && msg.text.includes(error)) && (
        <div className="p-3 bg-red-100 text-red-700 text-center text-sm border-b border-red-200">
          <p><strong>Application Error:</strong> {error}</p>
        </div>
      )}
      <ChatWindow messages={messages} isLoadingInitial={isLoading && messages.length <= 1 && !chatSession} />
      <ChatInput 
        onSendMessage={handleSendMessage} 
        isLoading={isLoading || isInitializingGis} 
        disabled={!chatSession || !!error || isInitializingGis || !isGClientIdSet} 
      />
    </div>
  );
};

export default App;
