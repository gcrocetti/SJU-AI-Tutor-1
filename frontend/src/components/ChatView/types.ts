import { Message, AgentAction, Citation } from '../../types';

export interface ChatViewProps {
  initialMessages?: Message[];
}

export interface ChatInputProps {
  onSendMessage: (text: string) => void;
  isDisabled?: boolean;
}

export interface MessageListProps {
  messages: Message[];
  isTyping?: boolean;
}

export interface MessageItemProps {
  message: Message;
}

export interface ThinkingIndicatorProps {
  actions?: AgentAction[] | undefined;
}

export interface CitationListProps {
  citations?: Citation[] | undefined;
}