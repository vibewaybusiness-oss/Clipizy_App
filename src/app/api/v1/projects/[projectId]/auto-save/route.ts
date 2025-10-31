import { NextRequest, NextResponse } from 'next/server';
import { withErrorHandling, requireAuth, ValidationError } from '../../../middleware/error-handling';

export async function POST(
  request: NextRequest,
  { params }: { params: Promise<{ projectId: string }> }
) {
  console.log('🚀 AUTO-SAVE ROUTE: Starting request processing');
  
  try {
    return await withErrorHandling(requireAuth(async (req: NextRequest) => {
      console.log('🔐 AUTH: Authentication successful, proceeding with auto-save');
      
      const { projectId } = await params;
      const data = await req.json();

      if (!projectId) {
        console.error('❌ VALIDATION: Project ID is missing');
        throw new ValidationError('Project ID is required');
      }

      console.log(`🔄 UNIFIED SAVE ROUTE: Auto-saving data for project ${projectId}`);

      // Validate required data structure
      if (!data.projectType || !data.projectData) {
        console.error('❌ VALIDATION: Invalid data structure', {
          hasProjectType: !!data.projectType,
          hasProjectData: !!data.projectData,
          dataKeys: Object.keys(data)
        });
        throw new ValidationError('Invalid data structure. Expected projectType and projectData.');
      }

    try {
      // Forward the request to the running backend
      const { makeBackendRequest } = await import('../../../lib/utils/backend');
      
      console.log(`📤 BACKEND: Forwarding to running backend for project ${projectId}`);
      console.log(`📦 Data structure:`, {
        projectType: data.projectType,
        hasSettings: !!data.projectData.settings,
        hasAnalysis: !!data.projectData.analysis,
        settingsKeys: data.projectData.settings ? Object.keys(data.projectData.settings) : []
      });

      const response = await makeBackendRequest(`/api/storage/projects/${projectId}/auto-save`, {
        method: 'POST',
        body: data
      }, req);

      if (!response.ok) {
        const errorText = await response.text();
        console.error('❌ Backend error response:', errorText);
        return NextResponse.json(
          { error: `Backend error: ${response.status} - ${errorText}` },
          { status: response.status }
        );
      }

      const result = await response.json();
      console.log('✅ REAL: Data saved successfully to PostgreSQL via backend');
      return NextResponse.json(result);
    } catch (error: any) {
      console.error('❌ Failed to auto-save project data:', error);
      return NextResponse.json(
        { error: `Auto-save failed: ${error.message}` },
        { status: 500 }
      );
    }
    }))(request);
  } catch (error: any) {
    console.error('❌ AUTO-SAVE ROUTE ERROR:', error);
    console.error('❌ Error stack:', error.stack);
    return NextResponse.json(
      { error: `Route error: ${error.message}` },
      { status: 500 }
    );
  }
}
