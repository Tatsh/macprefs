class PropertyListConversionError(Exception):
    def __init__(self, filename: str | None = None):
        super().__init__(f'Property list {filename} failed to convert'
                         if filename else 'Property list conversion failed')
