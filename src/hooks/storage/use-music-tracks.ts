"use client";

import { useState, useCallback, useMemo } from "react";
import { useToast } from "../ui/use-toast";
import { musicService } from "@/lib/api/music";
import type { MusicTrack } from "@/types/domains/music";

interface UseMusicTracksProps {
  projectId: string | null;
  markAsChanged?: () => void;
}

export function useMusicTracks({ projectId, markAsChanged }: UseMusicTracksProps) {
  const [tracks, setTracks] = useState<MusicTrack[]>([]);
  const [selectedTrackId, setSelectedTrackId] = useState<string | null>(null);
  const [selectedTrackIds, setSelectedTrackIdsState] = useState<string[]>([]);
  const { toast } = useToast();

  const selectedTrack = useMemo(() => {
    return tracks.find(track => track.id === selectedTrackId) || null;
  }, [tracks, selectedTrackId]);

  const addTracks = useCallback((newTracks: MusicTrack[]) => {
    console.log('🎵 addTracks called with:', {
      newTracksCount: newTracks.length,
      newTrackIds: newTracks.map(t => t.id),
      newTrackNames: newTracks.map(t => t.name)
    });
    
    setTracks(prevTracks => {
      console.log('🎵 Current tracks before adding:', {
        currentTracksCount: prevTracks.length,
        currentTrackIds: prevTracks.map(t => t.id),
        currentTrackNames: prevTracks.map(t => t.name)
      });
      
          const existingIds = new Set(prevTracks.map(track => track.id));
          const uniqueNewTracks = newTracks.filter(track => !existingIds.has(track.id));

          console.log('🎵 Track filtering result:', {
            totalNewTracks: newTracks.length,
            uniqueNewTracks: uniqueNewTracks.length,
            duplicateTracks: newTracks.length - uniqueNewTracks.length,
            duplicateTrackIds: newTracks.filter(track => existingIds.has(track.id)).map(t => t.id),
            newTrackIds: newTracks.map(t => t.id),
            existingTrackIds: Array.from(existingIds),
            newTrackIdsWithTypes: newTracks.map(t => ({ id: t.id, type: typeof t.id, isUndefined: t.id === undefined }))
          });
      
      if (uniqueNewTracks.length === 0) {
        console.log('🎵 No unique tracks to add, returning existing tracks');
        return prevTracks;
      }
      
      const updatedTracks = [...prevTracks, ...uniqueNewTracks];
      
      console.log('🎵 Updated tracks after adding:', {
        totalTracks: updatedTracks.length,
        addedTrackIds: uniqueNewTracks.map(t => t.id),
        addedTrackNames: uniqueNewTracks.map(t => t.name)
      });
      
      if (!selectedTrackId && uniqueNewTracks.length > 0) {
        const firstTrackId = uniqueNewTracks[0].id;
        setSelectedTrackId(firstTrackId);
        setSelectedTrackIdsState([firstTrackId]);
        console.log('🎵 Set selected track ID to:', firstTrackId);
      }
      
      return updatedTracks;
    });
    
    // Trigger auto-save when tracks are added
    markAsChanged?.();
  }, [selectedTrackId, markAsChanged]);

  const removeTrack = useCallback(async (trackId: string, deleteFromBackend: boolean = true) => {
    try {
      if (projectId && deleteFromBackend) {
        await musicService.deleteTrack(projectId, trackId);
      }
      
      setTracks(prevTracks => {
        const updatedTracks = prevTracks.filter(track => track.id !== trackId);
        
        if (selectedTrackId === trackId) {
          setSelectedTrackId(updatedTracks.length > 0 ? updatedTracks[0].id : null);
        }
        
        return updatedTracks;
      });
      
      // Remove from selected tracks array
      setSelectedTrackIdsState(prev => prev.filter(id => id !== trackId));
      
      // Trigger auto-save when tracks are removed
      markAsChanged?.();
      
      toast({
        title: "Track Removed",
        description: "Track has been successfully removed.",
      });
    } catch (error) {
      console.error('Error removing track:', error);
      toast({
        variant: "destructive",
        title: "Error",
        description: "Failed to remove track. Please try again.",
      });
    }
  }, [projectId, toast]);

  const removeTracks = useCallback(async (trackIds: string[], deleteFromBackend: boolean = true) => {
    try {
      if (projectId && deleteFromBackend) {
        // Delete all tracks from backend
        await Promise.all(trackIds.map(trackId => musicService.deleteTrack(projectId, trackId)));
      }
      
      setTracks(prevTracks => {
        const updatedTracks = prevTracks.filter(track => !trackIds.includes(track.id));
        
        // Update selected track if it was removed
        if (selectedTrackId && trackIds.includes(selectedTrackId)) {
          setSelectedTrackId(updatedTracks.length > 0 ? updatedTracks[0].id : null);
        }
        
        return updatedTracks;
      });
      
      // Remove from selected tracks array
      setSelectedTrackIdsState(prev => prev.filter(id => !trackIds.includes(id)));
      
      // Trigger auto-save when tracks are removed
      markAsChanged?.();
      
      toast({
        title: "Tracks Removed",
        description: `${trackIds.length} tracks have been successfully removed.`,
      });
    } catch (error) {
      console.error('Error removing tracks:', error);
      toast({
        variant: "destructive",
        title: "Error",
        description: "Failed to remove tracks. Please try again.",
      });
    }
  }, [projectId, selectedTrackId, toast]);

  const selectTrack = useCallback((track: MusicTrack, event?: React.MouseEvent) => {
    const trackId = track.id;
    
    if (event?.ctrlKey || event?.metaKey) {
      // Multi-select mode
      setSelectedTrackIdsState(prev => {
        if (prev.includes(trackId)) {
          // Remove from selection
          const newSelection = prev.filter(id => id !== trackId);
          setSelectedTrackId(newSelection.length > 0 ? newSelection[0] : null);
          return newSelection;
        } else {
          // Add to selection
          const newSelection = [...prev, trackId];
          setSelectedTrackId(trackId);
          return newSelection;
        }
      });
    } else {
      // Single select mode
      setSelectedTrackId(trackId);
      setSelectedTrackIdsState([trackId]);
    }
    markAsChanged?.();
  }, [markAsChanged]);

  const reorderTracks = useCallback((startIndex: number, endIndex: number) => {
    setTracks(prevTracks => {
      const result = Array.from(prevTracks);
      const [removed] = result.splice(startIndex, 1);
      result.splice(endIndex, 0, removed);
      return result;
    });
  }, []);

  const updateTrackDuration = useCallback((trackId: string, duration: number) => {
    setTracks(prevTracks => 
      prevTracks.map(track => 
        track.id === trackId ? { ...track, duration } : track
      )
    );
    
    // Trigger auto-save when track duration is updated
    markAsChanged?.();
  }, [markAsChanged]);

  const updateTrack = useCallback((trackId: string, updates: Partial<MusicTrack>) => {
    setTracks(prevTracks => 
      prevTracks.map(track => 
        track.id === trackId ? { ...track, ...updates } : track
      )
    );
    
    // Trigger auto-save when track is updated
    markAsChanged?.();
  }, [markAsChanged]);

  const updateTrackAnalysis = useCallback((trackId: string, analysis: any) => {
    console.log('🎵 Updating track analysis:', { trackId, analysis });
    console.log('🎵 Analysis data structure:', analysis);
    console.log('🎵 Analysis keys:', analysis ? Object.keys(analysis) : 'null');
    
    setTracks(prevTracks => {
      const updatedTracks = prevTracks.map(track => 
        track.id === trackId ? { ...track, analysis } : track
      );
      
      console.log('🎵 Updated tracks:', updatedTracks);
      const updatedTrack = updatedTracks.find(t => t.id === trackId);
      console.log('🎵 Updated track analysis:', updatedTrack?.analysis);
      
      return updatedTracks;
    });
    
    // Trigger auto-save when track analysis is updated
    markAsChanged?.();
  }, [markAsChanged]);

  const clearTracks = useCallback(() => {
    setTracks([]);
    setSelectedTrackId(null);
    
    // Trigger auto-save when tracks are cleared
    markAsChanged?.();
  }, [markAsChanged]);

  const setTracksFromData = useCallback((tracksData: MusicTrack[]) => {
    setTracks(tracksData);
    if (tracksData.length > 0 && !selectedTrackId) {
      setSelectedTrackId(tracksData[0].id);
    }
  }, [selectedTrackId]);

  // Additional methods expected by orchestrator
  const getCurrentState = useCallback(() => {
    return {
      tracks,
      selectedTrackId,
      selectedTrack
    };
  }, [tracks, selectedTrackId, selectedTrack]);

  const loadTracksFromBackend = useCallback((backendTracks: MusicTrack[]) => {
    console.log('🔄 loadTracksFromBackend called with:', {
      trackCount: backendTracks.length,
      tracks: backendTracks.map(t => ({ 
        id: t.id, 
        name: t.name, 
        url: t.url, 
        duration: t.duration,
        status: t.status,
        hasBlob: !!(t as any).blob,
        hasBlobUrl: !!(t as any).blobUrl,
        blobSize: (t as any).blob?.size,
        blobType: (t as any).blob?.type
      }))
    });
    
    setTracks(prevTracks => {
      console.log('🔄 Current tracks before backend load:', {
        currentTrackCount: prevTracks.length,
        currentTrackIds: prevTracks.map(t => t.id),
        currentTrackNames: prevTracks.map(t => t.name)
      });
      
      // Merge backend tracks with existing tracks
      // Backend tracks take precedence for existing IDs, but keep local tracks that aren't in backend
      const backendTrackIds = new Set(backendTracks.map(t => t.id));
      const localTracksNotInBackend = prevTracks.filter(t => !backendTrackIds.has(t.id));
      
      const mergedTracks = [...backendTracks, ...localTracksNotInBackend];
      
      console.log('🔄 Track merging result:', {
        backendTracks: backendTracks.length,
        localTracksNotInBackend: localTracksNotInBackend.length,
        mergedTracks: mergedTracks.length,
        localTrackIds: localTracksNotInBackend.map(t => t.id),
        localTrackNames: localTracksNotInBackend.map(t => t.name)
      });
      
      return mergedTracks;
    });
    
    console.log('🔄 Tracks state updated with merged tracks');
    
    if (backendTracks.length > 0 && !selectedTrackId) {
      setSelectedTrackId(backendTracks[0].id);
      console.log('🔄 Set selected track ID to:', backendTracks[0].id);
    }
    markAsChanged?.();
  }, [selectedTrackId, markAsChanged]);

  const setMusicTracks = useCallback((newTracks: MusicTrack[]) => {
    setTracks(newTracks);
    markAsChanged?.();
  }, [markAsChanged]);

  const saveTracksToBackend = useCallback(async () => {
    console.log('🔄 Saving tracks to backend immediately...');
    try {
      // This will trigger the backend storage to save the current tracks
      markAsChanged?.();
      console.log('🔄 Tracks marked for backend save');
    } catch (error) {
      console.error('🔄 Failed to save tracks to backend:', error);
    }
  }, [markAsChanged]);

  const reloadTracksFromBackend = useCallback((backendTracks: MusicTrack[]) => {
    // Force reload - replace all tracks with backend tracks
    setTracks(backendTracks);
    if (backendTracks.length > 0 && !selectedTrackId) {
      setSelectedTrackId(backendTracks[0].id);
    }
    markAsChanged?.();
  }, [selectedTrackId, markAsChanged]);

  const setSelectedTrackIdMethod = useCallback((trackId: string | null) => {
    setSelectedTrackId(trackId);
    markAsChanged?.();
  }, [markAsChanged]);

  const setSelectedTrackIds = useCallback((trackIds: string[]) => {
    setSelectedTrackIdsState(trackIds);
    // Set the first track as the primary selected track
    if (trackIds.length > 0) {
      setSelectedTrackId(trackIds[0]);
    } else {
      setSelectedTrackId(null);
    }
    markAsChanged?.();
  }, [markAsChanged]);

  const setTrackDescriptions = useCallback((descriptions: Record<string, string>) => {
    // Update tracks with descriptions
    setTracks(prevTracks => 
      prevTracks.map(track => ({
        ...track,
        description: descriptions[track.id] || track.description
      }))
    );
    markAsChanged?.();
  }, [markAsChanged]);

  const setTrackGenres = useCallback((genres: Record<string, string>) => {
    // Update tracks with genres
    setTracks(prevTracks => 
      prevTracks.map(track => ({
        ...track,
        genre: genres[track.id] || track.genre
      }))
    );
    markAsChanged?.();
  }, [markAsChanged]);

  return {
    tracks,
    selectedTrack,
    selectedTrackId,
    selectedTrackIds,
    addTracks,
    removeTrack,
    removeTracks,
    selectTrack,
    reorderTracks,
    updateTrackDuration,
    updateTrack,
    updateTrackAnalysis,
    clearTracks,
    clearAllTracks: clearTracks, // Alias for compatibility
    setTracksFromData,
    getCurrentState,
    loadTracksFromBackend,
    reloadTracksFromBackend,
    setMusicTracks,
    saveTracksToBackend,
    setSelectedTrackId: setSelectedTrackIdMethod,
    setSelectedTrackIds,
    setTrackDescriptions,
    setTrackGenres
  };
}
