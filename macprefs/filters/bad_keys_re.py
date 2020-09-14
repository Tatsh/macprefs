import re

__all__ = ('BAD_KEYS_RE', )

# spell-checker: disable
BAD_KEYS_RE = re.compile(r'^(' + '|'.join({
    '(?:Favorites|Recents|SkinTones)' +
    re.escape(':com.apple.CharacterPicker.DefaultDataStorage'),
    '(?:NSWindow|MASPreferences) Frame',
    'GEOUsageSessionIDGenerationTime',
    'NSNavLastRootDirectory',
    'NSNavPanelExpandedSizeFor(?:Open|Save)Mode',
    'NSOutlineView Items',
    'NSSplitView Subview Frames',
    'NSSplitView [^ ]+ Expanded Position',
    'NSStatusItem Preferred Position',
    'NSTableView (?:Hidden )?Columns',
    'NSTableView Sort Ordering',
    'OSAStandardAdditions ChooseApplication Bounds',
    'QtUi.MainWin(Geometry|State|Pos|Size)',
    'SPSelfBeaconUUIDKey',
    'SUEnableAutomaticChecks',
    'SULastCheckTime',
    'recentFilesList',
    r'QuickLookPreview_[A-Z0-9-\.]+',
    re.escape('Qt Factory Cache'),
    re.escape('last-messagetrace-stamp'),
}) + r')\b')
