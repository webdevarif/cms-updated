'use client';

import React, { useMemo } from 'react';
import dynamic from 'next/dynamic';
import { DeviceMode, BuilderView, Template, Theme } from '@/types/themes.types';
import { cn } from '@/lib/utils';

const MonacoEditor = dynamic(() => import('@monaco-editor/react').then((mod) => mod.default), {
  ssr: false,
  loading: () => (
    <div className="flex-1 flex items-center justify-center bg-gray-900">
      <span className="text-gray-500 text-sm">Loading editor...</span>
    </div>
  ),
});

interface BuilderCanvasProps {
  template: Template | null;
  currentContent: string;
  onContentChange: (content: string) => void;
  headerTemplate: Template | null;
  footerTemplate: Template | null;
  deviceMode: DeviceMode;
  viewMode: BuilderView;
  theme: Theme | null;
}

const DEVICE_WIDTHS: Record<DeviceMode, string> = {
  mobile: '375px',
  tablet: '768px',
  desktop: '100%',
};

export function BuilderCanvas({
  template,
  currentContent,
  onContentChange,
  headerTemplate,
  footerTemplate,
  deviceMode,
  viewMode,
  theme,
}: BuilderCanvasProps) {
  const canvasWidth = DEVICE_WIDTHS[deviceMode];

  // Build theme CSS variables from the default color scheme
  const themeStyles = useMemo(() => {
    if (!theme) return '';
    const defaultScheme = theme.color_schemes?.find((cs) => cs.is_default) || theme.color_schemes?.[0];
    if (!defaultScheme) return '';

    const c = defaultScheme.colors;
    const typo = theme.typography;
    return `
      :root {
        --bg: ${c.background};
        --text: ${c.text};
        --headings: ${c.headings};
        --links: ${c.links};
        --hover-links: ${c.hover_links};
        --borders: ${c.borders};
        --shadow: ${c.shadow};
        --btn-primary-bg: ${c.primary_button?.background || '#3b82f6'};
        --btn-primary-text: ${c.primary_button?.text || '#ffffff'};
        --btn-secondary-bg: ${c.secondary_button?.background || '#e5e7eb'};
        --btn-secondary-text: ${c.secondary_button?.text || '#1f2937'};
      }
      * { margin: 0; padding: 0; box-sizing: border-box; }
      body {
        background: var(--bg);
        color: var(--text);
        font-family: ${typo?.body?.font_family || 'Inter, sans-serif'};
        font-size: ${typo?.body?.size || '1rem'};
        line-height: ${typo?.body?.line_height || '1.5'};
      }
      h1, h2, h3, h4, h5, h6 {
        color: var(--headings);
        font-family: ${typo?.headings?.font_family || 'Inter, sans-serif'};
      }
      a { color: var(--links); }
      a:hover { color: var(--hover-links); }
    `;
  }, [theme]);

  // Build the full preview HTML with header + body + footer
  const previewHtml = useMemo(() => {
    const headerHtml = headerTemplate?.content || '';
    const footerHtml = footerTemplate?.content || '';
    const bodyHtml = currentContent || '<p style="padding:2rem;color:#999;">Empty template</p>';

    return `<!DOCTYPE html>
<html>
  <head>
    <meta charset="utf-8" />
    <meta name="viewport" content="width=device-width, initial-scale=1" />
    <style>${themeStyles}</style>
  </head>
  <body>
    ${headerHtml}
    <main>${bodyHtml}</main>
    ${footerHtml}
  </body>
</html>`;
  }, [headerTemplate, footerTemplate, currentContent, themeStyles]);

  if (!template) {
    return (
      <div className="flex-1 flex items-center justify-center bg-gray-50">
        <div className="text-center">
          <div className="w-16 h-16 mx-auto mb-4 rounded-full bg-gray-200 flex items-center justify-center">
            <svg className="w-8 h-8 text-gray-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
            </svg>
          </div>
          <h3 className="text-sm font-medium text-gray-900">No template selected</h3>
          <p className="text-sm text-gray-500 mt-1">Select a template from the top bar to start editing.</p>
        </div>
      </div>
    );
  }

  // Code mode: Monaco editor for template body content only
  if (viewMode === 'code') {
    const editorLanguage = template.content_type === 'json' ? 'json' : 'html';

    return (
      <div className="flex-1 overflow-hidden">
        <MonacoEditor
          height="100%"
          language={editorLanguage}
          theme="vs-dark"
          value={currentContent}
          onChange={(value) => onContentChange(value || '')}
          options={{
            minimap: { enabled: false },
            fontSize: 14,
            lineNumbers: 'on',
            wordWrap: 'on',
            scrollBeyondLastLine: false,
            automaticLayout: true,
            tabSize: 2,
            formatOnPaste: true,
          }}
        />
      </div>
    );
  }

  // Preview mode: full page iframe with header + body + footer and device sizing
  return (
    <div className="flex-1 overflow-auto bg-gray-100 p-4 flex justify-center">
      <div
        className={cn(
          'bg-white shadow-lg transition-all duration-300 overflow-hidden',
          deviceMode !== 'desktop' && 'rounded-lg border border-gray-300'
        )}
        style={{
          width: canvasWidth,
          maxWidth: '100%',
          height: deviceMode === 'desktop' ? '100%' : undefined,
          minHeight: '600px',
        }}
      >
        <iframe
          title="Template Preview"
          className="w-full h-full min-h-[600px] border-0"
          srcDoc={previewHtml}
          sandbox="allow-same-origin"
        />
      </div>
    </div>
  );
}
