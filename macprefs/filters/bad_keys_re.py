from typing import Final
import re

__all__ = ('BAD_KEYS_RE',)

# spell-checker: disable  # noqa: ERA001
BAD_KEYS_RE: Final[re.Pattern[str]] = re.compile(r'^(' + '|'.join({
    '(?:Favorites|Recents|SkinTones)' +
    re.escape(':com.apple.CharacterPicker.DefaultDataStorage'), '(?:NSWindow|MASPreferences) Frame',
    'CKPerBootTasks', 'CKStartupTime', 'DidShowFDEWarning', 'GEOUsageSessionIDGenerationTime',
    'NSNavLastRootDirectory', 'NSNavPanelExpandedSizeFor(?:Open|Save)Mode', 'NSOutlineView Items',
    'NSSplitView [^ ]+ Expanded Position', 'NSSplitView Subview Frames',
    'NSStatusItem Preferred Position', 'NSTableView (?:Hidden )?Columns',
    'NSTableView Sort Ordering', 'OSAStandardAdditions ChooseApplication Bounds',
    'QtUi.MainWin(?:Geometry|State|Pos|Size)', 'recentFilesList', 'SPSelfBeaconUUIDKey',
    'SUEnableAutomaticChecks', 'SULastCheckTime', 'TSAICloudAuthorNameKey',
    'TSKRemote(?:Defaults|Strings)ETag', r'NSToolbar Configuration',
    r'QuickLookPreview_[A-Z0-9-\.]+',
    re.escape('last-messagetrace-stamp'),
    re.escape('Qt Factory Cache')
}) + r')\b')
