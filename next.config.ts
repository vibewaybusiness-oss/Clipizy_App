import type {NextConfig} from 'next';

const nextConfig: NextConfig = {
  /* config options here */
  typescript: {
    ignoreBuildErrors: false,
  },
  eslint: {
    ignoreDuringBuilds: false,
  },
  // Ensure Next.js binds to all interfaces for WSL compatibility
  experimental: {
    serverActions: {
      bodySizeLimit: '100mb',
    },
  },
  images: {
    remotePatterns: [
      {
        protocol: 'https',
        hostname: 'placehold.co',
        port: '',
        pathname: '/**',
      },
      {
        protocol: 'https',
        hostname: 'picsum.photos',
        port: '',
        pathname: '/**',
      },
    ],
  },
  async rewrites() {
    // Use backend URL from environment variable (centralized in settings.py)
    // For WSL, use the Windows host IP that's accessible from WSL
    let backendUrl = process.env.BACKEND_URL || 'http://localhost:8000';
    
    // If running in WSL and no BACKEND_URL is set, use the Windows host IP
    if (process.env.WSL_DISTRO_NAME && !process.env.BACKEND_URL) {
      backendUrl = 'http://172.31.240.1:8000';
    }
    
    console.log('Next.js rewrites using backend URL:', backendUrl);
    
    return [
      {
        source: '/api/auth/:path*',
        destination: `${backendUrl}/api/auth/:path*`,
      },
      {
        source: '/api/projects/:path*',
        destination: `${backendUrl}/api/projects/:path*`,
      },
      {
        source: '/api/tracks/:path*',
        destination: `${backendUrl}/api/tracks/:path*`,
      },
      {
        source: '/api/exports/:path*',
        destination: `${backendUrl}/api/exports/:path*`,
      },
      {
        source: '/api/stats/:path*',
        destination: `${backendUrl}/api/stats/:path*`,
      },
      {
        source: '/api/prompts/:path*',
        destination: `${backendUrl}/api/prompts/:path*`,
      },
      // Removed /api/analysis/:path* rewrite - handled by Next.js API routes
      {
        source: '/api/music-analysis/:path*',
        destination: `${backendUrl}/api/music-analysis/:path*`,
      },
      {
        source: '/file-path/:path*',
        destination: `${backendUrl}/file-path/:path*`,
      },
      {
        source: '/api/particles/:path*',
        destination: `${backendUrl}/api/particles/:path*`,
      },
      {
        source: '/api/visualizers/:path*',
        destination: `${backendUrl}/api/visualizers/:path*`,
      },
      {
        source: '/api/comfyui/:path*',
        destination: `${backendUrl}/api/comfyui/:path*`,
      },
      {
        source: '/api/chatbot/:path*',
        destination: `${backendUrl}/api/chatbot/:path*`,
      },
      {
        source: '/api/runpod/:path*',
        destination: `${backendUrl}/api/runpod/:path*`,
      },
      {
        source: '/api/ai/:path*',
        destination: `${backendUrl}/api/ai/:path*`,
      },
      {
        source: '/api/credits/:path*',
        destination: `${backendUrl}/api/credits/:path*`,
      },
      {
        source: '/api/payments/:path*',
        destination: `${backendUrl}/api/payments/:path*`,
      },
      {
        source: '/api/social-media/:path*',
        destination: `${backendUrl}/api/social-media/:path*`,
      },
      {
        source: '/api/automation/:path*',
        destination: `${backendUrl}/api/automation/:path*`,
      },
      {
        source: '/api/storage/:path*',
        destination: `${backendUrl}/api/storage/:path*`,
      },
      {
        source: '/user-management/:path*',
        destination: `${backendUrl}/user-management/:path*`,
      },
      {
        source: '/backend/:path*',
        destination: '/api/backend/:path*',
      },
    ];
  },
};

export default nextConfig;
