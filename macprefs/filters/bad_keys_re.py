from __future__ import annotations

__all__ = ('BAD_KEYS_RE',)

# spell-checker: disable
BAD_KEYS_RE = '^(' + '|'.join({
    '(?:Favorites|Recents|SkinTones):com.apple.CharacterPicker.DefaultDataStorage',
    '(?:NSWindow|MASPreferences) Frame', 'CKPerBootTasks', 'CKStartupTime', 'DidShowFDEWarning',
    'GEOUsageSessionIDGenerationTime', 'last-messagetrace-stamp', 'LastRunAppBundlePath',
    'MSAppCenter.*', 'MSInstallId', 'NSNavLastRootDirectory',
    'NSNavPanelExpandedSizeFor(?:Open|Save)Mode', 'NSNavRecentPlaces', 'NSOutlineView Items',
    'NSSplitView [^ ]+ Expanded Position', 'NSSplitView Subview Frames',
    'NSStatusItem Preferred Position', 'NSTableView (?:Hidden )?Columns',
    'NSTableView Sort Ordering', 'NSToolbar Configuration',
    'OSAStandardAdditions ChooseApplication Bounds', 'Qt Factory Cache',
    'QtUi.MainWin(?:Geometry|State|Pos|Size)', 'recentFilesList', 'SPSelfBeaconUUIDKey',
    'SUEnableAutomaticChecks', 'SULastCheckTime', 'TSAICloudAuthorNameKey',
    'TSKRemote(?:Defaults|Strings)ETag', r'QuickLookPreview_[A-Z0-9-\.]+'
}) + r')\b'
