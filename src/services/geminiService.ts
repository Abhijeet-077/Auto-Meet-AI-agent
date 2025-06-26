
import { Message, Sender } from '../types';

// API models matching backend/models.py
interface ApiChatMessage {
  role: string; // 'user' or 'model'
  content: string;
}

interface ChatRequestPayload {
  message: string;
  history: ApiChatMessage[];
}

interface ChatResponsePayload {
  reply: string;
}

// This function replaces the direct Gemini interactions
export const getBackendResponse = async (
  currentUserMessageText: string,
  chatHistory: Message[]
): Promise<string> => {
  // Prepare history, excluding any temporary AI "typing" messages
  const historyForBackend: ApiChatMessage[] = chatHistory
    .filter(msg => !(msg.isLoading && msg.sender === Sender.AI))
    .map(msg => ({
    role: msg.sender === Sender.USER ? 'user' : 'model', // Backend expects 'user' or 'model'
    content: msg.text,
  }));

  const payload: ChatRequestPayload = {
    message: currentUserMessageText,
    history: historyForBackend,
  };

  try {
    const response = await fetch('/api/chat_backend', { // URL to the FastAPI backend
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(payload),
    });

    if (!response.ok) {
      let errorData;
      try {
        errorData = await response.json();
      } catch (e) {
        throw new Error(`Network response was not ok: ${response.status} ${response.statusText}`);
      }
      const detail = errorData?.detail || `API request failed with status ${response.status}`;
      throw new Error(String(detail));
    }

    const data: ChatResponsePayload = await response.json();
    return data.reply;

  } catch (error) {
    console.error("Error fetching backend response:", error);
    if (error instanceof Error) {
        throw new Error(`Failed to get response from TailorTalk assistant: ${error.message}`);
    }
    throw new Error("An unknown error occurred while contacting the TailorTalk assistant.");
  }
};
