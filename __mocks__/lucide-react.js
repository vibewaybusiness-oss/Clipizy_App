const React = require('react');

// Mock for lucide-react icons
const createMockIcon = (name) => {
  return function MockIcon(props) {
    return React.createElement('svg', { 
      ...props, 
      'data-testid': `icon-${name}`,
      'data-lucide': name 
    });
  };
};

// Mock all the icons that might be used
const icons = [
  'ArrowRight', 'ArrowLeft', 'ArrowUp', 'ArrowDown',
  'Check', 'X', 'Plus', 'Minus', 'Edit', 'Trash', 'Save',
  'User', 'Settings', 'Home', 'Search', 'Menu', 'Close',
  'Play', 'Pause', 'Stop', 'Volume', 'VolumeX', 'Volume2',
  'Download', 'Upload', 'File', 'Folder', 'Image', 'Video',
  'Music', 'Heart', 'Star', 'Share', 'Copy', 'ExternalLink',
  'ChevronRight', 'ChevronLeft', 'ChevronUp', 'ChevronDown',
  'Calendar', 'Clock', 'Mail', 'Phone', 'MapPin', 'Globe',
  'Lock', 'Unlock', 'Eye', 'EyeOff', 'Shield', 'AlertCircle',
  'Info', 'Warning', 'Error', 'Success', 'Loading', 'Refresh'
];

const mockIcons = {};
icons.forEach(iconName => {
  mockIcons[iconName] = createMockIcon(iconName);
});

module.exports = {
  ...mockIcons,
  // Export individual icons as well
  createElement: React.createElement,
};
