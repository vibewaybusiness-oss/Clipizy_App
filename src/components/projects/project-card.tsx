import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import {
  Music,
  Video,
  Film,
  Calendar,
  Clock,
  Check
} from 'lucide-react';
import { Project } from '@/lib/api/projects';

interface ProjectCardProps {
  project: Project;
  onDelete: (projectId: string) => void;
  onPlay?: (project: Project) => void;
  viewMode?: 'grid' | 'list';
  isSelected?: boolean;
  onSelect?: (projectId: string, selected: boolean) => void;
  selectionMode?: boolean;
}

const PROJECT_ICONS = {
  'music-clip': Music,
  'video-clip': Video,
  'video-edit': Video, // Map video-edit to Video icon
  'audio-edit': Music, // Map audio-edit to Music icon
  'image-edit': Film, // Map image-edit to Film icon
  'short-clip': Film,
  'custom': Music, // Default to Music icon for custom types
  'undefined': Music, // Default to Music icon for undefined types
};

const STATUS_COLORS = {
  created: 'bg-gray-100 text-gray-800',
  uploading: 'bg-blue-100 text-blue-800',
  analyzing: 'bg-yellow-100 text-yellow-800',
  queued: 'bg-purple-100 text-purple-800',
  processing: 'bg-blue-100 text-blue-800',
  completed: 'bg-green-100 text-green-800',
  failed: 'bg-red-100 text-red-800',
  cancelled: 'bg-gray-100 text-gray-800',
  draft: 'bg-gray-100 text-gray-800',
  archived: 'bg-gray-100 text-gray-800',
};

