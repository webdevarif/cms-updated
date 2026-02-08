'use client';

import React, { useState } from 'react';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Button } from '@/components/ui/button';
import { Textarea } from '@/components/ui/textarea';
import { useStyleClasses, useCreateStyleClass, useUpdateStyleClass, useDeleteStyleClass } from '@/hooks/themes';
import { StyleClass } from '@/types/themes.types';
import { Paintbrush, Plus, Copy, Pencil, Trash2, X, Sun, Moon, Layers } from 'lucide-react';
import { cn } from '@/lib/utils';

interface ClassGeneratorPanelProps {
  themeId: string;
  storeId: string;
}

type CssMode = 'default' | 'light' | 'dark';

function parseCssInput(input: string): Record<string, string> {
  const obj: Record<string, string> = {};
  input.split('\n').forEach((line) => {
    const colonIdx = line.indexOf(':');
    if (colonIdx === -1) return;
    const key = line.substring(0, colonIdx).trim();
    const value = line.substring(colonIdx + 1).trim().replace(/;$/, '');
    if (key && value) obj[key] = value;
  });
  return obj;
}

function formatCss(css: Record<string, string> | null | undefined): string {
  if (!css || Object.keys(css).length === 0) return '';
  return Object.entries(css).map(([k, v]) => `${k}: ${v};`).join('\n');
}

