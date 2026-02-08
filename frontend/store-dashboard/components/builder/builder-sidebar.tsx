'use client';

import React from 'react';
import { BuilderTab } from '@/types/themes.types';
import { Bot, Palette, Paintbrush } from 'lucide-react';
import { cn } from '@/lib/utils';

interface BuilderSidebarProps {
  activeTab: BuilderTab;
  onTabChange: (tab: BuilderTab) => void;
}

const tabs: { id: BuilderTab; icon: React.ElementType; label: string }[] = [
  { id: 'ai-agent', icon: Bot, label: 'AI Agent' },
  { id: 'theme-settings', icon: Palette, label: 'Theme Settings' },
  { id: 'class-generator', icon: Paintbrush, label: 'Class Generator' },
];

export function BuilderSidebar({ activeTab, onTabChange }: BuilderSidebarProps) {
  return (
    <div className="w-12 bg-gray-900 flex flex-col items-center py-3 gap-1 shrink-0">
      {tabs.map((tab) => {
        const Icon = tab.icon;
        const isActive = activeTab === tab.id;
        return (
          <button
            key={tab.id}
            onClick={() => onTabChange(tab.id)}
            className={cn(
              'w-10 h-10 flex items-center justify-center rounded-lg transition-colors',
              'hover:bg-gray-700 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2 focus:ring-offset-gray-900',
              isActive ? 'bg-gray-700 text-white' : 'text-gray-400'
            )}
            title={tab.label}
            aria-label={tab.label}
          >
            <Icon className="h-5 w-5" />
          </button>
        );
      })}
    </div>
  );
}
