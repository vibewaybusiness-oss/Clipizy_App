import React, { useState, useEffect } from 'react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { ScrollArea } from '@/components/ui/scroll-area';
import { Separator } from '@/components/ui/separator';
import {
  Folder,
  File,
  Image,
  Video,
  Music,
  FileText,
  Download,
  Eye,
  ArrowLeft,
  Calendar,
  Clock,
  HardDrive,
  Play,
  Pause
} from 'lucide-react';
import { Project } from '@/lib/api/projects';

interface FileItem {
  name: string;
  type: 'file' | 'folder';
  path: string;
  size?: number;
  modified?: string;
  extension?: string;
  children?: FileItem[];
}

interface ProjectFileExplorerProps {
  project: Project;
  onClose: () => void;
  onOpenProject: (project: Project) => void;
}

const FILE_ICONS = {
  // Images
  '.png': Image,
  '.jpg': Image,
  '.jpeg': Image,
  '.gif': Image,
  '.webp': Image,
  '.svg': Image,
  // Videos
  '.mp4': Video,
  '.avi': Video,
  '.mov': Video,
  '.wmv': Video,
  '.flv': Video,
  '.webm': Video,
  // Audio
  '.mp3': Music,
  '.wav': Music,
  '.flac': Music,
  '.aac': Music,
  '.ogg': Music,
  // Documents
  '.json': FileText,
  '.txt': FileText,
  '.md': FileText,
  '.pdf': FileText,
  // Default
  default: File
};

const formatFileSize = (bytes: number): string => {
  if (bytes === 0) return '0 B';
  const k = 1024;
  const sizes = ['B', 'KB', 'MB', 'GB'];
  const i = Math.floor(Math.log(bytes) / Math.log(k));
  return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
};

const formatDate = (dateString: string): string => {
  return new Date(dateString).toLocaleDateString('en-US', {
    year: 'numeric',
    month: 'short',
    day: 'numeric',
    hour: '2-digit',
    minute: '2-digit'
  });
};

