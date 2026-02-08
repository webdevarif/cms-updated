'use client';

import React from 'react';
import { DeviceMode, BuilderView, Template } from '@/types/themes.types';
import { Button } from '@/components/ui/button';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { Smartphone, Tablet, Monitor, Save, Upload, Code, Eye } from 'lucide-react';
import { cn } from '@/lib/utils';

interface BuilderTopBarProps {
  deviceMode: DeviceMode;
  viewMode: BuilderView;
  templates: Template[];
  selectedTemplateId: string;
  isTemplateActive: boolean;
  onDeviceModeChange: (mode: DeviceMode) => void;
  onViewModeChange: (mode: BuilderView) => void;
  onTemplateChange: (templateId: string) => void;
  onSave: () => void;
  onPublish: () => void;
  isSaving: boolean;
  isDirty: boolean;
}

const ROLE_LABELS: Record<string, string> = {
  body: 'Body',
  header: 'Header',
  footer: 'Footer',
  partial: 'Partial',
  section: 'Section',
};

const deviceModes: { id: DeviceMode; icon: React.ElementType; label: string; width: string }[] = [
  { id: 'mobile', icon: Smartphone, label: 'Mobile', width: '375px' },
  { id: 'tablet', icon: Tablet, label: 'Tablet', width: '768px' },
  { id: 'desktop', icon: Monitor, label: 'Desktop', width: '100%' },
];

export function BuilderTopBar({
  deviceMode,
  viewMode,
  templates,
  selectedTemplateId,
  isTemplateActive,
  onDeviceModeChange,
  onViewModeChange,
  onTemplateChange,
  onSave,
  onPublish,
  isSaving,
  isDirty,
}: BuilderTopBarProps) {
  return (
    <div className="h-14 bg-white border-b border-gray-200 flex items-center justify-between px-4 shrink-0">
      {/* Left: Device mode icons — only visible in Preview mode */}
      <div className="flex items-center gap-1 min-w-[120px]">
        {viewMode === 'preview' && deviceModes.map((device) => {
          const Icon = device.icon;
          const isActive = deviceMode === device.id;
          return (
            <button
              key={device.id}
              onClick={() => onDeviceModeChange(device.id)}
              className={cn(
                'p-2 rounded-md transition-colors',
                isActive
                  ? 'bg-blue-100 text-blue-700'
                  : 'text-gray-500 hover:bg-gray-100 hover:text-gray-700'
              )}
              title={`${device.label} (${device.width})`}
              aria-label={device.label}
            >
              <Icon className="h-4 w-4" />
            </button>
          );
        })}
      </div>

      {/* Center: Template selector with role labels */}
      <div className="flex-1 max-w-xs mx-4">
        <Select value={selectedTemplateId} onValueChange={onTemplateChange}>
          <SelectTrigger className="h-9">
            <SelectValue placeholder="Select template..." />
          </SelectTrigger>
          <SelectContent>
            {templates.length === 0 ? (
              <SelectItem value="none" disabled>No templates available</SelectItem>
            ) : (
              templates.map((tpl) => (
                <SelectItem key={tpl.id} value={tpl.id}>
                  <span className="flex items-center gap-2">
                    <span className="text-xs font-medium text-gray-400 uppercase w-14">
                      {ROLE_LABELS[tpl.template_role] || tpl.template_role}
                    </span>
                    <span>{tpl.name}</span>
                    {tpl.is_active && (
                      <span className="ml-1 w-1.5 h-1.5 rounded-full bg-green-500 inline-block" />
                    )}
                  </span>
                </SelectItem>
              ))
            )}
          </SelectContent>
        </Select>
      </div>

      {/* Right: Grouped actions */}
      <div className="flex items-center gap-3">
        {/* Code / Preview toggle group */}
        <div className="flex items-center rounded-md border border-gray-200 overflow-hidden">
          <button
            onClick={() => onViewModeChange('code')}
            className={cn(
              'px-3 py-1.5 text-sm font-medium transition-colors flex items-center gap-1.5',
              viewMode === 'code'
                ? 'bg-gray-900 text-white'
                : 'bg-white text-gray-600 hover:bg-gray-50'
            )}
          >
            <Code className="h-3.5 w-3.5" />
            Code
          </button>
          <button
            onClick={() => onViewModeChange('preview')}
            className={cn(
              'px-3 py-1.5 text-sm font-medium transition-colors flex items-center gap-1.5',
              viewMode === 'preview'
                ? 'bg-gray-900 text-white'
                : 'bg-white text-gray-600 hover:bg-gray-50'
            )}
          >
            <Eye className="h-3.5 w-3.5" />
            Preview
          </button>
        </div>

        {/* Save / Publish group */}
        <div className="flex items-center gap-1.5">
          <Button
            variant="outline"
            size="sm"
            onClick={onSave}
            disabled={isSaving || !isDirty}
          >
            <Save className="h-4 w-4 mr-1" />
            Save
          </Button>

          <Button
            size="sm"
            onClick={onPublish}
            disabled={isSaving || isTemplateActive}
            title={isTemplateActive ? 'Template is already published' : 'Publish template'}
          >
            <Upload className="h-4 w-4 mr-1" />
            {isTemplateActive ? 'Published' : 'Publish'}
          </Button>
        </div>
      </div>
    </div>
  );
}
