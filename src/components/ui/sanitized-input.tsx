/**
 * SANITIZED INPUT COMPONENT
 * React component with built-in sanitization
 */
import React, { forwardRef, useCallback, useState } from 'react';
import { cn } from '@/lib/utils';
import { useSanitizedInput } from '@/hooks/utils/use-sanitizer';
import { AlertCircle, AlertTriangle, CheckCircle } from 'lucide-react';

export interface SanitizedInputProps extends Omit<React.InputHTMLAttributes<HTMLInputElement>, 'onChange' | 'value'> {
  name: string;
  value: any;
  onChange: (value: any, sanitizedValue: any, isValid: boolean) => void;
  inputType?: 'string' | 'number' | 'boolean' | 'array' | 'object' | 'json' | 'file' | 'auto';
  showValidation?: boolean;
  showWarnings?: boolean;
  showErrors?: boolean;
  className?: string;
  errorClassName?: string;
  warningClassName?: string;
  successClassName?: string;
}

export const SanitizedInput = forwardRef<HTMLInputElement, SanitizedInputProps>(
  ({
    name,
    value,
    onChange,
    inputType = 'string',
    showValidation = true,
    showWarnings = true,
    showErrors = true,
    className,
    errorClassName,
    warningClassName,
    successClassName,
    ...props
  }, ref) => {
    const {
      value: sanitizedValue,
      setValue,
      onBlur,
      field,
      isValid,
      errors,
      warnings,
    } = useSanitizedInput(name, value, inputType, {
      showWarnings,
      showErrors,
    });

    const [isFocused, setIsFocused] = useState(false);

    const handleChange = useCallback((e: React.ChangeEvent<HTMLInputElement>) => {
      const newValue = e.target.value;
      setValue(newValue);
      onChange(newValue, sanitizedValue, isValid);
    }, [setValue, sanitizedValue, isValid, onChange]);

    const handleFocus = useCallback(() => {
      setIsFocused(true);
    }, []);

    const handleBlur = useCallback(() => {
      setIsFocused(false);
      onBlur();
    }, [onBlur]);

    const hasErrors = errors.length > 0;
    const hasWarnings = warnings.length > 0;
    const showSuccess = isValid && !hasErrors && !hasWarnings && isFocused;

    const inputClasses = cn(
      'flex h-10 w-full rounded-md border border-input bg-background px-3 py-2 text-sm ring-offset-background file:border-0 file:bg-transparent file:text-sm file:font-medium placeholder:text-muted-foreground focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2 disabled:cursor-not-allowed disabled:opacity-50',
      {
        'border-destructive focus-visible:ring-destructive': hasErrors,
        'border-yellow-500 focus-visible:ring-yellow-500': hasWarnings && !hasErrors,
        'border-green-500 focus-visible:ring-green-500': showSuccess,
      },
      className
    );

    const validationIcon = () => {
      if (hasErrors) {
        return <AlertCircle className="h-4 w-4 text-destructive" />;
      }
      if (hasWarnings) {
        return <AlertTriangle className="h-4 w-4 text-yellow-500" />;
      }
      if (showSuccess) {
        return <CheckCircle className="h-4 w-4 text-green-500" />;
      }
      return null;
    };

    return (
      <div className="space-y-2">
        <div className="relative">
          <input
            ref={ref}
            name={name}
            value={value}
            onChange={handleChange}
            onFocus={handleFocus}
            onBlur={handleBlur}
            className={inputClasses}
            {...props}
          />
          {showValidation && (
            <div className="absolute right-3 top-1/2 -translate-y-1/2">
              {validationIcon()}
            </div>
          )}
        </div>
        
        {showValidation && (hasErrors || hasWarnings) && (
          <div className="space-y-1">
            {hasErrors && (
              <div className={cn('text-sm text-destructive', errorClassName)}>
                {errors.map((error, index) => (
                  <div key={index} className="flex items-center gap-2">
                    <AlertCircle className="h-3 w-3" />
                    {error}
                  </div>
                ))}
              </div>
            )}
            {hasWarnings && !hasErrors && (
              <div className={cn('text-sm text-yellow-600', warningClassName)}>
                {warnings.map((warning, index) => (
                  <div key={index} className="flex items-center gap-2">
                    <AlertTriangle className="h-3 w-3" />
                    {warning}
                  </div>
                ))}
              </div>
            )}
          </div>
        )}
      </div>
    );
  }
);

