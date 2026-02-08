'use client';

import React, { useState, useRef, useEffect, useCallback } from 'react';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Textarea } from '@/components/ui/textarea';
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogHeader,
  DialogTitle,
  DialogFooter,
} from '@/components/ui/dialog';
import { AiAgentMessage, AiAgentState } from '@/types/themes.types';
import { createBuilderWebSocket, sendBuilderPrompt } from '@/handles/themes.handles';
import { Bot, Send, Loader2, Wifi, WifiOff, Settings2 } from 'lucide-react';
import { cn } from '@/lib/utils';

interface AiAgentPanelProps {
  storeId: string;
  themeId: string;
  templateId: string;
  onContentGenerated: (content: string) => void;
}

export function AiAgentPanel({ storeId, themeId, templateId, onContentGenerated }: AiAgentPanelProps) {
  const [state, setState] = useState<AiAgentState>({
    messages: [],
    isConnected: false,
    isGenerating: false,
  });
  const [input, setInput] = useState('');
  const [showConnectModal, setShowConnectModal] = useState(false);
  const [wsUrl, setWsUrl] = useState(
    process.env.NEXT_PUBLIC_WS_URL || 'ws://localhost:8000'
  );
  const wsRef = useRef<WebSocket | null>(null);
  const messagesEndRef = useRef<HTMLDivElement>(null);

  const scrollToBottom = useCallback(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, []);

  useEffect(() => {
    scrollToBottom();
  }, [state.messages, scrollToBottom]);

  // Cleanup WebSocket on unmount
  useEffect(() => {
    return () => {
      wsRef.current?.close();
    };
  }, []);

  const handleConnect = useCallback(() => {
    if (!themeId) return;

    // Close existing connection
    wsRef.current?.close();

    wsRef.current = createBuilderWebSocket(
      themeId,
      (data) => {
        if (data.type === 'content') {
          onContentGenerated(data.content);
          setState((s) => ({
            ...s,
            isGenerating: false,
            messages: [
              ...s.messages,
              {
                id: Date.now().toString(),
                role: 'assistant',
                content: data.content.substring(0, 200) + '... (template updated)',
                timestamp: new Date().toISOString(),
                status: 'complete',
              },
            ],
          }));
        } else if (data.type === 'error') {
          setState((s) => ({
            ...s,
            isGenerating: false,
            messages: [
              ...s.messages,
              {
                id: Date.now().toString(),
                role: 'system',
                content: `Error: ${data.content}`,
                timestamp: new Date().toISOString(),
                status: 'error',
              },
            ],
          }));
        } else if (data.type === 'status' && data.status === 'streaming') {
          setState((s) => ({ ...s, isGenerating: true }));
        }
      },
      () => setState((s) => ({ ...s, isConnected: false })),
      () => setState((s) => ({ ...s, isConnected: false })),
    );

    if (wsRef.current) {
      wsRef.current.onopen = () => {
        setState((s) => ({ ...s, isConnected: true }));
        setShowConnectModal(false);
      };
    }
  }, [themeId, onContentGenerated]);

  const handleDisconnect = useCallback(() => {
    wsRef.current?.close();
    wsRef.current = null;
    setState((s) => ({ ...s, isConnected: false }));
  }, []);

  const handleSend = () => {
    const trimmed = input.trim();
    if (!trimmed) return;

    const userMessage: AiAgentMessage = {
      id: Date.now().toString(),
      role: 'user',
      content: trimmed,
      timestamp: new Date().toISOString(),
    };

    setState((s) => ({
      ...s,
      messages: [...s.messages, userMessage],
      isGenerating: true,
    }));
    setInput('');

    if (wsRef.current && wsRef.current.readyState === WebSocket.OPEN) {
      sendBuilderPrompt(wsRef.current, trimmed, templateId);
    } else {
      setTimeout(() => {
        setState((s) => ({
          ...s,
          isGenerating: false,
          messages: [
            ...s.messages,
            {
              id: (Date.now() + 1).toString(),
              role: 'system',
              content: 'Not connected. Click "Connect" to establish a WebSocket connection first.',
              timestamp: new Date().toISOString(),
              status: 'error',
            },
          ],
        }));
      }, 300);
    }
  };

  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSend();
    }
  };

  return (
    <div className="flex flex-col h-full">
      {/* Header */}
      <div className="p-3 border-b border-gray-200 flex items-center justify-between">
        <div className="flex items-center gap-2">
          <Bot className="h-4 w-4 text-blue-600" />
          <span className="text-sm font-medium">AI Agent</span>
        </div>
        <div className="flex items-center gap-1">
          {state.isConnected ? (
            <button
              onClick={handleDisconnect}
              className="flex items-center gap-1 text-xs px-2 py-1 rounded-full bg-green-100 text-green-700 hover:bg-green-200"
              title="Connected — click to disconnect"
            >
              <Wifi className="h-3 w-3" />
              Connected
            </button>
          ) : (
            <button
              onClick={() => setShowConnectModal(true)}
              className="flex items-center gap-1 text-xs px-2 py-1 rounded-full bg-gray-100 text-gray-500 hover:bg-gray-200"
              title="Click to connect"
            >
              <WifiOff className="h-3 w-3" />
              Connect
            </button>
          )}
        </div>
      </div>

      {/* Messages */}
      <div className="flex-1 overflow-y-auto p-3 space-y-3">
        {state.messages.length === 0 && (
          <div className="text-center py-8">
            <Bot className="h-8 w-8 mx-auto text-gray-300 mb-3" />
            <p className="text-sm text-gray-500">
              Describe the design you want to create or modify.
            </p>
            <p className="text-xs text-gray-400 mt-1">
              e.g. &quot;Create a modern hero section with a gradient background&quot;
            </p>
            {!state.isConnected && (
              <Button
                size="sm"
                variant="outline"
                className="mt-4"
                onClick={() => setShowConnectModal(true)}
              >
                <Settings2 className="h-3.5 w-3.5 mr-1.5" />
                Connect to AI Agent
              </Button>
            )}
          </div>
        )}

        {state.messages.map((msg) => (
          <div
            key={msg.id}
            className={cn(
              'text-sm rounded-lg px-3 py-2',
              msg.role === 'user'
                ? 'bg-blue-600 text-white ml-4'
                : msg.role === 'system'
                ? 'bg-red-50 text-red-700 border border-red-200'
                : 'bg-gray-100 text-gray-800 mr-4'
            )}
          >
            {msg.content}
          </div>
        ))}

        {state.isGenerating && (
          <div className="flex items-center gap-2 text-sm text-gray-500">
            <Loader2 className="h-3 w-3 animate-spin" />
            Generating...
          </div>
        )}

        <div ref={messagesEndRef} />
      </div>

      {/* Input */}
      <div className="p-3 border-t border-gray-200">
        <div className="flex gap-2">
          <Textarea
            value={input}
            onChange={(e) => setInput(e.target.value)}
            onKeyDown={handleKeyDown}
            placeholder={state.isConnected ? 'Describe what you want to build...' : 'Connect first to start chatting...'}
            className="min-h-[60px] max-h-[120px] resize-none text-sm"
            rows={2}
            disabled={!state.isConnected}
          />
          <Button
            size="sm"
            onClick={handleSend}
            disabled={!input.trim() || state.isGenerating || !state.isConnected}
            className="self-end"
          >
            <Send className="h-4 w-4" />
          </Button>
        </div>
      </div>

      {/* Connect Modal */}
      <Dialog open={showConnectModal} onOpenChange={setShowConnectModal}>
        <DialogContent className="sm:max-w-md">
          <DialogHeader>
            <DialogTitle>Connect to AI Agent</DialogTitle>
            <DialogDescription>
              Configure the WebSocket connection to the AI builder agent.
            </DialogDescription>
          </DialogHeader>

          <div className="space-y-4 py-2">
            <div>
              <Label className="text-sm">WebSocket URL</Label>
              <Input
                value={wsUrl}
                onChange={(e) => setWsUrl(e.target.value)}
                className="mt-1"
                placeholder="ws://localhost:8000"
              />
              <p className="text-xs text-gray-400 mt-1">
                The agent will connect to: {wsUrl}/ws/builder/{themeId || '<theme_id>'}/
              </p>
            </div>

            <div className="bg-gray-50 rounded-md p-3 space-y-1.5">
              <p className="text-xs font-medium text-gray-600">Connection Details</p>
              <div className="text-xs text-gray-500 space-y-0.5">
                <p><span className="font-medium">Store:</span> {storeId}</p>
                <p><span className="font-medium">Theme:</span> {themeId || 'None selected'}</p>
                <p><span className="font-medium">Template:</span> {templateId || 'None selected'}</p>
              </div>
            </div>
          </div>

          <DialogFooter>
            <Button variant="outline" onClick={() => setShowConnectModal(false)}>
              Cancel
            </Button>
            <Button onClick={handleConnect} disabled={!themeId}>
              <Wifi className="h-4 w-4 mr-1.5" />
              Connect
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>
    </div>
  );
}
