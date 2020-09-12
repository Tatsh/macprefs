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
    'OSAStandardAdditions ChooseApplication Bounds',
    'QtUi.MainWin(Geometry|State|Pos|Size)',
    r'QuickLookPreview_[A-Z0-9-\.]+',
    'SPSelfBeaconUUIDKey',
    'SUEnableAutomaticChecks',
    'SULastCheckTime',
    'recentFilesList',
    re.escape('Qt Factory Cache'),
    re.escape('last-messagetrace-stamp'),
}) + r')\b')
