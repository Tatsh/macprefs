(import 'defaults.libjsonnet') + {
  // Project-specific
  description: 'Command and library to export macOS preferences.',
  keywords: ['command line', 'macos', 'preferences', 'utilities'],
  project_name: 'macprefs',
  version: '0.4.1',
  want_main: true,
  citation+: {
    'date-released': '2025-05-04',
  },
  security_policy_supported_versions: { '0.4.x': ':white_check_mark:' },
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
          anyio: '^4.9.0',
          platformdirs: '^4.3.6',
          tomlkit: '^0.13.2',
        },
        group+: {
          tests+: {
            dependencies+: {
              'pytest-asyncio': '^0.26.0',
            },
          },
        },
      },
      pyright+: {
        pythonPlatform: 'Darwin',
      },
    },
  },
  copilot: {
    intro: 'macprefs is a command-line tool for managing macOS user defaults (preferences) in bulk.',
  },
  tests_run_on: 'macos-latest',
  // Common
  authors: [
    {
      'family-names': 'Udvare',
      'given-names': 'Andrew',
      email: 'audvare@gmail.com',
      name: '%s %s' % [self['given-names'], self['family-names']],
    },
  ],
  local funding_name = '%s2' % std.asciiLower(self.github_username),
  github_username: 'Tatsh',
  github+: {
    funding+: {
      ko_fi: funding_name,
      liberapay: funding_name,
      patreon: funding_name,
    },
  },
}
