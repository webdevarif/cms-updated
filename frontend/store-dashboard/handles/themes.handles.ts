'use client';

import { apiClient } from '@/lib/api-client';
import { ROUTES, buildUrlWithParams } from '@/lib/routes';
import {
  Theme,
  Template,
  StyleClass,
  ThemeCreateFormData,
  ThemeUpdateFormData,
  TemplateCreateFormData,
  TemplateUpdateFormData,
  StyleClassCreateFormData,
} from '@/types/themes.types';

// ─── Theme Handlers ───────────────────────────────────────────────────────────

export async function handleCreateTheme(data: ThemeCreateFormData): Promise<Theme> {
  const res = await apiClient.post<Theme>(ROUTES.API.THEMES.CREATE, data);
  return res.data;
}

export async function handleUpdateTheme(id: string | number, data: ThemeUpdateFormData): Promise<Theme> {
  const url = buildUrlWithParams(ROUTES.API.THEMES.UPDATE, { id });
  const res = await apiClient.patch<Theme>(url, data);
  return res.data;
}

export async function handleDeleteTheme(id: string | number): Promise<void> {
  const url = buildUrlWithParams(ROUTES.API.THEMES.DELETE, { id });
  await apiClient.delete(url);
}

// ─── Template Handlers ────────────────────────────────────────────────────────

export async function handleCreateTemplate(data: TemplateCreateFormData): Promise<Template> {
  const res = await apiClient.post<Template>(ROUTES.API.THEMES.TEMPLATES.CREATE, data);
  return res.data;
}

export async function handleUpdateTemplate(id: string | number, data: TemplateUpdateFormData): Promise<Template> {
  const url = buildUrlWithParams(ROUTES.API.THEMES.TEMPLATES.UPDATE, { id });
  const res = await apiClient.patch<Template>(url, data);
  return res.data;
}

export async function handleDeleteTemplate(id: string | number): Promise<void> {
  const url = buildUrlWithParams(ROUTES.API.THEMES.TEMPLATES.DELETE, { id });
  await apiClient.delete(url);
}

export async function handlePublishTemplate(id: string | number): Promise<Template> {
  const url = buildUrlWithParams(ROUTES.API.THEMES.TEMPLATES.UPDATE, { id });
  const res = await apiClient.patch<Template>(url, { is_active: true });
  return res.data;
}

// ─── Style Class Handlers ─────────────────────────────────────────────────────

export async function handleCreateStyleClass(data: StyleClassCreateFormData): Promise<StyleClass> {
  const res = await apiClient.post<StyleClass>(ROUTES.API.THEMES.STYLE_CLASSES.CREATE, data);
  return res.data;
}

export async function handleDeleteStyleClass(id: string | number): Promise<void> {
  const url = buildUrlWithParams(ROUTES.API.THEMES.STYLE_CLASSES.DELETE, { id });
  await apiClient.delete(url);
}

// ─── WebSocket / AI Agent Handlers ────────────────────────────────────────────

// TODO: Replace with actual WebSocket endpoint from Django channels
const WS_BASE_URL = process.env.NEXT_PUBLIC_WS_URL || 'ws://localhost:8000';

/**
 * Create a WebSocket connection for the AI builder agent.
 * The backend should expose a channel at /ws/builder/<theme_id>/
 * that accepts prompt messages and streams back generated HTML.
 */
export function createBuilderWebSocket(
  themeId: string,
  onMessage: (data: { type: string; content: string; status?: string }) => void,
  onError?: (error: Event) => void,
  onClose?: () => void,
): WebSocket | null {
  if (typeof window === 'undefined') return null;

  // TODO: Update path once Django Channels consumer is implemented
  const ws = new WebSocket(`${WS_BASE_URL}/ws/builder/${themeId}/`);

  ws.onmessage = (event) => {
    try {
      const data = JSON.parse(event.data);
      onMessage(data);
    } catch {
      console.error('Failed to parse WebSocket message:', event.data);
    }
  };

  ws.onerror = (error) => {
    console.error('Builder WebSocket error:', error);
    onError?.(error);
  };

  ws.onclose = () => {
    console.log('Builder WebSocket closed');
    onClose?.();
  };

  return ws;
}

/**
 * Send a prompt to the AI builder agent via WebSocket.
 */
export function sendBuilderPrompt(ws: WebSocket, prompt: string, templateId?: string): void {
  if (ws.readyState !== WebSocket.OPEN) {
    console.error('WebSocket is not open');
    return;
  }

  ws.send(JSON.stringify({
    type: 'generate',
    prompt,
    template_id: templateId || null,
  }));
}
