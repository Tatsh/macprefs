from typing import Final

__all__ = ('BAD_DOMAINS', 'BAD_DOMAIN_PREFIXES')

# spell-checker: disable
BAD_DOMAINS: Final[set[str]] = {
    'ContextStoreAgent', 'G2MUpdate', 'MiniLauncher', 'Mixpanel', 'MobileMeAccounts',
    'NoMachine Monitor', 'com.apple.AMPLibraryAgent', 'com.apple.AMPLibraryAgent',
    'com.apple.AdLib', 'com.apple.ColorSyncCalibrator', 'com.apple.CommCenter.counts',
    'com.apple.CoreDuet', 'com.apple.Dictionary.plist', 'com.apple.EmojiCache',
    'com.apple.EmojiCache', 'com.apple.FileStatsAgent', 'com.apple.SharedWebCredentials',
    'com.apple.appstore.commerce', 'com.apple.classroom', 'com.apple.cloudphotod',
    'com.apple.cloudphotosd', 'com.apple.commcenter', 'com.apple.commcenter.callservices',
    'com.apple.commcenter.plist', 'com.apple.commerce.knownclients', 'com.apple.coreauthd',
    'com.apple.corerecents.recentsd', 'com.apple.coreservices.uiagent', 'com.apple.facetime.bag',
    'com.apple.findmy', 'com.apple.findmy.fmfcore.notbackedup',
    'com.apple.findmy.fmipcore.notbackedup', 'com.apple.gamecenter', 'com.apple.gamed',
    'com.apple.help', 'com.apple.homed', 'com.apple.homed.notbackedup', 'com.apple.iApps',
    'com.apple.iChat.AIM', 'com.apple.iTunesHelper', 'com.apple.icloud.fmfd',
    'com.apple.icloud.fmfd.notbackedup', 'com.apple.icloud.fmip.clientconfiguration',
    'com.apple.icloud.fmip.voiceassistantsync.plist', 'com.apple.icloud.searchpartyuseragent',
    'com.apple.identityservicesd', 'com.apple.ids.deviceproperties', 'com.apple.imagecapture',
    'com.apple.imdsmsrecordstore', 'com.apple.imessage.bag', 'com.apple.imservice.ids.FaceTime',
    'com.apple.imservice.ids.iMessage', 'com.apple.inputmethod.CoreChineseEngineFramework',
    'com.apple.internal.ck', 'com.apple.ipTelephony', 'com.apple.itunesstored', 'com.apple.madrid',
    'com.apple.mediaaccessibility', 'com.apple.mediaanalysisd', 'com.apple.mmcs',
    'com.apple.newscore', 'com.apple.newscore2', 'com.apple.parsecd', 'com.apple.passd',
    'com.apple.photos.shareddefaults', 'com.apple.pipagent', 'com.apple.preference.general',
    'com.apple.preferences.softwareupdate', 'com.apple.proactive.PersonalizationPortrait',
    'com.apple.protectedcloudstorage.protectedcloudkeysyncing',
    'com.apple.protectedcloudstorage.protectedcloudkeysyncing.plist', 'com.apple.rapport',
    'com.apple.remindd', 'com.apple.remindd.babysitter', 'com.apple.routined',
    'com.apple.security.cloudkeychainproxy3.keysToRegister', 'com.apple.security.ctkd-db',
    'com.apple.security.pboxd', 'com.apple.security.sosaccount', 'com.apple.sharingd',
    'com.apple.siri-distributed-evaluation', 'com.apple.siricore.fides', 'com.apple.studentd',
    'com.apple.suggestions', 'com.apple.sync.NanoHome', 'com.apple.syncserver',
    'com.apple.textInput.keyboardServices.textReplacement', 'com.apple.tourist',
    'com.apple.touristd', 'com.apple.voicememod', 'com.apple.xpc.activity2',
    'com.gammonsoft.Absolute-Backgammon-64', 'com.glancenetworks.Glance',
    'com.glancenetworks.Log.Levels', 'com.google.Keystone.Agent',
    'com.microsoft.outlook.office_reminders', 'com.nomachine.nxdock',
    'com.parallels.desktop.console', 'com.rogueamoeba.AudioHijackPro2', 'com.rogueamoeba.loopbackd',
    'com.teamviewer.TeamViewer', 'com.teamviewer.teamviewer.preferences',
    'com.teamviewer.teamviewer.preferences.Machine', 'com.unity3d.UnityStandalone',
    'fr.madrau.switchresx.app', 'fr.madrau.switchresx.daemon', 'jp.naver.line.mac',
    'knowledge-agent', 'org.bitcoinfoundation.Bitcoin-Qt.plist', 'org.kde.marble',
    'plugin.sketch.com.google.ux.material.spec_tools',
    'systemgroup.com.apple.icloud.searchpartyd.sharedsettings', 'systemsettings5', 'vlc.exe'
}
BAD_DOMAIN_PREFIXES: Final[set[str]] = {
    'com.parallels.toolbox.', 'org.gimp.gimp-', 'org.python.', 'workplace-desktop'
}
