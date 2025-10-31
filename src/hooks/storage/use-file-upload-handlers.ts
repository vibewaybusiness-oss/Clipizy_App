"use client";

import { useCallback } from "react";
import { useToast } from "../ui/use-toast";
import { projectsAPI } from "@/lib/api/projects";
import { getValidatedAudioDuration, isValidDuration } from "@/utils/music-clip-utils";
import { useGlobalAudioMemoryManagement } from "./use-audio-memory-management";
import { createValidatedBlobURL } from "@/utils/memory-management";
import type { MusicTrack } from "@/types/domains/music";

interface UseFileUploadHandlersProps {
  musicClipState: any;
  musicTracks: any;
  projectManagement: any;
  setShowOnboardingLoading: (loading: boolean) => void;
}

// Helper function to generate file checksum
async function generateFileChecksum(file: File): Promise<string> {
  try {
    const arrayBuffer = await file.arrayBuffer();
    const hashBuffer = await crypto.subtle.digest('SHA-256', arrayBuffer);
    const hashArray = Array.from(new Uint8Array(hashBuffer));
    return hashArray.map(b => b.toString(16).padStart(2, '0')).join('');
  } catch (error) {
    console.warn('Failed to generate file checksum:', error);
    return `${file.name}_${file.size}_${file.lastModified}`;
  }
}

