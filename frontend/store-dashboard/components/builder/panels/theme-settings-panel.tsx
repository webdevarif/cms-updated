'use client';

import React, { useState } from 'react';
import { Theme, ColorSet, ColorScheme, Typography, ColorSchemeUpdateFormData } from '@/types/themes.types';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Button } from '@/components/ui/button';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { useUpdateTheme, useUpdateColorScheme } from '@/hooks/themes';
import { Palette, Type, ChevronDown, ChevronRight, Sun, Moon, Check } from 'lucide-react';
import { cn } from '@/lib/utils';

interface ThemeSettingsPanelProps {
  theme: Theme | null;
  themes: Theme[];
  storeId: string;
  onSelectTheme: (themeId: string) => void;
}

interface ColorFieldProps {
  label: string;
  value: string;
  onChange: (value: string) => void;
}

function ColorField({ label, value, onChange }: ColorFieldProps) {
  return (
    <div className="flex items-center gap-2">
      <input
        type="color"
        value={value || '#000000'}
        onChange={(e) => onChange(e.target.value)}
        className="w-7 h-7 rounded border border-gray-300 cursor-pointer p-0"
      />
      <div className="flex-1 min-w-0">
        <span className="text-xs text-gray-600 truncate block">{label}</span>
        <span className="text-xs text-gray-400 font-mono">{value || '#000000'}</span>
      </div>
    </div>
  );
}

function ColorGroup({ title, colors, onChange }: {
  title: string;
  colors: Record<string, string>;
  onChange: (key: string, value: string) => void;
}) {
  const [open, setOpen] = useState(false);
  return (
    <div className="border border-gray-100 rounded-md">
      <button
        onClick={() => setOpen(!open)}
        className="w-full flex items-center justify-between px-2 py-1.5 text-xs font-medium text-gray-600 hover:bg-gray-50"
      >
        {title}
        {open ? <ChevronDown className="h-3 w-3" /> : <ChevronRight className="h-3 w-3" />}
      </button>
      {open && (
        <div className="px-2 pb-2 space-y-2">
          {Object.entries(colors).map(([key, val]) => (
            <ColorField
              key={key}
              label={key.replace(/_/g, ' ')}
              value={val}
              onChange={(v) => onChange(key, v)}
            />
          ))}
        </div>
      )}
    </div>
  );
}

export function ThemeSettingsPanel({ theme, themes, storeId, onSelectTheme }: ThemeSettingsPanelProps) {
  const { updateTheme, isLoading: isSavingTheme } = useUpdateTheme();
  const { updateColorScheme, isLoading: isSavingColors } = useUpdateColorScheme();

  if (!theme) {
    return (
      <div className="p-4 text-center text-sm text-gray-500">
        <Palette className="h-8 w-8 mx-auto text-gray-300 mb-2" />
        No theme selected
      </div>
    );
  }

  // Find the active color scheme
  const activeScheme = theme.color_schemes?.find((cs) => cs.is_default) || theme.color_schemes?.[0];

  // Use a key to reset local state when theme/scheme changes
  const schemeKey = activeScheme?.id || '';
  const themeKey = theme.id;

  return (
    <ThemeSettingsPanelInner
      key={`${themeKey}-${schemeKey}`}
      theme={theme}
      themes={themes}
      activeScheme={activeScheme || null}
      storeId={storeId}
      onSelectTheme={onSelectTheme}
      updateTheme={updateTheme}
      isSavingTheme={isSavingTheme}
      updateColorScheme={updateColorScheme}
      isSavingColors={isSavingColors}
    />
  );
}

interface InnerProps {
  theme: Theme;
  themes: Theme[];
  activeScheme: ColorScheme | null;
  storeId: string;
  onSelectTheme: (themeId: string) => void;
  updateTheme: (id: string | number, data: { typography?: Typography }, storeId: string) => Promise<Theme>;
  isSavingTheme: boolean;
  updateColorScheme: (id: string | number, data: ColorSchemeUpdateFormData, storeId: string) => Promise<ColorScheme>;
  isSavingColors: boolean;
}

