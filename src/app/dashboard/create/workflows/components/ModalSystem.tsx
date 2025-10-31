"use client";

import React, { createContext, useContext, useState, useCallback } from 'react';
import { Dialog, DialogContent, DialogHeader, DialogTitle } from '@/components/ui/dialog';
import { Button } from '@/components/ui/button';
import { X } from 'lucide-react';

interface ModalContextType {
  openModal: (modalId: string, props: any) => void;
  closeModal: (modalId: string) => void;
  isModalOpen: (modalId: string) => boolean;
  getModalProps: (modalId: string) => any;
}

const ModalContext = createContext<ModalContextType | null>(null);

export function useModal() {
  const context = useContext(ModalContext);
  if (!context) {
    throw new Error('useModal must be used within a ModalProvider');
  }
  return context;
}

interface ModalProviderProps {
  children: React.ReactNode;
}

export function ModalProvider({ children }: ModalProviderProps) {
  const [modals, setModals] = useState<Map<string, any>>(new Map());

  const openModal = useCallback((modalId: string, props: any) => {
    setModals(prev => new Map(prev).set(modalId, props));
  }, []);

  const closeModal = useCallback((modalId: string) => {
    setModals(prev => {
      const newMap = new Map(prev);
      newMap.delete(modalId);
      return newMap;
    });
  }, []);

  const isModalOpen = useCallback((modalId: string) => {
    return modals.has(modalId);
  }, [modals]);

  const getModalProps = useCallback((modalId: string) => {
    return modals.get(modalId);
  }, [modals]);

  const contextValue: ModalContextType = {
    openModal,
    closeModal,
    isModalOpen,
    getModalProps
  };

  return (
    <ModalContext.Provider value={contextValue}>
      {children}
      {Array.from(modals.entries()).map(([modalId, props]) => (
        <ModalRenderer
          key={modalId}
          modalId={modalId}
          props={props}
          onClose={() => closeModal(modalId)}
        />
      ))}
    </ModalContext.Provider>
  );
}

interface ModalRendererProps {
  modalId: string;
  props: any;
  onClose: () => void;
}

function ModalRenderer({ modalId, props, onClose }: ModalRendererProps) {
  const { title, content, onConfirm, onCancel, confirmText, cancelText, variant } = props;

  const handleConfirm = () => {
    if (onConfirm) {
      onConfirm();
    }
    onClose();
  };

  const handleCancel = () => {
    if (onCancel) {
      onCancel();
    }
    onClose();
  };

  return (
    <Dialog open={true} onOpenChange={onClose}>
      <DialogContent className="sm:max-w-md">
        <DialogHeader>
          <DialogTitle className="flex items-center justify-between">
            {title || 'Modal'}
            <Button
              variant="ghost"
              size="sm"
              onClick={onClose}
              className="h-6 w-6 p-0"
            >
              <X className="h-4 w-4" />
            </Button>
          </DialogTitle>
        </DialogHeader>
        
        <div className="py-4">
          {content}
        </div>
        
        <div className="flex justify-end gap-2">
          {cancelText && (
            <Button variant="outline" onClick={handleCancel}>
              {cancelText}
            </Button>
          )}
          {confirmText && (
            <Button 
              variant={variant || "default"} 
              onClick={handleConfirm}
            >
              {confirmText}
            </Button>
          )}
        </div>
      </DialogContent>
    </Dialog>
  );
}

// Predefined modal types
export const ModalTypes = {
  CONFIRM: 'confirm',
  ALERT: 'alert',
  CUSTOM: 'custom'
} as const;

export type ModalType = typeof ModalTypes[keyof typeof ModalTypes];