export function ProjectCard({
  project,
  onDelete,
  onPlay,
  viewMode = 'grid',
  isSelected = false,
  onSelect,
  selectionMode = false
}: ProjectCardProps) {
  const IconComponent = PROJECT_ICONS[project.type] || PROJECT_ICONS['undefined'] || Music;

  const formatDate = (dateString: string) => {
    return new Date(dateString).toLocaleDateString('en-US', {
      year: 'numeric',
      month: 'short',
      day: 'numeric',
    });
  };

  const handlePlay = () => {
    onPlay?.(project);
  };

  const handleSelect = (e: React.MouseEvent) => {
    if (selectionMode && onSelect) {
      e.stopPropagation();
      onSelect(project.id, !isSelected);
    }
  };

  const handleCardClick = (e: React.MouseEvent) => {
    if (selectionMode && onSelect) {
      e.stopPropagation();
      onSelect(project.id, !isSelected);
    } else if (!selectionMode) {
      // Open the project in dashboard/create section
      onPlay?.(project);
    }
  };

  if (viewMode === 'list') {
    return (
      <Card 
        className={`group hover:shadow-md hover:bg-muted/30 transition-all duration-200 cursor-pointer border-border/50 hover:border-border ${
          isSelected ? 'ring-2 ring-primary bg-primary/5' : ''
        }`}
        onClick={handleCardClick}
      >
        <CardContent className="p-6">
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-4 flex-1">
              {selectionMode && (
                <div 
                  className={`w-5 h-5 rounded border-2 flex items-center justify-center flex-shrink-0 ${
                    isSelected ? 'bg-primary border-primary text-white' : 'border-gray-300'
                  }`}
                  onClick={handleSelect}
                >
                  {isSelected && <Check className="w-3 h-3" />}
                </div>
              )}
              <div className="p-3 bg-muted rounded-lg flex-shrink-0">
                <IconComponent className="w-5 h-5 text-muted-foreground" />
              </div>
              <div className="flex-1 min-w-0">
                <h3 className="font-semibold text-lg text-foreground truncate">{project.name || 'Untitled Project'}</h3>
                <div className="flex items-center space-x-3 mt-1">
                  <p className="text-sm text-muted-foreground capitalize">
                    {project.type?.replace('-', ' ') || 'Music Clip'}
                  </p>
                  <span className="text-muted-foreground/60">•</span>
                  <p className="text-sm text-muted-foreground/80">
                    Created {formatDate(project.created_at)}
                  </p>
                </div>
              </div>
            </div>

            <div className="flex items-center space-x-4 flex-shrink-0">
              <Badge className={`${STATUS_COLORS[project.status]} font-medium`}>
                {project.status}
              </Badge>
            </div>
          </div>
        </CardContent>
      </Card>
    );
  }

  return (
    <Card 
      className={`group hover:shadow-lg hover:bg-muted/30 transition-all duration-200 cursor-pointer border-border/50 hover:border-border ${
        isSelected ? 'ring-2 ring-primary bg-primary/5' : ''
      }`}
      onClick={handleCardClick}
    >
      {(project.thumbnail_url || project.preview_url) && (
        <div className="relative w-full h-48 overflow-hidden rounded-t-lg bg-muted">
          <img 
            src={project.thumbnail_url || project.preview_url} 
            alt={project.name || 'Project preview'} 
            className="w-full h-full object-cover"
            onError={(e) => {
              (e.target as HTMLImageElement).style.display = 'none';
            }}
          />
          {project.status === 'completed' && (
            <div className="absolute top-2 right-2">
              <Badge className="bg-green-500 text-white">Completed</Badge>
            </div>
          )}
        </div>
      )}
      <CardHeader className="pb-4">
        <div className="flex items-start justify-between">
          <div className="flex items-center space-x-3 flex-1 min-w-0">
            {selectionMode && (
              <div 
                className={`w-5 h-5 rounded border-2 flex items-center justify-center flex-shrink-0 ${
                  isSelected ? 'bg-primary border-primary text-white' : 'border-gray-300'
                }`}
                onClick={handleSelect}
              >
                {isSelected && <Check className="w-3 h-3" />}
              </div>
            )}
            <div className="p-3 bg-muted rounded-lg flex-shrink-0">
              <IconComponent className="w-5 h-5 text-muted-foreground" />
            </div>
            <div className="flex-1 min-w-0">
              <CardTitle className="text-lg font-semibold text-foreground truncate">{project.name || 'Untitled Project'}</CardTitle>
              <CardDescription className="capitalize text-muted-foreground mt-1">
                {project.type?.replace('-', ' ') || 'Music Clip'}
              </CardDescription>
            </div>
          </div>
        </div>
      </CardHeader>
      <CardContent className="space-y-4 pt-0">
        <div className="flex items-center justify-between">
          <Badge className={`${STATUS_COLORS[project.status]} font-medium`}>
            {project.status}
          </Badge>
        </div>

        <div className="space-y-3 text-sm text-muted-foreground">
          <div className="flex items-center">
            <Calendar className="w-4 h-4 mr-3 text-muted-foreground/60" />
            <span>Created {formatDate(project.created_at)}</span>
          </div>
          <div className="flex items-center">
            <Clock className="w-4 h-4 mr-3 text-muted-foreground/60" />
            <span>Updated {formatDate(project.updated_at)}</span>
          </div>
          {project.media_counts && (project.media_counts.tracks > 0 || project.media_counts.videos > 0 || project.media_counts.images > 0) && (
            <div className="flex items-center gap-3 pt-2 border-t border-border/50">
              {project.media_counts.tracks > 0 && (
                <span className="text-xs text-muted-foreground">
                  <Music className="w-3 h-3 inline mr-1" />
                  {project.media_counts.tracks}
                </span>
              )}
              {project.media_counts.videos > 0 && (
                <span className="text-xs text-muted-foreground">
                  <Video className="w-3 h-3 inline mr-1" />
                  {project.media_counts.videos}
                </span>
              )}
              {project.media_counts.images > 0 && (
                <span className="text-xs text-muted-foreground">
                  <Film className="w-3 h-3 inline mr-1" />
                  {project.media_counts.images}
                </span>
              )}
            </div>
          )}
        </div>

      </CardContent>
    </Card>
  );
}