export function ProjectFileExplorer({ project, onClose, onOpenProject }: ProjectFileExplorerProps) {
  const [currentPath, setCurrentPath] = useState<string>('');
  const [fileTree, setFileTree] = useState<FileItem[]>([]);
  const [selectedFile, setSelectedFile] = useState<FileItem | null>(null);
  const [loading, setLoading] = useState(true);

  // Mock file structure based on project type
  const generateMockFileStructure = (project: Project): FileItem[] => {
    const baseStructure: FileItem[] = [
      {
        name: 'music',
        type: 'folder',
        path: '/music',
        children: [
          {
            name: 'track1.wav',
            type: 'file',
            path: '/music/track1.wav',
            size: 10240000,
            modified: project.updated_at,
            extension: '.wav'
          },
          {
            name: 'track2.mp3',
            type: 'file',
            path: '/music/track2.mp3',
            size: 5120000,
            modified: project.updated_at,
            extension: '.mp3'
          },
          {
            name: 'background_music.wav',
            type: 'file',
            path: '/music/background_music.wav',
            size: 8000000,
            modified: project.updated_at,
            extension: '.wav'
          }
        ]
      },
      {
        name: 'video',
        type: 'folder',
        path: '/video',
        children: [
          {
            name: 'final_video.mp4',
            type: 'file',
            path: '/video/final_video.mp4',
            size: 50000000,
            modified: project.updated_at,
            extension: '.mp4'
          },
          {
            name: 'draft_video.mp4',
            type: 'file',
            path: '/video/draft_video.mp4',
            size: 25000000,
            modified: project.updated_at,
            extension: '.mp4'
          },
          {
            name: 'preview.mp4',
            type: 'file',
            path: '/video/preview.mp4',
            size: 12000000,
            modified: project.updated_at,
            extension: '.mp4'
          }
        ]
      },
      {
        name: 'image',
        type: 'folder',
        path: '/image',
        children: [
          {
            name: 'thumbnail.png',
            type: 'file',
            path: '/image/thumbnail.png',
            size: 500000,
            modified: project.updated_at,
            extension: '.png'
          },
          {
            name: 'cover.jpg',
            type: 'file',
            path: '/image/cover.jpg',
            size: 800000,
            modified: project.updated_at,
            extension: '.jpg'
          },
          {
            name: 'background.jpg',
            type: 'file',
            path: '/image/background.jpg',
            size: 1200000,
            modified: project.updated_at,
            extension: '.jpg'
          },
          {
            name: 'logo.png',
            type: 'file',
            path: '/image/logo.png',
            size: 150000,
            modified: project.updated_at,
            extension: '.png'
          }
        ]
      },
      {
        name: 'audio',
        type: 'folder',
        path: '/audio',
        children: [
          {
            name: 'voiceover.wav',
            type: 'file',
            path: '/audio/voiceover.wav',
            size: 2000000,
            modified: project.updated_at,
            extension: '.wav'
          },
          {
            name: 'sound_effects.wav',
            type: 'file',
            path: '/audio/sound_effects.wav',
            size: 800000,
            modified: project.updated_at,
            extension: '.wav'
          }
        ]
      }
    ];

    return baseStructure;
  };

  useEffect(() => {
    // Simulate loading
    setTimeout(() => {
      setFileTree(generateMockFileStructure(project));
      setLoading(false);
    }, 500);
  }, [project]);

  const getFileIcon = (file: FileItem) => {
    if (file.type === 'folder') return Folder;
    const extension = file.extension?.toLowerCase();
    return FILE_ICONS[extension as keyof typeof FILE_ICONS] || FILE_ICONS.default;
  };

  const handleFileClick = (file: FileItem) => {
    if (file.type === 'folder') {
      setCurrentPath(file.path);
    } else {
      setSelectedFile(file);
    }
  };

  const handleBack = () => {
    if (currentPath) {
      const parentPath = currentPath.split('/').slice(0, -1).join('/') || '';
      setCurrentPath(parentPath);
    }
  };

  const getCurrentFiles = (): FileItem[] => {
    if (!currentPath) return fileTree;
    
    const findFolder = (items: FileItem[], path: string): FileItem | null => {
      for (const item of items) {
        if (item.path === path) return item;
        if (item.children) {
          const found = findFolder(item.children, path);
          if (found) return found;
        }
      }
      return null;
    };

    const folder = findFolder(fileTree, currentPath);
    return folder?.children || [];
  };

  const handleOpenProject = () => {
    onOpenProject(project);
  };

  if (loading) {
    return (
      <div className="h-screen bg-background flex items-center justify-center">
        <div className="text-center">
          <div className="w-8 h-8 border-3 border-primary border-t-transparent rounded-full animate-spin mx-auto mb-4"></div>
          <p className="text-muted-foreground">Loading project files...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="h-screen bg-background flex">
      {/* Sidebar - Project Info */}
      <div className="w-96 border-r bg-card/50 backdrop-blur-sm flex flex-col">
        <div className="p-6 border-b bg-gradient-to-r from-primary/5 to-accent/5">
          <div className="flex items-center justify-between mb-6">
            <Button variant="ghost" size="sm" onClick={onClose} className="hover:bg-primary/10">
              <ArrowLeft className="w-4 h-4 mr-2" />
              Back to Projects
            </Button>
            <Button onClick={handleOpenProject} className="bg-primary hover:bg-primary/90">
              <Play className="w-4 h-4 mr-2" />
              Open Project
            </Button>
          </div>
          <div className="space-y-3">
            <h1 className="text-2xl font-bold text-foreground">{project.name || 'Untitled Project'}</h1>
            <div className="flex items-center gap-2">
              <Badge variant="secondary" className="bg-primary/10 text-primary border-primary/20">
                {project.status}
              </Badge>
              <span className="text-sm text-muted-foreground capitalize">
                {project.type?.replace('-', ' ') || 'Unknown Type'}
              </span>
            </div>
          </div>
        </div>

        <ScrollArea className="flex-1 p-6">
          <div className="space-y-8">
            {/* Project Details */}
            <div className="space-y-4">
              <h3 className="text-lg font-semibold text-foreground flex items-center gap-2">
                <div className="w-2 h-2 bg-primary rounded-full"></div>
                Project Details
              </h3>
              <div className="space-y-3">
                <div className="flex items-center gap-3 p-3 rounded-lg bg-muted/50">
                  <Calendar className="w-4 h-4 text-primary" />
                  <div>
                    <p className="text-sm font-medium">Created</p>
                    <p className="text-xs text-muted-foreground">{formatDate(project.created_at)}</p>
                  </div>
                </div>
                <div className="flex items-center gap-3 p-3 rounded-lg bg-muted/50">
                  <Clock className="w-4 h-4 text-primary" />
                  <div>
                    <p className="text-sm font-medium">Updated</p>
                    <p className="text-xs text-muted-foreground">{formatDate(project.updated_at)}</p>
                  </div>
                </div>
                <div className="flex items-center gap-3 p-3 rounded-lg bg-muted/50">
                  <HardDrive className="w-4 h-4 text-primary" />
                  <div>
                    <p className="text-sm font-medium">Project ID</p>
                    <p className="text-xs text-muted-foreground font-mono">{project.id.slice(0, 8)}...</p>
                  </div>
                </div>
              </div>
            </div>

            <Separator className="bg-border/50" />

            {/* File Statistics */}
            <div className="space-y-4">
              <h3 className="text-lg font-semibold text-foreground flex items-center gap-2">
                <div className="w-2 h-2 bg-accent rounded-full"></div>
                File Statistics
              </h3>
              <div className="grid grid-cols-2 gap-3">
                <div className="p-3 rounded-lg bg-gradient-to-br from-primary/10 to-primary/5 border border-primary/20">
                  <p className="text-2xl font-bold text-primary">11</p>
                  <p className="text-xs text-muted-foreground">Total Files</p>
                </div>
                <div className="p-3 rounded-lg bg-gradient-to-br from-accent/10 to-accent/5 border border-accent/20">
                  <p className="text-2xl font-bold text-accent">87.5 MB</p>
                  <p className="text-xs text-muted-foreground">Total Size</p>
                </div>
                <div className="p-3 rounded-lg bg-gradient-to-br from-green-500/10 to-green-500/5 border border-green-500/20">
                  <p className="text-2xl font-bold text-green-600">3</p>
                  <p className="text-xs text-muted-foreground">Videos</p>
                </div>
                <div className="p-3 rounded-lg bg-gradient-to-br from-blue-500/10 to-blue-500/5 border border-blue-500/20">
                  <p className="text-2xl font-bold text-blue-600">4</p>
                  <p className="text-xs text-muted-foreground">Images</p>
                </div>
                <div className="p-3 rounded-lg bg-gradient-to-br from-purple-500/10 to-purple-500/5 border border-purple-500/20">
                  <p className="text-2xl font-bold text-purple-600">5</p>
                  <p className="text-xs text-muted-foreground">Audio</p>
                </div>
                <div className="p-3 rounded-lg bg-gradient-to-br from-orange-500/10 to-orange-500/5 border border-orange-500/20">
                  <p className="text-2xl font-bold text-orange-600">4</p>
                  <p className="text-xs text-muted-foreground">Folders</p>
                </div>
              </div>
            </div>

            <Separator className="bg-border/50" />

            {/* Selected File Info */}
            {selectedFile && (
              <div className="space-y-4">
                <h3 className="text-lg font-semibold text-foreground flex items-center gap-2">
                  <div className="w-2 h-2 bg-green-500 rounded-full"></div>
                  File Details
                </h3>
                <div className="p-4 rounded-lg bg-muted/50 border border-border/50">
                  <div className="space-y-3">
                    <div>
                      <p className="text-sm font-medium text-foreground">Name</p>
                      <p className="text-sm text-muted-foreground font-mono">{selectedFile.name}</p>
                    </div>
                    <div>
                      <p className="text-sm font-medium text-foreground">Path</p>
                      <p className="text-sm text-muted-foreground font-mono">{selectedFile.path}</p>
                    </div>
                    {selectedFile.size && (
                      <div>
                        <p className="text-sm font-medium text-foreground">Size</p>
                        <p className="text-sm text-muted-foreground">{formatFileSize(selectedFile.size)}</p>
                      </div>
                    )}
                    {selectedFile.modified && (
                      <div>
                        <p className="text-sm font-medium text-foreground">Modified</p>
                        <p className="text-sm text-muted-foreground">{formatDate(selectedFile.modified)}</p>
                      </div>
                    )}
                  </div>
                </div>
              </div>
            )}
          </div>
        </ScrollArea>
      </div>

      {/* Main Content - File Explorer */}
      <div className="flex-1 flex flex-col bg-background">
        {/* Header */}
        <div className="p-6 border-b bg-gradient-to-r from-background to-muted/20">
          <div className="flex items-center gap-3 mb-3">
            {currentPath && (
              <Button variant="outline" size="sm" onClick={handleBack} className="hover:bg-primary/10">
                <ArrowLeft className="w-4 h-4 mr-2" />
                Back
              </Button>
            )}
            <div className="flex items-center gap-2">
              <Folder className="w-5 h-5 text-primary" />
              <h2 className="text-xl font-semibold text-foreground">
                {currentPath ? currentPath.split('/').pop() : 'Project Files'}
              </h2>
            </div>
          </div>
          <div className="flex items-center gap-2 text-sm text-muted-foreground">
            <div className="w-1 h-1 bg-muted-foreground rounded-full"></div>
            <span>{currentPath || 'Root directory'}</span>
            <span>•</span>
            <span>{getCurrentFiles().length} items</span>
          </div>
        </div>

        {/* File List */}
        <ScrollArea className="flex-1 p-6">
          <div className="space-y-3">
            {getCurrentFiles().map((file, index) => {
              const IconComponent = getFileIcon(file);
              const isSelected = selectedFile?.path === file.path;
              
              return (
                <Card
                  key={index}
                  className={`cursor-pointer transition-all duration-200 hover:shadow-md ${
                    isSelected 
                      ? 'ring-2 ring-primary bg-primary/5 border-primary/20' 
                      : 'hover:bg-muted/30 border-border/50'
                  }`}
                  onClick={() => handleFileClick(file)}
                >
                  <CardContent className="p-4">
                    <div className="flex items-center gap-4">
                      <div className={`p-2 rounded-lg ${
                        file.type === 'folder' 
                          ? 'bg-primary/10 text-primary' 
                          : 'bg-muted text-muted-foreground'
                      }`}>
                        <IconComponent className="w-5 h-5" />
                      </div>
                      <div className="flex-1 min-w-0">
                        <p className="font-medium text-foreground truncate">{file.name}</p>
                        <div className="flex items-center gap-4 text-sm text-muted-foreground mt-1">
                          <span className="capitalize font-medium">{file.type}</span>
                          {file.size && (
                            <span className="px-2 py-1 bg-muted rounded text-xs">
                              {formatFileSize(file.size)}
                            </span>
                          )}
                          {file.modified && (
                            <span className="text-xs">
                              {formatDate(file.modified)}
                            </span>
                          )}
                        </div>
                      </div>
                      {file.type === 'file' && (
                        <div className="flex gap-1 opacity-0 group-hover:opacity-100 transition-opacity">
                          <Button 
                            variant="ghost" 
                            size="sm" 
                            className="h-8 w-8 p-0 hover:bg-primary/10"
                            onClick={(e) => {
                              e.stopPropagation();
                              // Handle view action
                            }}
                          >
                            <Eye className="w-4 h-4" />
                          </Button>
                          <Button 
                            variant="ghost" 
                            size="sm" 
                            className="h-8 w-8 p-0 hover:bg-primary/10"
                            onClick={(e) => {
                              e.stopPropagation();
                              // Handle download action
                            }}
                          >
                            <Download className="w-4 h-4" />
                          </Button>
                        </div>
                      )}
                    </div>
                  </CardContent>
                </Card>
              );
            })}
          </div>
        </ScrollArea>
      </div>
    </div>
  );
}
