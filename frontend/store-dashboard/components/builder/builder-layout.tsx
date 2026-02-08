'use client';

import React, { useState } from 'react';
import { BuilderTab, DeviceMode, BuilderView, Template, Theme, Layout } from '@/types/themes.types';
import { BuilderSidebar } from './builder-sidebar';
import { BuilderTopBar } from './builder-top-bar';
import { BuilderCanvas } from './builder-canvas';
import { AiAgentPanel } from './panels/ai-agent-panel';
import { ThemeSettingsPanel } from './panels/theme-settings-panel';
import { ClassGeneratorPanel } from './panels/class-generator-panel';

interface BuilderLayoutProps {
  storeId: string;
  themes: Theme[];
  templates: Template[];
  selectedTheme: Theme | null;
  selectedTemplate: Template | null;
  defaultLayout: Layout | null;
  currentContent: string;
  onContentChange: (content: string) => void;
  onSelectTheme: (themeId: string) => void;
  onSelectTemplate: (templateId: string) => void;
  onSave: () => void;
  onPublish: () => void;
  isSaving: boolean;
  isDirty: boolean;
}

export function BuilderLayout({
  storeId,
  themes,
  templates,
  selectedTheme,
  selectedTemplate,
  defaultLayout,
  currentContent,
  onContentChange,
  onSelectTheme,
  onSelectTemplate,
  onSave,
  onPublish,
  isSaving,
  isDirty,
}: BuilderLayoutProps) {
  const [activeTab, setActiveTab] = useState<BuilderTab>('ai-agent');
  const [deviceMode, setDeviceMode] = useState<DeviceMode>('desktop');
  const [viewMode, setViewMode] = useState<BuilderView>('preview');

  // Find header/footer templates from the layout for preview
  const headerTemplate = defaultLayout?.header_template
    ? templates.find((t) => t.id === defaultLayout.header_template) || null
    : null;
  const footerTemplate = defaultLayout?.footer_template
    ? templates.find((t) => t.id === defaultLayout.footer_template) || null
    : null;

  const panelContent: Record<BuilderTab, React.ReactNode> = {
    'ai-agent': (
      <AiAgentPanel
        storeId={storeId}
        themeId={selectedTheme?.id || ''}
        templateId={selectedTemplate?.id || ''}
        onContentGenerated={(content: string) => {
          onContentChange(content);
        }}
      />
    ),
    'theme-settings': (
      <ThemeSettingsPanel
        theme={selectedTheme}
        themes={themes}
        storeId={storeId}
        onSelectTheme={onSelectTheme}
      />
    ),
    'class-generator': (
      <ClassGeneratorPanel
        themeId={selectedTheme?.id || ''}
        storeId={storeId}
      />
    ),
  };

  return (
    <div className="h-screen flex overflow-hidden bg-gray-100">
      <BuilderSidebar
        activeTab={activeTab}
        onTabChange={setActiveTab}
      />

      <div className="w-80 bg-white border-r border-gray-200 flex flex-col overflow-hidden shrink-0">
        <div className="flex-1 overflow-y-auto">
          {panelContent[activeTab]}
        </div>
      </div>

      <div className="flex-1 flex flex-col overflow-hidden">
        <BuilderTopBar
          deviceMode={deviceMode}
          viewMode={viewMode}
          templates={templates}
          selectedTemplateId={selectedTemplate?.id || ''}
          isTemplateActive={selectedTemplate?.is_active || false}
          onDeviceModeChange={setDeviceMode}
          onViewModeChange={setViewMode}
          onTemplateChange={onSelectTemplate}
          onSave={onSave}
          onPublish={onPublish}
          isSaving={isSaving}
          isDirty={isDirty}
        />

        <BuilderCanvas
          template={selectedTemplate}
          currentContent={currentContent}
          onContentChange={onContentChange}
          headerTemplate={headerTemplate}
          footerTemplate={footerTemplate}
          deviceMode={deviceMode}
          viewMode={viewMode}
          theme={selectedTheme}
        />
      </div>
    </div>
  );
}
