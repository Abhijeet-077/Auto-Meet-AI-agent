
import { GoogleGenAI, Chat, GenerateContentResponse, GenerateContentParametersMessage } from "@google/genai";
import { SYSTEM_PROMPT } from '../constants';

let ai: GoogleGenAI | null = null;

const getAIInstance = (): GoogleGenAI => {
  if (!ai) {
    const apiKey = process.env.API_KEY;
    if (!apiKey) {
      console.error("API_KEY environment variable not set.");
      throw new Error("API_KEY environment variable not set. Please configure it to use TailorTalk.");
    }
    ai = new GoogleGenAI({ apiKey });
  }
  return ai;
};

export const initializeChat = async (): Promise<Chat> => {
  const genAI = getAIInstance();
  // Model and system instruction are crucial for the AI's behavior
  const chatSession = genAI.chats.create({
    model: 'gemini-2.5-flash-preview-04-17',
    config: {
      systemInstruction: SYSTEM_PROMPT,
      // No thinkingConfig for general chat, default is appropriate.
    },
    // history: [] // Start with an empty history, managed by the chat object itself.
  });
  return chatSession;
};

export const sendMessageStream = async (
  currentChat: Chat,
  messageText: string
): Promise<AsyncIterable<GenerateContentResponse>> => {
  if (!currentChat) {
    throw new Error("Chat session not initialized. Cannot send message.");
  }
  
  // The message parameter for sendMessageStream should be GenerateContentParameters
  // which includes a 'message' property.
  // The 'message' property can be string | Part | Array<string | Part>
  // Sending a simple string is fine here.
  const params: GenerateContentParametersMessage = { message: messageText };

  return currentChat.sendMessageStream(params);
};
