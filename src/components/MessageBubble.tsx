
import React from 'react';
import { Message, Sender } from '../types';
import { UserIcon } from './icons/UserIcon';
import { TailorTalkLogoIcon } from './icons/TailorTalkLogoIcon';

export const MessageBubble: React.FC<{ message: Message }> = ({ message }) => {
  const isUser = message.sender === Sender.USER;
  const bubbleClasses = isUser
    ? 'bg-blue-500 text-white self-end rounded-tl-xl rounded-tr-xl rounded-bl-xl'
    : 'bg-slate-200 text-slate-800 self-start rounded-tl-xl rounded-tr-xl rounded-br-xl';
  
  const alignmentClass = isUser ? 'items-end' : 'items-start';
  const iconOrderClass = isUser ? 'order-2' : 'order-1';
  const textOrderClass = isUser ? 'order-1' : 'order-2';
  const iconMarginClass = isUser ? 'ml-2' : 'mr-2';

  const IconComponent = isUser ? UserIcon : TailorTalkLogoIcon;

  const formatText = (text: string) => {
    text = text.replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>');
    text = text.replace(/\*(.*?)\*/g, '<em>$1</em>');
    text = text.replace(/\n/g, '<br />');
    return { __html: text };
  };
  
  return (
    <div className={`flex flex-col w-full ${alignmentClass}`}>
      <div className={`flex ${isUser ? 'flex-row-reverse' : 'flex-row'} items-end max-w-lg lg:max-w-xl`}>
        <IconComponent className={`w-8 h-8 p-1 rounded-full ${isUser ? 'bg-blue-400 text-white' : 'bg-slate-300 text-blue-600'} ${iconMarginClass} ${iconOrderClass} flex-shrink-0`} />
        <div
          className={`px-4 py-3 shadow-md ${bubbleClasses} ${textOrderClass} ${message.error ? 'bg-red-500 text-white' : ''}`}
        >
          {message.isLoading && message.sender === Sender.AI ? (
            <div className="flex items-center justify-center h-5 py-1"> {/* Typing indicator */}
              <div className="animate-pulse flex space-x-1">
                <div className="w-1.5 h-1.5 bg-slate-500 rounded-full"></div>
                <div className="w-1.5 h-1.5 bg-slate-500 rounded-full animation-delay-200" style={{animationDelay: '0.2s'}}></div>
                <div className="w-1.5 h-1.5 bg-slate-500 rounded-full animation-delay-400" style={{animationDelay: '0.4s'}}></div>
              </div>
            </div>
          ) : message.text ? (
             <p className="text-sm whitespace-pre-wrap" dangerouslySetInnerHTML={formatText(message.text)} />
          ) : (
            // Fallback for empty text if not loading (e.g. initial AI message before content)
            // This case should be rare if isLoading is handled correctly.
             <div className="flex items-center justify-center h-5 py-1"> 
              <div className="animate-pulse flex space-x-1">
                <div className="w-1.5 h-1.5 bg-current rounded-full"></div>
                <div className="w-1.5 h-1.5 bg-current rounded-full animation-delay-200" style={{animationDelay: '0.2s'}}></div>
                <div className="w-1.5 h-1.5 bg-current rounded-full animation-delay-400" style={{animationDelay: '0.4s'}}></div>
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
