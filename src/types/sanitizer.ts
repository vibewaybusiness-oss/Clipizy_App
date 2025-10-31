/**
 * SANITIZER TYPES
 * TypeScript type definitions for sanitizer functionality
 */

export interface SanitizerConfig {
  maxLength: number;
  allowHtml: boolean;
  allowScripts: boolean;
  allowSqlKeywords: boolean;
  stripWhitespace: boolean;
  normalizeUnicode: boolean;
  removeControlChars: boolean;
  allowedTags: string[];
  allowedAttributes: string[];
  customPatterns: string[];
}

export interface SanitizerResult {
  original: any;
  sanitized: any;
  isValid: boolean;
  warnings: string[];
  errors: string[];
}

export interface SanitizedField {
  value: any;
  sanitized: any;
  isValid: boolean;
  warnings: string[];
  errors: string[];
  isDirty: boolean;
  isTouched: boolean;
}

export interface UseSanitizerOptions {
  config?: Partial<SanitizerConfig>;
  validateOnChange?: boolean;
  validateOnBlur?: boolean;
  showWarnings?: boolean;
  showErrors?: boolean;
}

export interface UseSanitizerReturn {
  sanitize: (value: any, inputType?: string, schema?: Record<string, string>) => SanitizerResult;
  sanitizeField: (name: string, value: any, inputType?: string) => SanitizedField;
  validateField: (name: string, value: any, inputType?: string) => boolean;
  getField: (name: string) => SanitizedField | undefined;
  clearField: (name: string) => void;
  clearAll: () => void;
  fields: Record<string, SanitizedField>;
  hasErrors: boolean;
  hasWarnings: boolean;
  isValid: boolean;
}

export interface UseSanitizedInputReturn {
  value: any;
  setValue: (value: any) => void;
  onBlur: () => void;
  field: SanitizedField | undefined;
  isValid: boolean;
  errors: string[];
  warnings: string[];
  sanitizedValue: any;
}

export interface UseFormSanitizerReturn {
  values: Record<string, any>;
  setValue: (name: string, value: any) => void;
  setValues: (values: Record<string, any>) => void;
  validateAll: () => void;
  reset: () => void;
  getFieldErrors: (name: string) => string[];
  getFieldWarnings: (name: string) => string[];
  isFieldValid: (name: string) => boolean;
  hasErrors: boolean;
  hasWarnings: boolean;
  isValid: boolean;
  fields: Record<string, SanitizedField>;
}

export type InputType = 
  | 'string' 
  | 'number' 
  | 'boolean' 
  | 'array' 
  | 'object' 
  | 'json' 
  | 'file' 
  | 'auto';

export type SanitizerPattern = 
  | 'sqlInjection'
  | 'xss'
  | 'pathTraversal'
  | 'commandInjection'
  | 'ldapInjection'
  | 'noSqlInjection'
  | 'controlChars'
  | 'unicodeAbuse';

export interface SanitizerPatterns {
  [key: string]: RegExp[];
}

export interface FileUploadData {
  filename: string;
  contentType: string;
  size: number;
}

export interface SanitizedFileUpload {
  filename: string;
  contentType: string;
  size: number;
}

export interface ValidationSchema {
  [fieldName: string]: string | ValidationRule;
}

export interface ValidationRule {
  type: InputType;
  required?: boolean;
  minLength?: number;
  maxLength?: number;
  pattern?: RegExp;
  custom?: (value: any) => boolean;
}

export interface SanitizerMiddlewareOptions {
  skipPaths?: string[];
  skipMethods?: string[];
  config?: Partial<SanitizerConfig>;
  logViolations?: boolean;
}

export interface SanitizerError extends Error {
  field?: string;
  inputType?: string;
  violations?: string[];
}

export interface SanitizerStats {
  totalInputs: number;
  sanitizedInputs: number;
  violations: number;
  warnings: number;
  errors: number;
  patterns: Record<string, number>;
}
