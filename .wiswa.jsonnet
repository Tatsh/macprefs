(import 'defaults.libjsonnet') + {
  // Project-specific
  description: 'Command and library to export macOS preferences.',
  keywords: ['command line', 'macos', 'preferences', 'utilities'],
  project_name: 'macprefs',
  version: '0.3.4',
  want_main: true,
  citation+: {
    'date-released': '2025-05-04',
  },
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
      poetry+: {
        dependencies+: {
          deepdiff: '^8.4.2',
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
    },
  },
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
