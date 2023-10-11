from typing import Final

__all__ = ('BAD_KEYS',)

# spell-checker: disable  # noqa: ERA001
BAD_KEYS: Final[dict[str, set[str]]] = {

    # Devices get added to global domain with -string 1
    '-globalDomain': {
        'AKLastEmailListRequestDateKey', 'AppleInterfaceStyle', 'AppleLanguagesDidMigrate',
        'AppleLanguagesSchemaVersion', 'NSNavRecentPlaces', 'NavPanelFileListModeForPanelerMode',
        're:^NSLinguisticDataAssets.*', r're:^(Amazon|Apple|Canon|Generic|HP|HuiJia) ',
        r're:^AKLast'
    },
    'SSHKeychain': {'Authentication Socket Path'},
    'ThnkDev.QuickRes': {'DM_SID', 'DevMateLaunchCount', 'matchedIds', 'version'},
    'ch.tripmode.TripMode': {'Networks', r're:^ActivationOverrides?'},
    'com.apple.ActivityMonitor': {'cacheTableSortDescriptors'},
    'com.apple.AdPlatforms': {
        'AppStorePAAvailable', 're:^Config.*', 'LatestPAVersion',
        'acknowledgedPersonalizedAdsVersion'
    },
    'com.apple.AddressBook': {
        'ABDefaultSourceID', 'ABMetaDataChangeCount', 'ABMetadataLastOilChange',
        're:^ABCleanWindowController.*', 'ABVersion'
    },
    'com.apple.AppStore': {
        'ASAcknowledgedOnboardingVersion', 'JE.MediaAPIToken',
        'MetricsSamplingLotteryWindowStart_pageRender', r're:^lastBootstrap'
    },
    'com.apple.AppleMediaServices': {
        'AMSMetricsTimingWindowStartTime', 'AMSDidSetUpServerDataCache', 'AMSFPCertExpiration',
        're:^AMSIncludeFull.*', 'AMSJSVersionMap', 'AMSDeviceBiometricsState'
    },
    'com.apple.AppleMultitouchMouse': {'version'},
    'com.apple.AppleMultitouchTrackpad': {'version'},
    'com.apple.CallHistorySyncHelper': {
        'CallHistoryDeviceCount', 'ChangeToken', r're:.*Date$', r're:^/Users/'
    },
    'com.apple.CharacterPicker': {'version'},
    'com.apple.CloudKit': {'AccountInfoValidationCounter'},
    'com.apple.Console': {'ConsoleSearch'},
    'com.apple.DictionaryServices': {'DCSPreferenceVersion'},
    'com.apple.EmojiPreferences': {'EMFDefaultsKey'},
    'com.apple.FaceTime': {'AccountSortOrder'},
    'com.apple.FontRegistry.user': {'LastUpdated', 'Version'},
    'com.apple.GEO': {'DefaultsSanitizedVersion'},
    'com.apple.HearingAids': {'HearingFeatureUsagePreference'},
    'com.apple.Maps': {'ShareETABlocklistMigration2022'},
    'com.apple.MobileSMS': {'CatalystPreferenceMigrationVersion'},
    'com.apple.PhotoBooth': {'LibraryBookmark'},
    'com.apple.Preferences': {r're:^UserDictionary'},
    'com.apple.Safari': {'ResetCloudHistory'},
    'com.apple.Safari.PasswordBreachAgent': {'WBSPasswordBreachConfigurationBagLastUpdate'},
    'com.apple.Safari.SafeBrowsing': {r're:.*Date$', 'HasMigratedSafeBrowsingEnabledDefaults'},
    'com.apple.Safari.SandboxBroker': {
        'DidMigrateDownloadFolderToSandbox', 'DidMigrateResourcesToSandbox'
    },
    'com.apple.SafariBookmarksSyncAgent': {
        'CloudBookmarksSupplementalClientIdentifier',
        'NewestLaunchedSafariBookmarksSyncAgentVersion'
    },
    'com.apple.SafariServices': {'SearchProviderIdentifierMigratedToSystemPreference'},
    'com.apple.ServicesMenu.Services': {'NSServices'},
    'com.apple.SetupAssistant': {
        'MiniBuddyLaunchReason', 'MiniBuddyLaunchedPostMigration', 'PreviousBuildVersion',
        'PreviousSystemVersion'
    },
    'com.apple.SpeakSelection': {'re:^TTS.*Cache.*'},
    'com.apple.Spotlight': {
        'GEOUsageSessionID', 'engagementCount-com.apple.Spotlight', 'startTime', 'version',
        r're:.*Count$'
    },
    'com.apple.SystemProfiler': {'CPU Names', 'PrefsVersion', r're:^SPLast'},
    'com.apple.TelephonyUtilities': {
        'CachedVCCaps', 'GondolaLastAccountsChangedState', 'kLastIDSFirewallVersionDefaultsKey',
        'registeredProviders', 'registeredProvidersVersion'
    },
    'com.apple.Terminal': {
        'CommandHistory', 'ProfileCurrentVersion', 're:^TTAppPreferences .*',
        're:^NSWindowTabbingShoudShowTabBarKey.*', 'DefaultProfilesVersion'
    },
    'com.apple.TextInputMenuAgent': {'re:^NSStatusItem .*'},
    'com.apple.WindowManager': {'LastDailyHeartbeatDateString'},
    'com.apple.accounts.suggestions': {'InitialLocalMigration', 'LocalDeviceID'},
    'com.apple.accountsd': {'AuthenticationPluginCache', 'LastSystemVersion'},
    'com.apple.amp.mediasharingd': {r're:.*\-id$'},
    'com.apple.appleaccountd': {'lastCloudSyncTimestampKey'},
    'com.apple.appstored': {
        'ArcadeDeviceGUID', 'ArcadeDeviceID', 'ArcadePayoutDeviceID', 'ArcadeSubscriptionState',
        'CurrentUpdateSource', 'LastUpdatesCheck', 'LastWeeklyAnalyticsPostDate', 're:^LastOS.*',
        'WelcomeNotificationLastAppStoreConnectionProductVersion', r're:^.*Date$', 're:^TargetDate'
    },
    'com.apple.assistant': {'re:^.* date$', 're:^.*_experiment$'},
    'com.apple.assistant.backedup': {'Cloud Sync Enabled Modification Date', 'Cloud Sync User ID'},
    'com.apple.backgroundtaskmanagement.agent': {'ManagedNotificationMuzzleExpirationDate'},
    'com.apple.bird': {r're:^icloud-drive\.account-migration-status'},
    'com.apple.bluetoothuserd': {'LastOSLaunchVersion', 'lastLaunchBootSessionUUID'},
    'com.apple.calaccessd': {'CALNNotificationIconIdentifierVersion'},
    'com.apple.calculateframework': {'currencyCache', 'currencyCacheRefreshDate'},
    'com.apple.cloudd': {'com.apple.private.cloudkit.shouldUseGeneratedDeviceID'},
    'com.apple.cloudpaird': {
        'MagicCloudPairingMasterSubscriptionID', 'PreviousToken', 'UploadedHSA2KeysForLocalDevice'
    },
    'com.apple.commcenter.data': {'pw_ver'},
    'com.apple.commerce': {
        'AvailableUpdatesAtLastNotification', 'LastUpdateNotificationOSMajorVersion',
        r'^re:PrivacyConsent\:'
    },
    'com.apple.configurator': {'Storefront'},
    'com.apple.configurator.ui': {'LastAcceptedConfiguratorLicenseVersion'},
    'com.apple.configurator.ui.commerce': {'re:^PrimaryAccount', 're:^Storefront'},
    'com.apple.controlcenter': {'re:^LastHeartbeat.*'},
    'com.apple.coreservices.useractivityd': {'re:k(?:Local|Remote)PasteboardBlobName'},
    'com.apple.dataaccess.babysitter': {'LastSystemVersion'},
    'com.apple.dataaccess.dataaccessd': {'kDAMigrationBuildVersionKey'},
    'com.apple.diagnosticextensionsd': {'directoriesCleanupDone'},
    'com.apple.dock': {'mod-count', 'last-analytics-stamp', 'lastShowIndicatorTime'},
    'com.apple.driver.AppleBluetoothMultitouch.trackpad': {'version'},
    'com.apple.dt.Instruments': {
        'DTDKLastLSRegisterHashes', 'DTWirelessUniqueShortTypeLocationID', 'RecentTemplates.array'
    },
    'com.apple.dt.Xcode': {
        'DeveloperAccountForProject', 'DVTTextCompletionRecentCompletions',
        'IDESourceControlKnownSSHHostsDefaultsKey', 're:^IDEPlatformsFirstLaunchPresented.*',
        're:lastRecordedRefresh$'
    },
    'com.apple.finder': {
        'CopyProgressWindowLocation', 'EmptyTrashProgressWindowLocation', 'FXConnectToBounds',
        'FXConnectToLastURL', 'FXPreferencesWindow.Location', 'GoToField', 'GoToFieldHistory',
        'LastTrashState', 'MountProgressWindowLocation', 'RecentMoveAndCopyDestinations',
        'TagsCloudSerialNumber'
    },
    'com.apple.iBooksX': {
        r're:^BKBookViewerPlugInInstanceDescriptor', r're:^MZBookKeeper\.LastDsid'
    },
    'com.apple.iBooksX.commerce': {'Storefront'},
    'com.apple.iCal': {
        'AccountDisplayOrder', 'CalAgentNS_Preference_DefaultReminderCalendar',
        'CalFirstVisibleDate', 'CALPrefLastTruthFileMigrationVersion', 'first shown minute of day',
        'iCal version', 'kCalDBLastSpotLightIndexVersion', 'last selected calendar list item',
        'LastCheckForIgnoredPseudoEvents', 'LastSaveDate', 'lastViewsTimeZone', 'PrefMigrationSeed'
    },
    'com.apple.iChat': {
        'AccountSortOrder', 'ChatWindowControllerUnifiedFrame', 'KeepMessagesVersionID',
        'LastFailedMessageIMDNotificationPostedDate', 'LastIMDNotificationPostedDate',
        'UnifiedChatWindowControllerSelectionGUIDSet', r're:^messageTracer'
    },
    'com.apple.iCloudNotificationAgent': {
        'com.apple.iCloudNotification.sessionUUID', 're:^_ICQLegacyQuotaFollowupCleanup.*'
    },
    'com.apple.iTunes': {'Store Apple ID', 'Store DSID', 'WirelessBuddyID', 'storefront'},
    'com.apple.iWork.Pages': {'re:^TSAICloudDocumentPreferencePrefix'},
    'com.apple.iclouddrive.features': {'re:^iCloudDrive-on-FPFS-last-boot-(uuid|timestamp)$'},
    'com.apple.imagent': {'IMChatVocabularyUpdaterDidPerformInitialUpdateKey'},
    'com.apple.imessage': {'DidDoInitialDisableHashtagImages'},
    'com.apple.internetconnect': {'ServiceID'},
    'com.apple.iphonesimulator': {'CurrentDeviceUDID'},
    'com.apple.itunescloud': {'ICDefaultsKeyLastKnownSubscriptionStatusBaseCacheKey'},
    'com.apple.itunescloud.daemon': {
        'ICDDefaultsKeyKnowAccountDSIDs', 'ICDDefaultsKeyKnownActiveAccountDSID'
    },
    'com.apple.keychainaccess': {'Last Selected Keychain'},
    'com.apple.knowledge-agent': {
        'kCDIntentDeletionPendingDeletesQueued', 're:_DKThrottledActivityLast_.*'
    },
    'com.apple.languageassetd': {'LastSystemVersion'},
    'com.apple.logic10': {'lastSelectedKeyCommandsPath', r're:^DefaultDir'},
    'com.apple.loginwindow': {'TALLogoutReason', 'oneTimeSSMigrationComplete'},
    'com.apple.mail': {
        'AccountInfoLastSelectedAccountId', 'AccountOrdering',
        'com.apple.mail.searchableIndex.lastProcessedAttachmentIDKey',
        'CurrentTransferMailboxURLString', 'LastAttachedDir', 'LastChatSyncTime',
        'LastMessageTracingDate', 'MailSections', 'MailUpgraderPrePersistenceVersion',
        'MailUpgraderVersion', 'MailVisibleSections', 'NumberOfMessagesMarkedAsJunk',
        'NumberOfMessagesMarkedAsNotJunk', 'SignatureSelectionMethods', 'SignaturesSelected'
    },
    'com.apple.messages.nicknames': {
        'NicknameAppleIDAndiCloudAccountMatchAndExist', 'NicknameScrutinyDoNotHandle',
        'ReuploadLocalNicknamesVersion'
    },
    'com.apple.mobiletimer': {'LatestUpdateVersion', 'citiesLastModified'},
    'com.apple.mobiletimerd': {
        'MTAlarmModifiedDate', 'MTAlarmStorageVersion', 'MTTimerStorageVersion',
        'MTTimerModifiedDate'
    },
    'com.apple.networkserviceproxy': {'NSPLastGeohash'},
    'com.apple.newsd': {'FCAppConfigurationBundleShortVersionKey'},
    'com.apple.print.PrinterProxy': {'IK_Scanner_downloadURL', 'IK_Scanner_selectedTag'},
    'com.apple.quicklook.ThumbnailsAgent': {'QLMTCacheSizeLastCheckAbsoluteTime'},
    'com.apple.screencapture': {'last-analytics-stamp'},
    'com.apple.searchd': {r're:^engagementCount'},
    'com.apple.seeding': {'HasRunMigration'},
    'com.apple.seserviced': {'keysync.recovery.required'},
    'com.apple.siri.VoiceShortcuts': {'VCLSDataSequenceKey', 'VCLSDatabaseUUIDKey'},
    'com.apple.sms': {'hasBeenApprovedForSMSRelay'},
    'com.apple.speech.recognition.AppleSpeechRecognition.prefs': {r're:^DictationIMUpgradedTo'},
    'com.apple.stocks': {'lastModified'},
    'com.apple.systempreferences': {
        'ThirdPartyCount', 'com.apple.SecurityPref.Privacy.LastSourceSelected',
        r're:^NSTableView Supports'
    },
    'com.apple.systemuiserver': {'last-analytics-stamp'},
    'com.apple.talagent': {'LastKeyChange'},
    'com.apple.tipsd': {
        'DeliveryInfoVersion', 'TPSLastMajorVersion', 'TPSWelcomeNotificationViewedVersion',
        'TPSWidgetUpdateDate', 'TPSOfflineLastProcessedRemoteContentIdentifier',
        'TPSTipsAppInstalled', 'TPSWelcomeNotificationStartDate'
    },
    'com.apple.voicetrigger.notbackedup': {r're:^Power Logging Current'},
    'com.citrix.receiver.helper': {'ldDeviceIdentifier'},
    'com.citrix.receiver.nomas': {
        'AutoUpdateLastCheckedDate', 'CEIPLastUploadedReceiverVersion', 'CEIPPreviousUploadDate'
    },
    'com.crowdcafe.windowmagnet': {'usageCount'},
    'com.etresoft.EtreCheck4': {'asset'},
    'com.etresoft.EtreCheckMAS': {'asset'},
    'com.googlecode.iterm2': {
        'Default Bookmark Guid', 'NoSyncAllAppVersions', 'NoSyncInstallationId',
        'UKCrashReporterLastCrashReportDate', r're:^NeverWarnAboutShortLivedSessions',
        'iTerm Version', 'NoSyncLastOSVersion'
    },
    'com.jamfsoftware.selfservice.mac': {'com.jamfsoftware.selfservice.brandinginfo'},
    'com.lujjjh.LinearMouse': {'LaunchAtLogin__hasMigrated'},
    'com.manytricks.Moom': {'Automatic News Updates: Version'},
    'com.microsoft.OneDrive': {
        'EnableFileProvider_EnabledDate', 'SilentBusinessConfigCompleted',
        'UpdateRingSettingsLastSuccess'
    },
    'com.microsoft.OneDriveStandaloneUpdater': {'SQMSharedMachineId'},
    'com.microsoft.SharePoint-mac': {'UpdateRingSettingsLastSuccess'},
    'com.microsoft.office': {
        'CurrentUserConsentGroupKey', 'HaveMergedOldPrefs', r're:^MerpStateKey',
        'OCPS-LastSuccessfulUserId', r're:^Tenant', 'UpgradedOffice2011',
        'WLMKernel.Registry.UseRWDBSentinelFile', r're:^.*ADAL-',
        r're:^kFRETermsOfUseUpdat(?:ed|ing)Shown'
    },
    'com.monosnap.monosnap': {'last online time', 'mono_pref_time', r're:^[0-9a-f]{24}\&0$'},
    'com.parallels.Parallels Desktop': {
        r're:[0-9a-f]{12}\}\.', r're:^Guest OS Sources',
        r're:{[0-9a-f]{8}\-[0-9a-f]{4}]\-[0-9a-f]{4}\-[0-9a-f]{4}\-'
    },
    'com.qtproject': {'FileDialog.lastVisited', 'FileDialog.qtVersion'},
    'com.surteesstudios.Bartender': {r're:^TerminationReasons?', 'trial4Start'},
    'com.vmware.fusion': {'DUISettingsItemCDROM_recentItems'},
    'cx.c3.theunarchiver': {'DM_SID', '_sid'},
    'diagnostics_agent': {'lastSuccess'},
    'familycircled': {'FamilyMarqueeHasEverBeenCalled'},
    'loginwindow': {r're:^(?:Build|System)VersionStamp'},
    'org.quassel-irc.quasselclient': {
        r're:^CoreAccounts\.\d+\.General\.JumpKeyMap', r're:^CoreAccounts\.\d+\.Password'
    },
    'org.videolan.vlc': {r're:^recentlyPlayed', 'VLCPreferencesVersion'},
    'us.zoom.xos': {r're:^ZoomAutoUpdate', r're:^Pres(?:Meeting)?AppKeyHash'},
}
