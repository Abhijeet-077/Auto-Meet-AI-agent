
export enum Sender {
  USER = 'USER',
  AI = 'AI',
}

export interface Message {
  id: string;
  text: string;
  sender: Sender;
  timestamp: Date;
  error?: boolean;
  isLoading?: boolean; // New: for AI typing indicator on a specific bubble
}