export function useFileUploadHandlers({
  musicClipState,
  musicTracks,
  projectManagement,
  setShowOnboardingLoading
}: UseFileUploadHandlersProps) {
  const { toast } = useToast();
  const audioMemoryManager = useGlobalAudioMemoryManagement();

  // Get current user ID for traceability
  const getCurrentUserId = () => {
    if (typeof window !== 'undefined') {
      const userStr = localStorage.getItem('user');
      if (userStr) {
        try {
          const user = JSON.parse(userStr);
          return user.id || 'unknown';
        } catch (error) {
          console.warn('Failed to parse user data:', error);
        }
      }
    }
    return 'unknown';
  };

  const handleAudioFileChange = useCallback(async (files: File[]) => {
    console.log('🎵 handleAudioFileChange called with files:', files.map(f => ({ name: f.name, type: f.type, size: f.size })));
    
    // Check if user is authenticated
    const currentUserId = getCurrentUserId();
    if (!currentUserId || currentUserId === 'unknown') {
      toast({
        variant: "destructive",
        title: "Authentication Required",
        description: "Please log in to upload files.",
      });
      return;
    }
    
    const audioFiles = files.filter(file => file.type.startsWith("audio/"));
    console.log('🎵 Filtered audio files:', audioFiles.map(f => ({ name: f.name, type: f.type, size: f.size })));

    if (audioFiles.length === 0) {
      console.log('❌ No audio files found');
      toast({
        variant: "destructive",
        title: "Invalid File Type",
        description: "Please upload audio files (e.g., MP3, WAV).",
      });
      return;
    }

    console.log('🎵 Starting upload process...');
    musicClipState.actions.setIsUploadingTracks(true);

    try {
      let currentProjectId = projectManagement.state.currentProjectId;
      console.log('🎵 Project management state for file upload:', {
        currentProjectId: projectManagement.state.currentProjectId,
        isProjectCreated: projectManagement.state.isProjectCreated,
        isLoadingProject: projectManagement.state.isLoadingProject
      });
      
      if (projectManagement.state.isLoadingProject) {
        console.log('🎵 Project is currently loading for file upload, waiting...');
        await new Promise(resolve => setTimeout(resolve, 1000));
        currentProjectId = projectManagement.state.currentProjectId;
        console.log('🎵 After waiting for file upload, currentProjectId:', currentProjectId);
      }
      
      if (!currentProjectId) {
        console.log('🎵 Creating new project...');
        try {
          currentProjectId = await projectManagement.actions.createProject();
          console.log('🎵 Project created with ID:', currentProjectId);
        } catch (createError) {
          console.error('❌ Failed to create project via projectManagement:', createError);
          throw new Error(`Failed to create project: ${createError instanceof Error ? createError.message : String(createError)}`);
        }
      } else {
        console.log('🎵 Using existing project ID:', currentProjectId);
      }

      if (!currentProjectId) {
        console.log('🎵 No project ID found, creating a new project...');
        try {
          const newProject = await projectsAPI.createMusicClipProject('My Music Project', 'Created for file upload');
          currentProjectId = newProject.id;
          console.log('🎵 Created new project:', newProject);
          
          // Update the project management state
          projectManagement.actions.setCurrentProjectId(currentProjectId);
        } catch (createError) {
          console.error('❌ Failed to create project:', createError);
          throw new Error('Failed to create project for file upload');
        }
      }

      if (audioFiles.length > 1) {
        console.log('🎵 Uploading multiple files individually...');
        
        const newTracks: MusicTrack[] = [];
        let successCount = 0;
        let failCount = 0;

        for (const file of audioFiles) {
          try {
            // Validate duration before upload
            const durationResult = await getValidatedAudioDuration(file);
            console.log('🎵 Duration validation result for file:', file.name, durationResult);
            
            if (!durationResult.isValid) {
              console.warn('🎵 Invalid duration for file:', file.name, durationResult.error);
              toast({
                variant: "destructive",
                title: "Invalid Audio File",
                description: `${file.name}: ${durationResult.error}`,
              });
              failCount++;
              continue;
            }

            const uploadResult = await projectsAPI.uploadTrack(currentProjectId, file, {
              ai_generated: false,
              instrumental: false,
            });

            const url = createValidatedBlobURL(file);
            const finalDuration = durationResult.duration || uploadResult.data?.metadata?.duration || 0;

            // Generate file checksum for traceability
            const checksum = await generateFileChecksum(file);

            // Generate a unique track ID if backend doesn't provide one
            const trackId = uploadResult.data?.track_id || 
                           uploadResult.data?.id || 
                           uploadResult.data?.file_id || 
                           `track_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;
            
            console.log('🎵 Generated track ID for multiple upload:', trackId);

            const newTrack: MusicTrack = {
              id: trackId,
              file: file,
              url: url,
              duration: finalDuration,
              name: file.name,
              generatedAt: new Date(),
              prompt: uploadResult.data?.prompt,
              genre: uploadResult.data?.genre,
              videoDescription: uploadResult.data?.video_description,
              isGenerated: uploadResult.data?.ai_generated || false,
              status: 'completed',
              uploaded: true,
              created_at: new Date().toISOString(),
              // Enhanced file traceability
              originalFileInfo: {
                name: file.name,
                size: file.size,
                type: file.type,
                lastModified: file.lastModified,
                checksum: checksum,
                uploadSource: 'file_upload',
                uploadTimestamp: new Date().toISOString(),
                projectId: currentProjectId,
                userId: getCurrentUserId()
              },
              // Legacy backend storage removed - using unified PostgreSQL JSONB
              filePath: uploadResult.data?.file_path || '',
              bucket: 'clipizy',
              region: 'eu-north-1',
              uploadMethod: uploadResult.data?.file_path?.startsWith('http') ? 's3' : 'local',
              storageUrl: uploadResult.data?.file_path
            };

            console.log('🎵 Created new track for multiple upload:', {
              trackId: newTrack.id,
              fileName: newTrack.name,
              uploadResult: uploadResult.data
            });

            newTracks.push(newTrack);
            successCount++;

            if (finalDuration === 0) {
              const audio = new Audio(url);
              audio.addEventListener('loadedmetadata', () => {
                if (audio.duration && !isNaN(audio.duration) && audio.duration !== Infinity) {
                  musicTracks.updateTrackDuration(newTrack.id, audio.duration);
                }
              });
            }
          } catch (error) {
            console.error(`Failed to upload ${file.name}:`, error);
            failCount++;
          }
        }

        if (newTracks.length > 0) {
         console.log('🎵 Adding tracks to UI:', newTracks);
         musicTracks.addTracks(newTracks);
         console.log('🎵 Tracks added to musicTracks state');
         
         // Force save tracks to backend immediately to prevent them from being lost
         if (musicTracks.saveTracksToBackend) {
           await musicTracks.saveTracksToBackend();
           console.log('🎵 Tracks saved to backend immediately');
         }

          const firstTrack = newTracks[0];
          if (firstTrack.file && firstTrack.file instanceof File) {
            musicClipState.actions.setAudioFile(firstTrack.file);
            console.log('🎵 Set audio file in state');
          } else {
            musicClipState.actions.setAudioFile(null);
            console.log('🎵 Cleared audio file in state');
          }
          musicClipState.actions.setAudioUrl(firstTrack.url);
          musicClipState.actions.setAudioDuration(firstTrack.duration);
          console.log('🎵 Set audio URL and duration in state');
        }

        if (failCount > 0) {
          toast({
            variant: "destructive",
            title: "Some Uploads Failed",
            description: `Successfully uploaded ${successCount} file(s), failed to upload ${failCount} file(s).`,
          });
        } else {
          toast({
            title: "Tracks Uploaded",
            description: `Successfully uploaded ${successCount} track(s).`,
          });
        }
      } else {
        const file = audioFiles[0];
        console.log('🎵 Uploading single file:', file.name);
        try {
          let fileDuration = 0;
          try {
            fileDuration = await getAudioDuration(file);
            console.log('🎵 Extracted duration from file:', fileDuration);
          } catch (durationError) {
            console.warn('🎵 Failed to extract duration from file:', durationError);
          }

          const uploadResult = await projectsAPI.uploadTrack(currentProjectId, file, {
            ai_generated: false,
            instrumental: false,
          });
          console.log('🎵 Single upload result:', uploadResult);
          console.log('🎵 Upload result data structure:', {
            data: uploadResult.data,
            track_id: uploadResult.data?.track_id,
            id: uploadResult.data?.id,
            file_id: uploadResult.data?.file_id,
            allKeys: uploadResult.data ? Object.keys(uploadResult.data) : []
          });

          // Log file details before creating blob URL
          console.log('🎵 File details before blob URL creation:', {
            name: file.name,
            size: file.size,
            type: file.type,
            lastModified: file.lastModified
          });
          
          const url = createValidatedBlobURL(file);
          console.log('🎵 Created blob URL:', url);
          
          // Test blob URL immediately after creation
          const testAudio = new Audio();
          testAudio.onloadedmetadata = () => {
            console.log('🎵 Blob URL test: SUCCESS - file can be loaded');
          };
          testAudio.onerror = (e) => {
            console.error('🎵 Blob URL test: FAILED - file cannot be loaded', e);
            console.error('🎵 This indicates the file may be corrupted during upload process');
          };
          testAudio.src = url;
          
          const finalDuration = fileDuration || uploadResult.data?.metadata?.duration || 0;

              // Generate file checksum for traceability
              const checksum = await generateFileChecksum(file);

              // Generate a unique track ID if backend doesn't provide one
              const trackId = uploadResult.data?.track_id || 
                             uploadResult.data?.id || 
                             uploadResult.data?.file_id || 
                             `track_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;
              
              console.log('🎵 Generated track ID:', trackId);

              const newTrack: MusicTrack = {
                id: trackId,
                file: file,
                url: url,
                duration: finalDuration,
                name: file.name,
                generatedAt: new Date(),
                prompt: uploadResult.data?.prompt,
                genre: uploadResult.data?.genre,
                videoDescription: uploadResult.data?.video_description,
                isGenerated: uploadResult.data?.ai_generated || false,
                status: 'completed',
                uploaded: true,
                created_at: new Date().toISOString(),
                // Enhanced file traceability
                originalFileInfo: {
                  name: file.name,
                  size: file.size,
                  type: file.type,
                  lastModified: file.lastModified,
                  checksum: checksum,
                  uploadSource: 'file_upload',
                  uploadTimestamp: new Date().toISOString(),
                  projectId: currentProjectId,
                  userId: getCurrentUserId()
                },
                // Legacy backend storage removed - using unified PostgreSQL JSONB
                filePath: uploadResult.data?.file_path || '',
                bucket: 'clipizy',
                region: 'eu-north-1',
                uploadMethod: uploadResult.data?.file_path?.startsWith('http') ? 's3' : 'local',
                storageUrl: uploadResult.data?.file_path
          };

          console.log('🎵 Created new track for single upload:', {
            trackId: newTrack.id,
            fileName: newTrack.name,
            uploadResult: uploadResult.data
          });

         console.log('🎵 Adding track to UI:', newTrack);
         musicTracks.addTracks([newTrack]);
         console.log('🎵 Track added to musicTracks state');
         
         // Force save tracks to backend immediately to prevent them from being lost
         if (musicTracks.saveTracksToBackend) {
           await musicTracks.saveTracksToBackend();
           console.log('🎵 Track saved to backend immediately');
         }

          if (newTrack.file && newTrack.file instanceof File) {
            musicClipState.actions.setAudioFile(newTrack.file);
            console.log('🎵 Set audio file in state');
          } else {
            musicClipState.actions.setAudioFile(null);
            console.log('🎵 Cleared audio file in state');
          }
          musicClipState.actions.setAudioUrl(newTrack.url);
          musicClipState.actions.setAudioDuration(newTrack.duration);
          console.log('🎵 Set audio URL and duration in state');

          if (finalDuration === 0) {
            const audio = new Audio(url);
            audio.addEventListener('loadedmetadata', () => {
              if (audio.duration && !isNaN(audio.duration) && audio.duration !== Infinity) {
                musicTracks.updateTrackDuration(newTrack.id, audio.duration);
                musicClipState.actions.setAudioDuration(audio.duration);
              }
            });
          }

          toast({
            title: "Track Uploaded",
            description: `Successfully uploaded ${file.name}.`,
          });
          console.log('🎵 Upload completed successfully');
        } catch (error) {
          console.error('Error uploading single track:', error);
          toast({
            variant: "destructive",
            title: "Upload Failed",
            description: `Failed to upload ${file.name}. Please try again.`,
          });
        }
      }
    } catch (error) {
      console.error('Error in handleAudioFileChange:', error);
      toast({
        variant: "destructive",
        title: "Upload Failed",
        description: "Failed to upload tracks. Please try again.",
      });
    } finally {
      musicClipState.actions.setIsUploadingTracks(false);
      setShowOnboardingLoading(false);
    }
  }, [musicClipState, musicTracks, projectManagement, toast]);

  return {
    handleAudioFileChange
  };
}