function ThemeSettingsPanelInner({
  theme,
  themes,
  activeScheme,
  storeId,
  onSelectTheme,
  updateTheme,
  isSavingTheme,
  updateColorScheme,
  isSavingColors,
}: InnerProps) {
  const [colorsOpen, setColorsOpen] = useState(true);
  const [typographyOpen, setTypographyOpen] = useState(false);
  const [colorMode, setColorMode] = useState<'light' | 'dark'>('light');
  const [saveStatus, setSaveStatus] = useState<string | null>(null);

  // Local color state initialized from active scheme (resets via key remount)
  const [lightColors, setLightColors] = useState<ColorSet | null>(
    activeScheme?.colors ? { ...activeScheme.colors } : null
  );
  const [darkColors, setDarkColors] = useState<ColorSet | null>(
    activeScheme?.dark_colors ? { ...activeScheme.dark_colors } : null
  );

  // Typography state initialized from theme (resets via key remount)
  const [typography, setTypography] = useState(theme?.typography || null);

  const currentColors = colorMode === 'light' ? lightColors : darkColors;

  const updateCurrentColor = (key: string, value: string) => {
    if (colorMode === 'light') {
      setLightColors((prev) => prev ? { ...prev, [key]: value } : prev);
    } else {
      setDarkColors((prev) => prev ? { ...prev, [key]: value } : prev);
    }
  };

  const updateNestedColor = (group: string, key: string, value: string) => {
    const setter = colorMode === 'light' ? setLightColors : setDarkColors;
    setter((prev) => {
      if (!prev) return prev;
      const groupObj = (prev as unknown as Record<string, unknown>)[group];
      if (typeof groupObj === 'object' && groupObj !== null) {
        return { ...prev, [group]: { ...(groupObj as Record<string, string>), [key]: value } };
      }
      return prev;
    });
  };

  const handleSaveColors = async () => {
    if (!activeScheme || !lightColors || !darkColors) return;
    try {
      await updateColorScheme(activeScheme.id, {
        colors: lightColors,
        dark_colors: darkColors,
      }, storeId);
      setSaveStatus('Colors saved');
      setTimeout(() => setSaveStatus(null), 2000);
    } catch (err) {
      console.error('Failed to save colors:', err);
    }
  };

  const handleSaveTypography = async () => {
    if (!theme || !typography) return;
    try {
      await updateTheme(theme.id, { typography }, storeId);
      setSaveStatus('Typography saved');
      setTimeout(() => setSaveStatus(null), 2000);
    } catch (err) {
      console.error('Failed to save typography:', err);
    }
  };

  const updateTypoField = (section: string, key: string, value: string) => {
    setTypography((prev) => {
      if (!prev) return prev;
      const sectionObj = prev[section as keyof typeof prev];
      if (typeof sectionObj === 'object' && sectionObj !== null) {
        return { ...prev, [section]: { ...sectionObj, [key]: value } };
      }
      return prev;
    });
  };

  return (
    <div className="flex flex-col h-full">
      {/* Header */}
      <div className="p-3 border-b border-gray-200">
        <div className="flex items-center gap-2 mb-2">
          <Palette className="h-4 w-4 text-purple-600" />
          <span className="text-sm font-medium">Theme Settings</span>
        </div>
        {/* Theme selector */}
        {themes.length > 1 && (
          <Select value={theme.id} onValueChange={onSelectTheme}>
            <SelectTrigger className="h-8 text-xs">
              <SelectValue />
            </SelectTrigger>
            <SelectContent>
              {themes.map((t) => (
                <SelectItem key={t.id} value={t.id}>
                  {t.name} {t.is_default && '(default)'}
                </SelectItem>
              ))}
            </SelectContent>
          </Select>
        )}
      </div>

      {/* Save status toast */}
      {saveStatus && (
        <div className="mx-3 mt-2 flex items-center gap-1.5 text-xs text-green-700 bg-green-50 border border-green-200 rounded-md px-2 py-1.5">
          <Check className="h-3 w-3" />
          {saveStatus}
        </div>
      )}

      <div className="flex-1 overflow-y-auto">
        {/* Colors Section */}
        <div className="border-b border-gray-100">
          <button
            onClick={() => setColorsOpen(!colorsOpen)}
            className="w-full flex items-center justify-between p-3 text-sm font-medium text-gray-700 hover:bg-gray-50"
          >
            <span className="flex items-center gap-2">
              <Palette className="h-4 w-4" />
              Colors
            </span>
            {colorsOpen ? <ChevronDown className="h-4 w-4" /> : <ChevronRight className="h-4 w-4" />}
          </button>

          {colorsOpen && (
            <div className="px-3 pb-3 space-y-3">
              {activeScheme && currentColors ? (
                <>
                  {/* Light / Dark toggle */}
                  <div className="flex items-center rounded-md border border-gray-200 overflow-hidden">
                    <button
                      onClick={() => setColorMode('light')}
                      className={cn(
                        'flex-1 flex items-center justify-center gap-1 px-2 py-1.5 text-xs font-medium transition-colors',
                        colorMode === 'light' ? 'bg-gray-900 text-white' : 'bg-white text-gray-500 hover:bg-gray-50'
                      )}
                    >
                      <Sun className="h-3 w-3" /> Light
                    </button>
                    <button
                      onClick={() => setColorMode('dark')}
                      className={cn(
                        'flex-1 flex items-center justify-center gap-1 px-2 py-1.5 text-xs font-medium transition-colors',
                        colorMode === 'dark' ? 'bg-gray-900 text-white' : 'bg-white text-gray-500 hover:bg-gray-50'
                      )}
                    >
                      <Moon className="h-3 w-3" /> Dark
                    </button>
                  </div>

                  {/* Base colors */}
                  <ColorField label="Background" value={currentColors.background} onChange={(v) => updateCurrentColor('background', v)} />
                  <ColorField label="Headings" value={currentColors.headings} onChange={(v) => updateCurrentColor('headings', v)} />
                  <ColorField label="Text" value={currentColors.text} onChange={(v) => updateCurrentColor('text', v)} />
                  <ColorField label="Links" value={currentColors.links} onChange={(v) => updateCurrentColor('links', v)} />
                  <ColorField label="Hover Links" value={currentColors.hover_links} onChange={(v) => updateCurrentColor('hover_links', v)} />
                  <ColorField label="Borders" value={currentColors.borders} onChange={(v) => updateCurrentColor('borders', v)} />
                  <ColorField label="Shadow" value={currentColors.shadow} onChange={(v) => updateCurrentColor('shadow', v)} />

                  {/* Grouped: buttons, inputs, variants */}
                  <ColorGroup
                    title="Primary Button"
                    colors={currentColors.primary_button as unknown as Record<string, string>}
                    onChange={(k, v) => updateNestedColor('primary_button', k, v)}
                  />
                  <ColorGroup
                    title="Secondary Button"
                    colors={currentColors.secondary_button as unknown as Record<string, string>}
                    onChange={(k, v) => updateNestedColor('secondary_button', k, v)}
                  />
                  <ColorGroup
                    title="Inputs"
                    colors={currentColors.inputs as unknown as Record<string, string>}
                    onChange={(k, v) => updateNestedColor('inputs', k, v)}
                  />
                  <ColorGroup
                    title="Variants"
                    colors={currentColors.variants as unknown as Record<string, string>}
                    onChange={(k, v) => updateNestedColor('variants', k, v)}
                  />

                  <Button
                    size="sm"
                    className="w-full mt-2"
                    onClick={handleSaveColors}
                    disabled={isSavingColors}
                  >
                    {isSavingColors ? 'Saving...' : 'Save Colors'}
                  </Button>
                </>
              ) : (
                <p className="text-xs text-gray-400">No color scheme found for this theme.</p>
              )}
            </div>
          )}
        </div>

        {/* Typography Section */}
        <div className="border-b border-gray-100">
          <button
            onClick={() => setTypographyOpen(!typographyOpen)}
            className="w-full flex items-center justify-between p-3 text-sm font-medium text-gray-700 hover:bg-gray-50"
          >
            <span className="flex items-center gap-2">
              <Type className="h-4 w-4" />
              Typography
            </span>
            {typographyOpen ? <ChevronDown className="h-4 w-4" /> : <ChevronRight className="h-4 w-4" />}
          </button>

          {typographyOpen && typography && (
            <div className="px-3 pb-3 space-y-4">
              {/* Headings */}
              <div className="space-y-2">
                <p className="text-xs font-medium text-gray-500 uppercase">Headings</p>
                <div>
                  <Label className="text-xs">Font Family</Label>
                  <Input value={typography.headings?.font_family || ''} onChange={(e) => updateTypoField('headings', 'font_family', e.target.value)} className="h-8 text-sm mt-1" placeholder="Inter, sans-serif" />
                </div>
              </div>

              {/* Body */}
              <div className="space-y-2">
                <p className="text-xs font-medium text-gray-500 uppercase">Body</p>
                <div>
                  <Label className="text-xs">Font Family</Label>
                  <Input value={typography.body?.font_family || ''} onChange={(e) => updateTypoField('body', 'font_family', e.target.value)} className="h-8 text-sm mt-1" placeholder="Inter, sans-serif" />
                </div>
                <div className="grid grid-cols-2 gap-2">
                  <div>
                    <Label className="text-xs">Size</Label>
                    <Input value={typography.body?.size || ''} onChange={(e) => updateTypoField('body', 'size', e.target.value)} className="h-8 text-sm mt-1" placeholder="1rem" />
                  </div>
                  <div>
                    <Label className="text-xs">Weight</Label>
                    <Input value={typography.body?.weight || ''} onChange={(e) => updateTypoField('body', 'weight', e.target.value)} className="h-8 text-sm mt-1" placeholder="400" />
                  </div>
                </div>
                <div>
                  <Label className="text-xs">Line Height</Label>
                  <Input value={typography.body?.line_height || ''} onChange={(e) => updateTypoField('body', 'line_height', e.target.value)} className="h-8 text-sm mt-1" placeholder="1.5" />
                </div>
              </div>

              {/* Buttons */}
              <div className="space-y-2">
                <p className="text-xs font-medium text-gray-500 uppercase">Buttons</p>
                <div>
                  <Label className="text-xs">Font Family</Label>
                  <Input value={typography.buttons?.font_family || ''} onChange={(e) => updateTypoField('buttons', 'font_family', e.target.value)} className="h-8 text-sm mt-1" placeholder="Inter, sans-serif" />
                </div>
                <div className="grid grid-cols-2 gap-2">
                  <div>
                    <Label className="text-xs">Size</Label>
                    <Input value={typography.buttons?.size || ''} onChange={(e) => updateTypoField('buttons', 'size', e.target.value)} className="h-8 text-sm mt-1" placeholder="0.875rem" />
                  </div>
                  <div>
                    <Label className="text-xs">Weight</Label>
                    <Input value={typography.buttons?.weight || ''} onChange={(e) => updateTypoField('buttons', 'weight', e.target.value)} className="h-8 text-sm mt-1" placeholder="500" />
                  </div>
                </div>
                <div>
                  <Label className="text-xs">Letter Spacing</Label>
                  <Input value={typography.buttons?.letter_spacing || ''} onChange={(e) => updateTypoField('buttons', 'letter_spacing', e.target.value)} className="h-8 text-sm mt-1" placeholder="0.025em" />
                </div>
              </div>

              {/* Inputs */}
              <div className="space-y-2">
                <p className="text-xs font-medium text-gray-500 uppercase">Inputs</p>
                <div>
                  <Label className="text-xs">Font Family</Label>
                  <Input value={typography.inputs?.font_family || ''} onChange={(e) => updateTypoField('inputs', 'font_family', e.target.value)} className="h-8 text-sm mt-1" placeholder="Inter, sans-serif" />
                </div>
                <div className="grid grid-cols-2 gap-2">
                  <div>
                    <Label className="text-xs">Size</Label>
                    <Input value={typography.inputs?.size || ''} onChange={(e) => updateTypoField('inputs', 'size', e.target.value)} className="h-8 text-sm mt-1" placeholder="0.875rem" />
                  </div>
                  <div>
                    <Label className="text-xs">Weight</Label>
                    <Input value={typography.inputs?.weight || ''} onChange={(e) => updateTypoField('inputs', 'weight', e.target.value)} className="h-8 text-sm mt-1" placeholder="400" />
                  </div>
                </div>
              </div>

              <Button
                size="sm"
                className="w-full"
                onClick={handleSaveTypography}
                disabled={isSavingTheme}
              >
                {isSavingTheme ? 'Saving...' : 'Save Typography'}
              </Button>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
