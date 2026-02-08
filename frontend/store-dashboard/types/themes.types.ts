// ─── Color Scheme Types ───────────────────────────────────────────────────────

export interface ButtonColors {
  background: string;
  text: string;
  hover_background: string;
  hover_text: string;
  hover_border: string;
  border: string;
}

export interface InputColors {
  background: string;
  text: string;
  border: string;
  hover_background: string;
  hover_border: string;
  focus_border: string;
}

export interface VariantColors {
  background: string;
  text: string;
  border: string;
  hover_background: string;
  hover_text: string;
  hover_border: string;
}

export interface ColorSet {
  background: string;
  headings: string;
  text: string;
  links: string;
  hover_links: string;
  borders: string;
  shadow: string;
  primary_button: ButtonColors;
  secondary_button: ButtonColors;
  inputs: InputColors;
  variants: VariantColors;
}

export interface ColorScheme {
  id: string;
  theme: string;
  key: string;
  name: string;
  is_default: boolean;
  colors: ColorSet;
  dark_colors: ColorSet;
  created_at: string;
  updated_at: string;
}

// ─── Typography Types ─────────────────────────────────────────────────────────

export interface TypographyHeadings {
  font_family: string;
  weights: Record<string, string>;
  sizes: Record<string, string>;
  line_heights: Record<string, string>;
}

export interface TypographyBody {
  font_family: string;
  size: string;
  line_height: string;
  weight: string;
}

export interface TypographyButtons {
  font_family: string;
  weight: string;
  size: string;
  letter_spacing: string;
}

export interface TypographyInputs {
  font_family: string;
  size: string;
  weight: string;
}

export interface Typography {
  headings: TypographyHeadings;
  body: TypographyBody;
  buttons: TypographyButtons;
  inputs: TypographyInputs;
}

// ─── Layout Types ─────────────────────────────────────────────────────────────

export interface Layout {
  id: string;
  theme: string;
  store: string;
  name: string;
  key: string;
  description: string;
  header_template: string | null;
  footer_template: string | null;
  content_slots: Record<string, unknown>;
  is_default: boolean;
  is_system: boolean;
  is_active: boolean;
  created_at: string;
  updated_at: string;
}

// ─── Style Class Types ────────────────────────────────────────────────────────

export interface StyleClass {
  id: string;
  theme: string;
  name: string;
  slug: string;
  description: string;
  default_css: Record<string, string>;
  light_css: Record<string, string>;
  dark_css: Record<string, string>;
  created_at: string;
  updated_at: string;
}

// ─── Template Types ───────────────────────────────────────────────────────────

export type TemplateRole = 'body' | 'header' | 'footer' | 'partial' | 'section';
export type TemplateContentType = 'html' | 'json';

export interface Template {
  id: string;
  theme: string;
  name: string;
  key: string;
  template_role: TemplateRole;
  template_type: string;
  content: string;
  content_type: TemplateContentType;
  is_active: boolean;
  created_at: string;
  updated_at: string;
}

// ─── Theme Types ──────────────────────────────────────────────────────────────

export interface Theme {
  id: string;
  store: string;
  name: string;
  key: string;
  description: string;
  is_default: boolean;
  typography: Typography;
  color_schemes: ColorScheme[];
  layouts: Layout[];
  style_classes: StyleClass[];
  templates: Template[];
  created_at: string;
  updated_at: string;
}

// ─── Form Data Types ──────────────────────────────────────────────────────────

export interface ThemeCreateFormData {
  name: string;
  key: string;
  description?: string;
  is_default?: boolean;
}

export interface ThemeUpdateFormData {
  name?: string;
  key?: string;
  description?: string;
  is_default?: boolean;
  typography?: Typography;
}

export interface ColorSchemeCreateFormData {
  theme: string;
  key: string;
  name: string;
  is_default?: boolean;
  colors?: ColorSet;
  dark_colors?: ColorSet;
}

export interface TemplateCreateFormData {
  theme: string;
  name: string;
  key: string;
  template_role?: TemplateRole;
  template_type?: string;
  content: string;
  content_type?: TemplateContentType;
}

export interface TemplateUpdateFormData {
  name?: string;
  key?: string;
  template_role?: TemplateRole;
  template_type?: string;
  content?: string;
  content_type?: TemplateContentType;
  is_active?: boolean;
}

export interface ColorSchemeUpdateFormData {
  key?: string;
  name?: string;
  is_default?: boolean;
  colors?: ColorSet;
  dark_colors?: ColorSet;
}

export interface StyleClassCreateFormData {
  theme: string;
  name: string;
  slug: string;
  description?: string;
  default_css?: Record<string, string>;
  light_css?: Record<string, string>;
  dark_css?: Record<string, string>;
}

export interface StyleClassUpdateFormData {
  name?: string;
  slug?: string;
  description?: string;
  default_css?: Record<string, string>;
  light_css?: Record<string, string>;
  dark_css?: Record<string, string>;
}

export interface LayoutCreateFormData {
  theme: string;
  name: string;
  key: string;
  description?: string;
  header_template?: string;
  footer_template?: string;
  content_slots?: Record<string, unknown>;
  is_default?: boolean;
}

export interface LayoutUpdateFormData {
  name?: string;
  key?: string;
  description?: string;
  header_template?: string | null;
  footer_template?: string | null;
  content_slots?: Record<string, unknown>;
  is_default?: boolean;
  is_active?: boolean;
}

// ─── Builder Types ────────────────────────────────────────────────────────────

export type DeviceMode = 'mobile' | 'tablet' | 'desktop';
export type BuilderView = 'code' | 'preview';
export type BuilderTab = 'ai-agent' | 'theme-settings' | 'class-generator';

export interface BuilderState {
  activeTab: BuilderTab;
  deviceMode: DeviceMode;
  viewMode: BuilderView;
  selectedThemeId: string | null;
  selectedTemplateId: string | null;
  isDirty: boolean;
}

export interface AiAgentMessage {
  id: string;
  role: 'user' | 'assistant' | 'system';
  content: string;
  timestamp: string;
  status?: 'pending' | 'streaming' | 'complete' | 'error';
}

export interface AiAgentState {
  messages: AiAgentMessage[];
  isConnected: boolean;
  isGenerating: boolean;
}
