import { BaseApiClient } from './base';

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

interface AnalysisResult {
  trackId: string;
  analysis?: any;
  error?: string;
}

class MusicService extends BaseApiClient {
  constructor() {
    super(API_BASE_URL);
  }

  async analyzeTracksInParallel(tracks: any[]): Promise<AnalysisResult[]> {
    console.log(`🎵 Analyzing ${tracks.length} tracks in parallel`);
    
    try {
      // Make real API calls to analyze tracks
      const results: AnalysisResult[] = [];
      
      for (const track of tracks) {
        console.log(`🔍 Analyzing track: ${track.name} (${track.id})`);
        
        try {
          // Call the real analysis API endpoint
          const response = await this.post(`/api/music-analysis/music/${track.id}`);
          
          // Extract the actual analysis data from the response
          const analysisData = response.analysis || response;
          
          results.push({
            trackId: track.id,
            analysis: analysisData
          });
        } catch (error) {
          console.error(`❌ Analysis failed for track ${track.id}:`, error);
          results.push({
            trackId: track.id,
            error: error instanceof Error ? error.message : 'Analysis failed'
          });
        }
      }

      console.log(`✅ Analysis completed for ${results.length} tracks`);
      return results;
      
    } catch (error) {
      console.error('❌ Analysis failed:', error);
      return tracks.map(track => ({
        trackId: track.id,
        error: error instanceof Error ? error.message : 'Analysis failed'
      }));
    }
  }

  async deleteTrack(projectId: string, trackId: string): Promise<void> {
    console.log(`🗑️ Deleting track ${trackId} from project ${projectId}`);
    
    try {
      await this.delete(`/api/storage/projects/${projectId}/files/${trackId}`);
      console.log(`✅ Track ${trackId} deleted successfully`);
    } catch (error) {
      console.error(`❌ Failed to delete track ${trackId}:`, error);
      throw error;
    }
  }
}

export const musicService = new MusicService();
