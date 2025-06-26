import React from 'react';
import { Message, Sender } from '../types';
import { UserIcon } from './icons/UserIcon';
import { TailorTalkLogoIcon } from './icons/TailorTalkLogoIcon'; 
import { SystemIcon } from './icons/SystemIcon'; // Create this icon

export const MessageBubble: React.FC<{ message: Message }> = ({ message }) => {
  const isUser = message.sender === Sender.USER;
  const isAI = message.sender === Sender.AI;
  const isSystem = message.sender === Sender.SYSTEM;

  let bubbleClasses = '';
  let alignmentClass = '';
  let iconOrderClass = '';
  let textOrderClass = '';
  let iconMarginClass = '';
  let IconComponent: React.FC<{className?: string}> = UserIcon; // Default

  if (isUser) {
    bubbleClasses = 'bg-blue-500 text-white self-end rounded-tl-xl rounded-tr-xl rounded-bl-xl';
    alignmentClass = 'items-end';
    iconOrderClass = 'order-2';
    textOrderClass = 'order-1';
    iconMarginClass = 'ml-2';
    IconComponent = UserIcon;
  } else if (isAI) {
    bubbleClasses = 'bg-slate-200 text-slate-800 self-start rounded-tl-xl rounded-tr-xl rounded-br-xl';
    alignmentClass = 'items-start';
    iconOrderClass = 'order-1';
    textOrderClass = 'order-2';
    iconMarginClass = 'mr-2';
    IconComponent = TailorTalkLogoIcon;
  } else if (isSystem) {
    bubbleClasses = 'bg-amber-100 text-amber-800 self-center rounded-lg w-auto max-w-md lg:max-w-lg mx-auto border border-amber-300';
    alignmentClass = 'items-center justify-center'; // Center system messages
    // No icon for system messages in this layout, or a specific system icon
    IconComponent = SystemIcon; // Or null if no icon
  }
  
  const formatText = (text: string) => {
    text = text.replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>');
    text = text.replace(/\*(.*?)\*/g, '<em>$1</em>');
    text = text.replace(/\n/g, '<br />');
    return { __html: text };
  };
  
  // System messages are simpler, centered, no icon beside bubble typically
  if (isSystem) {
    return (
      <div className={`flex flex-col w-full ${alignmentClass} my-2`}>
        <div className={`px-4 py-2 shadow-sm ${bubbleClasses} ${message.error ? 'bg-red-200 text-red-800 border-red-400' : ''}`}>
           <div className="flex items-center space-x-2">
            {!message.error && <SystemIcon className="w-5 h-5 text-amber-600 flex-shrink-0" />}
            {message.error && <SystemIcon className="w-5 h-5 text-red-600 flex-shrink-0" />} {/*  Adjust icon for error */}
            <p className="text-xs sm:text-sm" dangerouslySetInnerHTML={formatText(message.text)} />
           </div>
        </div>
         <p className="text-xs text-slate-400 mt-1 text-center">
            {message.timestamp.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}
        </p>
      </div>
    );
  }

  // User and AI messages
  return (
    <div className={`flex flex-col w-full ${alignmentClass}`}>
      <div className={`flex ${isUser ? 'flex-row-reverse' : 'flex-row'} items-end max-w-lg lg:max-w-xl`}>
        <IconComponent className={`w-8 h-8 p-1 rounded-full ${isUser ? 'bg-blue-400 text-white' : 'bg-slate-300 text-blue-600'} ${iconMarginClass} ${iconOrderClass} flex-shrink-0`} />
        <div
          className={`px-4 py-3 shadow-md ${bubbleClasses} ${textOrderClass} ${message.error ? 'bg-red-500 text-white' : ''}`}
        >
          {message.isLoading && isAI ? (
            <div className="flex items-center justify-center h-5 py-1"> {/* Typing indicator for AI */}
              <div className="animate-pulse flex space-x-1">
                <div className="w-1.5 h-1.5 bg-slate-500 rounded-full"></div>
                <div className="w-1.5 h-1.5 bg-slate-500 rounded-full animation-delay-200" style={{animationDelay: '0.2s'}}></div>
                <div className="w-1.5 h-1.5 bg-slate-500 rounded-full animation-delay-400" style={{animationDelay: '0.4s'}}></div>
              </div>
            </div>
          ) : message.text ? (
             <p className="text-sm whitespace-pre-wrap" dangerouslySetInnerHTML={formatText(message.text)} />
          ) : (
            // Fallback for empty text if not loading (should be rare)
             <div className="flex items-center justify-center h-5 py-1"> 
              <div className="animate-pulse flex space-x-1">
                <div className={`w-1.5 h-1.5 ${isUser ? 'bg-white' : 'bg-slate-500'} rounded-full`}></div>
                <div className={`w-1.5 h-1.5 ${isUser ? 'bg-white' : 'bg-slate-500'} rounded-full animation-delay-200`} style={{animationDelay: '0.2s'}}></div>
                <div className={`w-1.5 h-1.5 ${isUser ? 'bg-white' : 'bg-slate-500'} rounded-full animation-delay-400`} style={{animationDelay: '0.4s'}}></div>
              </div>
            </div>
          )}
        </div>
      </div>
      <p className={`text-xs text-slate-500 mt-1 ${isUser ? 'text-right' : 'text-left'} px-10`}>
        {message.timestamp.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}
      </p>
    </div>
  );
};
