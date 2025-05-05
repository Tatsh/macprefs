Configuration
=============

macprefs can be customised with a TOML file. By default ``prefs-export`` checks for the path
``~/Library/Application Support/macprefs/config.toml``. Example file:

.. code-block:: toml

   # The extend-* options extend the default values used by macprefs.
   [tool.macprefs]
   deploy-key = '/path/to/deploy-key'
   extend-ignore-domain-prefixes = ['org.gimp.gimp-']
   extend-ignore-domains = ['domain1', 'domain2']
   extend-ignore-key-regexes = ['QuickLookPreview_[A-Z0-9-\\.]+']
   # Only set these if you want to override the default values used by macprefs.
   # ignore-domain-prefixes = []
   # ignore-domains = []
   # ignore-key-regexes = []
   # ignore-keys = {}

   [tool.macprefs.extend-ignore-keys]
   "domain-name" = ["key-to-ignore1", "re:^key-to-ignore"]

In ``extend-ignore-keys`` and ``ignore-keys``, a string value to ignore can be prefixed with ``re:``
to indicate it is a regular expression.
