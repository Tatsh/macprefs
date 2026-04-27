local utils = import 'utils.libjsonnet';

{
  uses_user_defaults: true,
  description: 'Command and library to export macOS preferences.',
  keywords: ['command line', 'macos', 'preferences', 'utilities'],
  project_name: 'macprefs',
  version: '0.4.3',
  want_main: true,
  want_flatpak: false,
  want_snap: false,
  security_policy_supported_versions: { '0.4.x': ':white_check_mark:' },
  supported_platforms: 'macos',
  pyproject+: {
    project+: {
      classifiers+: [
        'Environment :: MacOS X',
        'Intended Audience :: Information Technology',
        'Intended Audience :: System Administrators',
        'Operating System :: MacOS :: MacOS X',
        'Topic :: System :: Archiving :: Backup',
        'Topic :: System :: Systems Administration',
        'Topic :: Utilities',
      ],
      scripts: {
        'macprefs-install-job': 'macprefs.main:install_job',
        'prefs-export': 'macprefs.main:main',
      },
    },
    tool+: {
      mypy+: { platform: 'darwin' },
      poetry+: {
        dependencies+: {
          anyio: utils.latestPypiPackageVersionCaret('anyio'),
          platformdirs: utils.latestPypiPackageVersionCaret('platformdirs'),
          tomlkit: utils.latestPypiPackageVersionCaret('tomlkit'),
        },
        group+: {
          tests+: {
            dependencies+: {
              'pytest-asyncio': utils.latestPypiPackageVersionCaret('pytest-asyncio'),
            },
          },
        },
      },
      pyright+: {
        pythonPlatform: 'Darwin',
      },
    },
  },
  tests_run_on: 'macos-latest',
}
