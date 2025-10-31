import { useState, useCallback, useEffect } from 'react';

export interface DragAndDropState {
  isDragOver: boolean;
  dragCounter: number;
  draggedTrackId: string | null;
  dragOverTrackId: string | null;
  isTrackReordering: boolean;
  dropPosition: 'above' | 'below' | null;
}

export interface DragAndDropActions {
  handleDragEnter: (e: React.DragEvent, isTrackReordering: boolean) => void;
  handleDragOver: (e: React.DragEvent, isTrackReordering: boolean) => void;
  handleDragLeave: (e: React.DragEvent, isTrackReordering: boolean) => void;
  handleDrop: (e: React.DragEvent, isTrackReordering: boolean) => void;
  handleDragStart: (e: React.DragEvent, trackId: string) => void;
  handleTrackDragOver: (e: React.DragEvent, trackId: string) => void;
  handleTrackDrop: (e: React.DragEvent, trackId: string) => { fromId: string; toId: string; position: 'above' | 'below' | null } | null;
  handleDragEnd: () => void;
  resetDragState: () => void;
}

export function useDragAndDrop() {
  const [isDragOver, setIsDragOver] = useState(false);
  const [dragCounter, setDragCounter] = useState(0);
  const [draggedTrackId, setDraggedTrackId] = useState<string | null>(null);
  const [dragOverTrackId, setDragOverTrackId] = useState<string | null>(null);
  const [isTrackReordering, setIsTrackReordering] = useState(false);
  const [dropPosition, setDropPosition] = useState<'above' | 'below' | null>(null);

  // Global drag and drop handlers to prevent conflicts
  useEffect(() => {
    const handleGlobalDragOver = (e: DragEvent) => {
      e.preventDefault();
    };

    const handleGlobalDrop = (e: DragEvent) => {
      e.preventDefault();
    };

    const handleDragEnd = () => {
      setIsDragOver(false);
      setDragCounter(0);
    };

    if (typeof document !== 'undefined') {
      document.addEventListener('dragover', handleGlobalDragOver);
      document.addEventListener('drop', handleGlobalDrop);
      document.addEventListener('dragend', handleDragEnd);
    }

    return () => {
      if (typeof document !== 'undefined') {
        document.removeEventListener('dragover', handleGlobalDragOver);
        document.removeEventListener('drop', handleGlobalDrop);
        document.removeEventListener('dragend', handleDragEnd);
      }
    };
  }, []);

  const handleDragEnter = useCallback((e: React.DragEvent, isTrackReordering: boolean) => {
    e.preventDefault();
    e.stopPropagation();

    // Don't handle file upload if we're reordering tracks
    if (isTrackReordering) {
      return;
    }

    setDragCounter(prev => prev + 1);
    setIsDragOver(true);
  }, []);

  const handleDragOver = useCallback((e: React.DragEvent, isTrackReordering: boolean) => {
    e.preventDefault();
    e.stopPropagation();

    // Don't handle file upload if we're reordering tracks
    if (isTrackReordering) {
      return;
    }
  }, []);

  const handleDragLeave = useCallback((e: React.DragEvent, isTrackReordering: boolean) => {
    e.preventDefault();
    e.stopPropagation();

    // Don't handle file upload if we're reordering tracks
    if (isTrackReordering) {
      return;
    }

    setDragCounter(prev => {
      const newCount = prev - 1;
      if (newCount === 0) {
        setIsDragOver(false);
      }
      return newCount;
    });
  }, []);

  const handleDrop = useCallback((e: React.DragEvent, isTrackReordering: boolean) => {
    e.preventDefault();
    e.stopPropagation();

    // Don't handle file upload if we're reordering tracks
    if (isTrackReordering) {
      return;
    }

    setIsDragOver(false);
    setDragCounter(0);
  }, []);

  const handleDragStart = useCallback((e: React.DragEvent, trackId: string) => {
    setDraggedTrackId(trackId);
    setIsTrackReordering(true);
    e.dataTransfer.effectAllowed = 'move';
  }, []);

  const handleTrackDragOver = useCallback((e: React.DragEvent, trackId: string) => {
    e.preventDefault();
    e.stopPropagation();

    if (isTrackReordering && draggedTrackId && draggedTrackId !== trackId) {
      setDragOverTrackId(trackId);

      // Determine drop position based on mouse position
      const rect = e.currentTarget.getBoundingClientRect();
      const mouseY = e.clientY;
      const trackCenter = rect.top + rect.height / 2;

      if (mouseY < trackCenter) {
        setDropPosition('above');
      } else {
        setDropPosition('below');
      }
    }
  }, [isTrackReordering, draggedTrackId]);

  const handleTrackDrop = useCallback((e: React.DragEvent, trackId: string) => {
    e.preventDefault();
    e.stopPropagation();

    if (isTrackReordering && draggedTrackId && draggedTrackId !== trackId) {
      // This will be handled by the parent component
      return { fromId: draggedTrackId, toId: trackId, position: dropPosition };
    }

    return null;
  }, [isTrackReordering, draggedTrackId, dropPosition]);

  const handleDragEnd = useCallback(() => {
    setDraggedTrackId(null);
    setDragOverTrackId(null);
    setIsTrackReordering(false);
    setDropPosition(null);
  }, []);

  const resetDragState = useCallback(() => {
    setIsDragOver(false);
    setDragCounter(0);
    setDraggedTrackId(null);
    setDragOverTrackId(null);
    setIsTrackReordering(false);
    setDropPosition(null);
  }, []);

  const state: DragAndDropState = {
    isDragOver,
    dragCounter,
    draggedTrackId,
    dragOverTrackId,
    isTrackReordering,
    dropPosition,
  };

  const actions: DragAndDropActions = {
    handleDragEnter,
    handleDragOver,
    handleDragLeave,
    handleDrop,
    handleDragStart,
    handleTrackDragOver,
    handleTrackDrop,
    handleDragEnd,
    resetDragState,
  };

  return {
    state,
    actions,
  };
}
