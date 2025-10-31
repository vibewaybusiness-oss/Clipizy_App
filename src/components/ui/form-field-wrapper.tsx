"use client";

import React from 'react';
import { FormField, FormItem, FormControl, FormLabel, FormMessage } from '@/components/ui/form';
import { UseFormReturn } from 'react-hook-form';
import { cn } from '@/lib/utils';

interface FormFieldWrapperProps {
  form: UseFormReturn<any>;
  name: string;
  label?: string;
  children: React.ReactNode;
  className?: string;
  required?: boolean;
}

export function FormFieldWrapper({
  form,
  name,
  label,
  children,
  className,
  required = false
}: FormFieldWrapperProps) {
  return (
    <FormField
      control={form.control}
      name={name}
      render={({ field }) => (
        <FormItem className={cn('space-y-2', className)}>
          {label && (
            <FormLabel className="text-xs font-medium text-foreground">
              {label}
              {required && <span className="text-destructive ml-1">*</span>}
            </FormLabel>
          )}
          <FormControl>
            {React.cloneElement(children as React.ReactElement, {
              ...field,
              ...((children as React.ReactElement).props || {})
            })}
          </FormControl>
          <FormMessage />
        </FormItem>
      )}
    />
  );
}
