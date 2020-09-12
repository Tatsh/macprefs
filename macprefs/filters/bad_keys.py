__all__ = ('BAD_KEYS', )
# spell-checker: disable
BAD_KEYS = {
    '-globalDomain': {
        'AKLastEmailListRequestDateKey',
        'AppleInterfaceStyle',
        'NSLinguisticDataAssetsRequestTime',
        'NSNavRecentPlaces',
        'NavPanelFileListModeForPanelerMode',
        r're:^AKLast',
        # Devices get added to global domain with -string 1
        r're:^(Amazon|Apple|Canon|Generic|HP|HuiJia) '
    },
    'SSHKeychain': {'Authentication Socket Path'},
    'com.apple.accountsd': {'AuthenticationPluginCache', 'LastSystemVersion'},
    'com.apple.ServicesMenu.Services': {'NSServices'},
    'com.apple.dt.Xcode': {
        'DVTTextCompletionRecentCompletions', 'DeveloperAccountForProject',
        'IDESourceControlKnownSSHHostsDefaultsKey', 're:lastRecordedRefresh$'
    },
    'com.apple.TelephonyUtilities': {'registeredProviders'},
    'org.videolan.vlc': {r're:^recentlyPlayed'},
    'com.apple.amp.mediasharingd': {r're:.*\-id$'},
    'com.apple.AddressBook':
    {'ABDefaultSourceID', 'ABMetaDataChangeCount', 'ABMetadataLastOilChange'},
    'com.apple.appstored': {
        'ArcadePayoutDeviceID', 'ArcadeDeviceID', 'LastUpdatesCheck',
        r're:^TargetDate', r're:^Arcade.*Date$'
    },
    'com.apple.assistant.backedup': {'Cloud Sync User ID'},
    'com.apple.AppStore': {
        r're:^lastBootstrap', 'JE.MediaAPIToken',
        'MetricsSamplingLotteryWindowStart_pageRender'
    },
    'com.apple.AppleMediaServices': {'AMSMetricsTimingWindowStartTime'},
    'com.apple.bird': {r're:^icloud\-drive\.account\-migration\-status'},
    'com.apple.calculateframework': {'currencyCache'},
    'com.apple.cloudd':
    {'com.apple.private.cloudkit.shouldUseGeneratedDeviceID'},
    'com.apple.cloudpaird':
    {'PreviousToken', 'UploadedHSA2KeysForLocalDevice'},
    'com.apple.commerce': {
        'LastUpdateNotificationOSMajorVersion', r'^re:PrivacyConsent\:',
        'AvailableUpdatesAtLastNotification'
    },
    'com.apple.CallHistorySyncHelper':
    {'CallHistoryDeviceCount', 'ChangeToken', r're:.*Date$', r're:^/Users/'},
    'com.apple.Console': {'ConsoleSearch'},
    'com.apple.configurator': {'Storefront'},
    'com.apple.configurator.ui': {'LastAcceptedConfiguratorLicenseVersion'},
    'com.apple.configurator.ui.commerce':
    {'re:^PrimaryAccount', 're:^Storefront'},
    'com.apple.coreservices.useractivityd':
    {'re:k(?:Local|Remote)PasteboardBlobName'},
    'com.apple.dock': {'mod-count'},
    'com.apple.driver.AppleBluetoothMultitouch.trackpad': {'version'},
    'com.apple.dt.Instruments': {
        'DTWirelessUniqueShortTypeLocationID', 'DTDKLastLSRegisterHashes',
        'RecentTemplates.array'
    },
    'com.apple.FaceTime': {'AccountSortOrder'},
    'com.apple.finder': {
        'CopyProgressWindowLocation', 'EmptyTrashProgressWindowLocation',
        'FXConnectToBounds', 'FXConnectToLastURL',
        'FXPreferencesWindow.Location', 'GoToField', 'GoToFieldHistory',
        'MountProgressWindowLocation', 'RecentMoveAndCopyDestinations',
        'TagsCloudSerialNumber'
    },
    'com.apple.iBooksX': {
        r're:^BKBookViewerPlugInInstanceDescriptor',
        r're:^MZBookKeeper\.LastDsid'
    },
    'com.apple.iBooksX.commerce': {'Storefront'},
    'com.apple.iCal': {
        'AccountDisplayOrder', 'CalAgentNS_Preference_DefaultReminderCalendar',
        'LastCheckForIgnoredPseudoEvents', 'last selected calendar list item',
        'first shown minute of day', 'iCal version', 'lastViewsTimeZone',
        'CalFirstVisibleDate'
    },
    'com.apple.iChat': {
        'AccountSortOrder',
        'ChatWindowControllerUnifiedFrame',
        'LastFailedMessageIMDNotificationPostedDate',
        'KeepMessagesVersionID',
        'LastIMDNotificationPostedDate',
        'UnifiedChatWindowControllerSelectionGUIDSet',
        r're:^messageTracer',
    },
    'com.apple.iTunes':
    {'Store Apple ID', 'Store DSID', 'WirelessBuddyID', 'storefront'},
    'com.apple.iWork.Numbers': {
        'TSAICloudAuthorNameKey', 'TSKRemoteStringsETag',
        'TSURemoteDefaultsETag'
    },
    'com.apple.iWork.Pages': {
        'TSAICloudAuthorNameKey', 're:^TSAICloudDocumentPreferencePrefix',
        'TSKRemoteStringsETag', 'TSURemoteDefaultsETag'
    },
    'com.apple.internetconnect': {'ServiceID'},
    'com.apple.iphonesimulator': {'CurrentDeviceUDID'},
    'com.apple.keychainaccess': {'Last Selected Keychain'},
    'com.apple.logic10': {r're:^DefaultDir', 'lastSelectedKeyCommandsPath'},
    'com.apple.languageassetd': {'LastSystemVersion'},
    'com.apple.mail': {
        'AccountInfoLastSelectedAccountId', 'AccountOrdering',
        'CurrentTransferMailboxURLString', 'MailSections', 'LastAttachedDir',
        'LastMessageTracingDate', 'LastChatSyncTime', 'SignaturesSelected',
        'MailUpgraderPrePersistenceVersion', 'MailUpgraderVersion',
        'MailVisibleSections', 'NumberOfMessagesMarkedAsJunk',
        'NumberOfMessagesMarkedAsNotJunk', 'SignatureSelectionMethods',
        'com.apple.mail.searchableIndex.lastProcessedAttachmentIDKey'
    },
    'com.apple.PhotoBooth': {'LibraryBookmark'},
    'com.apple.Preferences': {r're:^UserDictionary'},
    'com.apple.print.PrinterProxy':
    {'IK_Scanner_downloadURL', 'IK_Scanner_selectedTag'},
    'com.apple.searchd': {r're:^engagementCount'},
    'com.apple.Spotlight': {
        'GEOUsageSessionID', 'startTime', 'version',
        'engagementCount-com.apple.Spotlight', r're:.*Count$'
    },
    'com.apple.SystemProfiler': {'CPU Names', r're:^SPLast'},
    'com.apple.Terminal': {'CommandHistory'},
    'com.apple.Safari.SafeBrowsing': {r're:.*Date$'},
    'com.apple.sms': {'hasBeenApprovedForSMSRelay'},
    'com.apple.stocks': {'lastModified'},
    'com.apple.systempreferences':
    {'ThirdPartyCount', 'com.apple.SecurityPref.Privacy.LastSourceSelected'},
    'com.apple.talagent': {'LastKeyChange'},
    'cx.c3.theunarchiver': {'_sid', 'DM_SID'},
    'com.parallels.Parallels Desktop': {
        r're:{[0-9a-f]{8}\-[0-9a-f]{4}]\-[0-9a-f]{4}\-[0-9a-f]{4}\-'
        r'[0-9a-f]{12}\}\.', r're:^Guest OS Sources'
    },
    'com.monosnap.monosnap':
    {r're:^[0-9a-f]{24}\&0$', 'last online time', 'mono_pref_time'},
    'com.googlecode.iterm2': {
        'NoSyncInstallationId', r're:^NeverWarnAboutShortLivedSessions',
        'Default Bookmark Guid'
    },
    'com.etresoft.EtreCheckMAS': {'asset'},
    'com.etresoft.EtreCheck4': {'asset'},
    'org.quassel-irc.quasselclient': {
        r're:^CoreAccounts\.\d+\.General\.JumpKeyMap',
        r're:^CoreAccounts\.\d+\.Password'
    },
    'ThnkDev.QuickRes': {'DM_SID', 'DevMateLaunchCount', 'matchedIds'},
    'ch.tripmode.TripMode': {r're:^ActivationOverrides?', 'Networks'},
    'com.apple.ActivityMonitor': {'cacheTableSortDescriptors'},
}
