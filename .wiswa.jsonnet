local utils = import 'utils.libjsonnet';

(import 'defaults.libjsonnet') + {
  // Project-specific
  description: 'Command and library to export macOS preferences.',
  keywords: ['command line', 'macos', 'preferences', 'utilities'],
  project_name: 'macprefs',
  version: '0.3.4',
  want_main: true,
  citation+: {
    'date-released': '2025-04-14',
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
        'macprefs-install-job': 'macprefs:install_job',
        'prefs-export': 'macprefs:prefs_export',
      },
    },
    tool+: {
      mypy+: {
        mypy_path: './.stubs',
      },
      poetry+: {
        dependencies+: {
          click: '^8.1.8',
          deepdiff: '^8.4.2',
        },
      },
    },
  },
  skip+: ['tests/test_main.py', 'tests/test_utils.py', 'macprefs/utils.py'],
  // Common
  authors: [
    {
      'family-names': 'Udvare',
      'given-names': 'Andrew',
      email: 'audvare@gmail.com',
      name: '%s %s' % [self['given-names'], self['family-names']],
    },
    {
      'family-names': 'Javier',
      'given-names': 'Francisco',
      email: 'web@inode64.com',
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
