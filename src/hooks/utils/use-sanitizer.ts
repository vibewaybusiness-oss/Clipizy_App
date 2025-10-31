/**
 * SANITIZER HOOK
 * React hook for input sanitization and validation
 */
import { useState, useCallback, useMemo } from 'react';
import { sanitizeInput, SanitizerConfig, SanitizerResult } from '@/lib/sanitizer';

export interface UseSanitizerOptions {
  config?: Partial<SanitizerConfig>;
  validateOnChange?: boolean;
  validateOnBlur?: boolean;
  showWarnings?: boolean;
  showErrors?: boolean;
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

export function useSanitizer(options: UseSanitizerOptions = {}): UseSanitizerReturn {
  const {
    config = {},
    validateOnChange = true,
    validateOnBlur = true,
    showWarnings = true,
    showErrors = true,
  } = options;

  const [fields, setFields] = useState<Record<string, SanitizedField>>({});
  const [touchedFields, setTouchedFields] = useState<Set<string>>(new Set());

  const sanitize = useCallback((
    value: any,
    inputType: string = 'auto',
    schema?: Record<string, string>
  ): SanitizerResult => {
    return sanitizeInput(value, inputType, schema, config);
  }, [config]);

  const sanitizeField = useCallback((
    name: string,
    value: any,
    inputType: string = 'auto'
  ): SanitizedField => {
    const result = sanitize(value, inputType);
    
    const field: SanitizedField = {
      value,
      sanitized: result.sanitized,
      isValid: result.isValid,
      warnings: showWarnings ? result.warnings : [],
      errors: showErrors ? result.errors : [],
      isDirty: true,
      isTouched: touchedFields.has(name),
    };

    setFields(prev => ({
      ...prev,
      [name]: field,
    }));

    return field;
  }, [sanitize, showWarnings, showErrors, touchedFields]);

  const validateField = useCallback((
    name: string,
    value: any,
    inputType: string = 'auto'
  ): boolean => {
    const field = sanitizeField(name, value, inputType);
    return field.isValid;
  }, [sanitizeField]);

  const getField = useCallback((name: string): SanitizedField | undefined => {
    return fields[name];
  }, [fields]);

  const clearField = useCallback((name: string) => {
    setFields(prev => {
      const { [name]: removed, ...rest } = prev;
      return rest;
    });
    setTouchedFields(prev => {
      const newSet = new Set(prev);
      newSet.delete(name);
      return newSet;
    });
  }, []);

  const clearAll = useCallback(() => {
    setFields({});
    setTouchedFields(new Set());
  }, []);

  const hasErrors = useMemo(() => {
    return Object.values(fields).some(field => field.errors.length > 0);
  }, [fields]);

  const hasWarnings = useMemo(() => {
    return Object.values(fields).some(field => field.warnings.length > 0);
  }, [fields]);

  const isValid = useMemo(() => {
    return Object.values(fields).every(field => field.isValid);
  }, [fields]);

  return {
    sanitize,
    sanitizeField,
    validateField,
    getField,
    clearField,
    clearAll,
    fields,
    hasErrors,
    hasWarnings,
    isValid,
  };
}

export function useSanitizedInput(
  name: string,
  initialValue: any = '',
  inputType: string = 'string',
  options: UseSanitizerOptions = {}
) {
  const sanitizer = useSanitizer(options);
  const [value, setValue] = useState(initialValue);

  const handleChange = useCallback((newValue: any) => {
    setValue(newValue);
    if (options.validateOnChange !== false) {
      sanitizer.sanitizeField(name, newValue, inputType);
    }
  }, [name, inputType, sanitizer, options.validateOnChange]);

  const handleBlur = useCallback(() => {
    if (options.validateOnBlur !== false) {
      sanitizer.sanitizeField(name, value, inputType);
    }
  }, [name, value, inputType, sanitizer, options.validateOnBlur]);

  const field = sanitizer.getField(name);

  return {
    value,
    setValue: handleChange,
    onBlur: handleBlur,
    field,
    isValid: field?.isValid ?? true,
    errors: field?.errors ?? [],
    warnings: field?.warnings ?? [],
    sanitizedValue: field?.sanitized ?? value,
  };
}

export function useFormSanitizer(
  initialValues: Record<string, any> = {},
  fieldTypes: Record<string, string> = {},
  options: UseSanitizerOptions = {}
) {
  const sanitizer = useSanitizer(options);
  const [values, setValues] = useState(initialValues);

  const setValue = useCallback((name: string, value: any) => {
    setValues(prev => ({ ...prev, [name]: value }));
    const inputType = fieldTypes[name] || 'string';
    sanitizer.sanitizeField(name, value, inputType);
  }, [sanitizer, fieldTypes]);

  const setValues_batch = useCallback((newValues: Record<string, any>) => {
    setValues(prev => ({ ...prev, ...newValues }));
    Object.entries(newValues).forEach(([name, value]) => {
      const inputType = fieldTypes[name] || 'string';
      sanitizer.sanitizeField(name, value, inputType);
    });
  }, [sanitizer, fieldTypes]);

  const validateAll = useCallback(() => {
    Object.entries(values).forEach(([name, value]) => {
      const inputType = fieldTypes[name] || 'string';
      sanitizer.sanitizeField(name, value, inputType);
    });
  }, [values, fieldTypes, sanitizer]);

  const reset = useCallback(() => {
    setValues(initialValues);
    sanitizer.clearAll();
  }, [initialValues, sanitizer]);

  const getFieldErrors = useCallback((name: string) => {
    const field = sanitizer.getField(name);
    return field?.errors ?? [];
  }, [sanitizer]);

  const getFieldWarnings = useCallback((name: string) => {
    const field = sanitizer.getField(name);
    return field?.warnings ?? [];
  }, [sanitizer]);

  const isFieldValid = useCallback((name: string) => {
    const field = sanitizer.getField(name);
    return field?.isValid ?? true;
  }, [sanitizer]);

  return {
    values,
    setValue,
    setValues: setValues_batch,
    validateAll,
    reset,
    getFieldErrors,
    getFieldWarnings,
    isFieldValid,
    hasErrors: sanitizer.hasErrors,
    hasWarnings: sanitizer.hasWarnings,
    isValid: sanitizer.isValid,
    fields: sanitizer.fields,
  };
}