SanitizedInput.displayName = 'SanitizedInput';

export interface SanitizedTextareaProps extends Omit<React.TextareaHTMLAttributes<HTMLTextAreaElement>, 'onChange' | 'value'> {
  name: string;
  value: any;
  onChange: (value: any, sanitizedValue: any, isValid: boolean) => void;
  inputType?: 'string' | 'number' | 'boolean' | 'array' | 'object' | 'json' | 'file' | 'auto';
  showValidation?: boolean;
  showWarnings?: boolean;
  showErrors?: boolean;
  className?: string;
  errorClassName?: string;
  warningClassName?: string;
  successClassName?: string;
}

export const SanitizedTextarea = forwardRef<HTMLTextAreaElement, SanitizedTextareaProps>(
  ({
    name,
    value,
    onChange,
    inputType = 'string',
    showValidation = true,
    showWarnings = true,
    showErrors = true,
    className,
    errorClassName,
    warningClassName,
    successClassName,
    ...props
  }, ref) => {
    const {
      value: sanitizedValue,
      setValue,
      onBlur,
      field,
      isValid,
      errors,
      warnings,
    } = useSanitizedInput(name, value, inputType, {
      showWarnings,
      showErrors,
    });

    const [isFocused, setIsFocused] = useState(false);

    const handleChange = useCallback((e: React.ChangeEvent<HTMLTextAreaElement>) => {
      const newValue = e.target.value;
      setValue(newValue);
      onChange(newValue, sanitizedValue, isValid);
    }, [setValue, sanitizedValue, isValid, onChange]);

    const handleFocus = useCallback(() => {
      setIsFocused(true);
    }, []);

    const handleBlur = useCallback(() => {
      setIsFocused(false);
      onBlur();
    }, [onBlur]);

    const hasErrors = errors.length > 0;
    const hasWarnings = warnings.length > 0;
    const showSuccess = isValid && !hasErrors && !hasWarnings && isFocused;

    const textareaClasses = cn(
      'flex min-h-[80px] w-full rounded-md border border-input bg-background px-3 py-2 text-sm ring-offset-background placeholder:text-muted-foreground focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2 disabled:cursor-not-allowed disabled:opacity-50',
      {
        'border-destructive focus-visible:ring-destructive': hasErrors,
        'border-yellow-500 focus-visible:ring-yellow-500': hasWarnings && !hasErrors,
        'border-green-500 focus-visible:ring-green-500': showSuccess,
      },
      className
    );

    const validationIcon = () => {
      if (hasErrors) {
        return <AlertCircle className="h-4 w-4 text-destructive" />;
      }
      if (hasWarnings) {
        return <AlertTriangle className="h-4 w-4 text-yellow-500" />;
      }
      if (showSuccess) {
        return <CheckCircle className="h-4 w-4 text-green-500" />;
      }
      return null;
    };

    return (
      <div className="space-y-2">
        <div className="relative">
          <textarea
            ref={ref}
            name={name}
            value={value}
            onChange={handleChange}
            onFocus={handleFocus}
            onBlur={handleBlur}
            className={textareaClasses}
            {...props}
          />
          {showValidation && (
            <div className="absolute right-3 top-3">
              {validationIcon()}
            </div>
          )}
        </div>
        
        {showValidation && (hasErrors || hasWarnings) && (
          <div className="space-y-1">
            {hasErrors && (
              <div className={cn('text-sm text-destructive', errorClassName)}>
                {errors.map((error, index) => (
                  <div key={index} className="flex items-center gap-2">
                    <AlertCircle className="h-3 w-3" />
                    {error}
                  </div>
                ))}
              </div>
            )}
            {hasWarnings && !hasErrors && (
              <div className={cn('text-sm text-yellow-600', warningClassName)}>
                {warnings.map((warning, index) => (
                  <div key={index} className="flex items-center gap-2">
                    <AlertTriangle className="h-3 w-3" />
                    {warning}
                  </div>
                ))}
              </div>
            )}
          </div>
        )}
      </div>
    );
  }
);

SanitizedTextarea.displayName = 'SanitizedTextarea';
