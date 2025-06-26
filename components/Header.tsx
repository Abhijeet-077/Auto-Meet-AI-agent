import React from 'react';
import { TailorTalkLogoIcon } from './icons/TailorTalkLogoIcon';
import { CalendarIcon } from './icons/CalendarIcon'; // Assuming you'll create this
import { GoogleUser } from '../services/googleCalendarService';

interface HeaderProps {
  googleUser: GoogleUser | null;
  isGoogleCalendarConnected: boolean;
  onConnectGoogleCalendar: () => void;
  onDisconnectGoogleCalendar: () => void;
  isInitializingGis: boolean;
}

export const Header: React.FC<HeaderProps> = ({
  googleUser,
  isGoogleCalendarConnected,
  onConnectGoogleCalendar,
  onDisconnectGoogleCalendar,
  isInitializingGis,
}) => {
  return (
    <header className="bg-gradient-to-r from-blue-600 to-indigo-700 text-white p-4 shadow-md flex items-center justify-between sticky top-0 z-20">
      <div className="flex items-center space-x-3">
        <TailorTalkLogoIcon className="w-10 h-10" />
        <h1 className="text-2xl font-bold tracking-tight">TailorTalk</h1>
      </div>
      <div className="flex items-center space-x-3">
        {isGoogleCalendarConnected && googleUser && (
          <div className="text-sm hidden sm:block">
            <span className="font-medium">{googleUser.name || googleUser.email}</span>
          </div>
        )}
        {isInitializingGis ? (
          <button
            className="flex items-center space-x-2 bg-slate-500 text-white px-3 py-2 rounded-md text-sm font-medium cursor-wait"
            disabled
          >
            <CalendarIcon className="w-5 h-5" />
            <span>Initializing...</span>
          </button>
        ) : isGoogleCalendarConnected ? (
          <button
            onClick={onDisconnectGoogleCalendar}
            className="flex items-center space-x-2 bg-red-500 hover:bg-red-600 text-white px-3 py-2 rounded-md text-sm font-medium transition-colors"
            title="Disconnect Google Calendar"
          >
            <CalendarIcon className="w-5 h-5" />
            <span>Disconnect</span>
          </button>
        ) : (
          <button
            onClick={onConnectGoogleCalendar}
            className="flex items-center space-x-2 bg-green-500 hover:bg-green-600 text-white px-3 py-2 rounded-md text-sm font-medium transition-colors"
            title="Connect Google Calendar"
          >
             <CalendarIcon className="w-5 h-5" />
            <span>Connect Calendar</span>
          </button>
        )}
      </div>
    </header>
  );
};