export function ClassGeneratorPanel({ themeId, storeId }: ClassGeneratorPanelProps) {
  const { data: styleClasses, isLoading, mutate } = useStyleClasses(themeId || undefined, storeId);
  const { createStyleClass, isLoading: isCreating } = useCreateStyleClass();
  const { updateStyleClass, isLoading: isUpdating } = useUpdateStyleClass();
  const { deleteStyleClass } = useDeleteStyleClass();

  const [showForm, setShowForm] = useState(false);
  const [editingId, setEditingId] = useState<string | null>(null);
  const [name, setName] = useState('');
  const [slug, setSlug] = useState('');
  const [description, setDescription] = useState('');
  const [defaultCssInput, setDefaultCssInput] = useState('');
  const [lightCssInput, setLightCssInput] = useState('');
  const [darkCssInput, setDarkCssInput] = useState('');
  const [cssMode, setCssMode] = useState<CssMode>('default');

  const resetForm = () => {
    setName('');
    setSlug('');
    setDescription('');
    setDefaultCssInput('');
    setLightCssInput('');
    setDarkCssInput('');
    setCssMode('default');
    setEditingId(null);
    setShowForm(false);
  };

  const startEdit = (sc: StyleClass) => {
    setEditingId(sc.id);
    setName(sc.name);
    setSlug(sc.slug);
    setDescription(sc.description || '');
    setDefaultCssInput(formatCss(sc.default_css));
    setLightCssInput(formatCss(sc.light_css));
    setDarkCssInput(formatCss(sc.dark_css));
    setCssMode('default');
    setShowForm(true);
  };

  const handleSubmit = async () => {
    if (!name || !slug || !themeId) return;

    const payload = {
      theme: themeId,
      name,
      slug,
      description,
      default_css: parseCssInput(defaultCssInput),
      light_css: parseCssInput(lightCssInput),
      dark_css: parseCssInput(darkCssInput),
    };

    try {
      if (editingId) {
        const { theme: _t, ...updatePayload } = payload; // eslint-disable-line @typescript-eslint/no-unused-vars
        await updateStyleClass(editingId, updatePayload, storeId);
      } else {
        await createStyleClass(payload);
      }
      mutate();
      resetForm();
    } catch (err) {
      console.error('Failed to save style class:', err);
    }
  };

  const handleDelete = async (id: string) => {
    try {
      await deleteStyleClass(id, storeId);
      mutate();
    } catch (err) {
      console.error('Failed to delete style class:', err);
    }
  };

  const handleCopyClass = (sc: StyleClass) => {
    const css = formatCss(sc.default_css);
    navigator.clipboard.writeText(`.${sc.slug} {\n${css}\n}`);
  };

  const currentCssInput = cssMode === 'default' ? defaultCssInput : cssMode === 'light' ? lightCssInput : darkCssInput;
  const setCurrentCssInput = cssMode === 'default' ? setDefaultCssInput : cssMode === 'light' ? setLightCssInput : setDarkCssInput;

  if (!themeId) {
    return (
      <div className="p-4 text-center text-sm text-gray-500">
        <Paintbrush className="h-8 w-8 mx-auto text-gray-300 mb-2" />
        No theme selected
      </div>
    );
  }

  return (
    <div className="flex flex-col h-full">
      {/* Header */}
      <div className="p-3 border-b border-gray-200 flex items-center justify-between">
        <div className="flex items-center gap-2">
          <Paintbrush className="h-4 w-4 text-orange-600" />
          <span className="text-sm font-medium">Style Classes</span>
        </div>
        <Button
          size="sm"
          variant="ghost"
          onClick={() => { resetForm(); setShowForm(!showForm); }}
        >
          {showForm ? <X className="h-4 w-4" /> : <Plus className="h-4 w-4" />}
        </Button>
      </div>

      <div className="flex-1 overflow-y-auto">
        {/* Create / Edit form */}
        {showForm && (
          <div className="p-3 border-b border-gray-200 space-y-2 bg-gray-50">
            <p className="text-xs font-medium text-gray-600">
              {editingId ? 'Edit Style Class' : 'New Style Class'}
            </p>
            <div>
              <Label className="text-xs">Name</Label>
              <Input
                value={name}
                onChange={(e) => setName(e.target.value)}
                className="h-8 text-sm mt-1"
                placeholder="e.g. Card Shadow"
              />
            </div>
            <div>
              <Label className="text-xs">Slug</Label>
              <Input
                value={slug}
                onChange={(e) => setSlug(e.target.value)}
                className="h-8 text-sm mt-1"
                placeholder="e.g. card-shadow"
              />
            </div>
            <div>
              <Label className="text-xs">Description</Label>
              <Input
                value={description}
                onChange={(e) => setDescription(e.target.value)}
                className="h-8 text-sm mt-1"
                placeholder="Optional description"
              />
            </div>

            {/* CSS mode tabs: default / light / dark */}
            <div className="flex items-center rounded-md border border-gray-200 overflow-hidden">
              <button
                onClick={() => setCssMode('default')}
                className={cn(
                  'flex-1 flex items-center justify-center gap-1 px-2 py-1 text-xs font-medium transition-colors',
                  cssMode === 'default' ? 'bg-gray-900 text-white' : 'bg-white text-gray-500 hover:bg-gray-50'
                )}
              >
                <Layers className="h-3 w-3" /> Default
              </button>
              <button
                onClick={() => setCssMode('light')}
                className={cn(
                  'flex-1 flex items-center justify-center gap-1 px-2 py-1 text-xs font-medium transition-colors',
                  cssMode === 'light' ? 'bg-gray-900 text-white' : 'bg-white text-gray-500 hover:bg-gray-50'
                )}
              >
                <Sun className="h-3 w-3" /> Light
              </button>
              <button
                onClick={() => setCssMode('dark')}
                className={cn(
                  'flex-1 flex items-center justify-center gap-1 px-2 py-1 text-xs font-medium transition-colors',
                  cssMode === 'dark' ? 'bg-gray-900 text-white' : 'bg-white text-gray-500 hover:bg-gray-50'
                )}
              >
                <Moon className="h-3 w-3" /> Dark
              </button>
            </div>

            <div>
              <Label className="text-xs">CSS Properties (one per line)</Label>
              <Textarea
                value={currentCssInput}
                onChange={(e) => setCurrentCssInput(e.target.value)}
                className="text-sm mt-1 font-mono text-xs"
                rows={4}
                placeholder={`box-shadow: 0 4px 6px rgba(0,0,0,0.1);\nborder-radius: 8px;`}
              />
            </div>
            <div className="flex gap-2">
              <Button
                size="sm"
                className="flex-1"
                onClick={handleSubmit}
                disabled={isCreating || isUpdating || !name || !slug}
              >
                {isCreating || isUpdating ? 'Saving...' : editingId ? 'Update Class' : 'Create Class'}
              </Button>
              <Button
                size="sm"
                variant="outline"
                onClick={resetForm}
              >
                Cancel
              </Button>
            </div>
          </div>
        )}

        {/* Style classes list */}
        {isLoading && (
          <div className="p-4 text-center text-sm text-gray-400">Loading...</div>
        )}

        {styleClasses && styleClasses.length === 0 && !showForm && (
          <div className="p-4 text-center">
            <Paintbrush className="h-6 w-6 mx-auto text-gray-300 mb-2" />
            <p className="text-xs text-gray-500">No style classes yet.</p>
            <Button
              size="sm"
              variant="link"
              onClick={() => setShowForm(true)}
              className="mt-1 text-xs"
            >
              Create your first class
            </Button>
          </div>
        )}

        {styleClasses && styleClasses.length > 0 && (
          <div className="divide-y divide-gray-100">
            {styleClasses.map((sc: StyleClass) => (
              <div key={sc.id} className="p-3 hover:bg-gray-50 group">
                <div className="flex items-start justify-between">
                  <div className="min-w-0">
                    <p className="text-sm font-medium text-gray-900 truncate">{sc.name}</p>
                    <p className="text-xs text-gray-400 font-mono">.{sc.slug}</p>
                    {sc.description && (
                      <p className="text-xs text-gray-400 mt-0.5">{sc.description}</p>
                    )}
                  </div>
                  <div className="flex gap-1 opacity-0 group-hover:opacity-100 transition-opacity">
                    <button
                      onClick={() => handleCopyClass(sc)}
                      className="p-1 text-gray-400 hover:text-gray-600"
                      title="Copy CSS"
                    >
                      <Copy className="h-3 w-3" />
                    </button>
                    <button
                      onClick={() => startEdit(sc)}
                      className="p-1 text-gray-400 hover:text-blue-600"
                      title="Edit"
                    >
                      <Pencil className="h-3 w-3" />
                    </button>
                    <button
                      onClick={() => handleDelete(sc.id)}
                      className="p-1 text-gray-400 hover:text-red-600"
                      title="Delete"
                    >
                      <Trash2 className="h-3 w-3" />
                    </button>
                  </div>
                </div>
                {sc.default_css && Object.keys(sc.default_css).length > 0 && (
                  <div className="mt-1.5 bg-gray-100 rounded px-2 py-1">
                    <pre className="text-xs text-gray-600 font-mono whitespace-pre-wrap">
                      {formatCss(sc.default_css)}
                    </pre>
                  </div>
                )}
                {/* Show light/dark indicators if they have overrides */}
                <div className="flex gap-1 mt-1">
                  {sc.light_css && Object.keys(sc.light_css).length > 0 && (
                    <span className="text-xs bg-yellow-50 text-yellow-600 px-1.5 py-0.5 rounded">light</span>
                  )}
                  {sc.dark_css && Object.keys(sc.dark_css).length > 0 && (
                    <span className="text-xs bg-gray-700 text-gray-200 px-1.5 py-0.5 rounded">dark</span>
                  )}
                </div>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
}
