export enum Sender {
  USER = 'USER',
  AI = 'AI',
  SYSTEM = 'SYSTEM', // Added for system messages e.g. calendar confirmations
}

export interface Message {
  id: string;
  text: string;
  sender: Sender;
  timestamp: Date;
  error?: boolean;
  isLoading?: boolean; // For AI typing or system processing states
}