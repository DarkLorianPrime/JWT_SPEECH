class Ctx:
    settings = None

    @property
    def auth_settings(self) -> 'InitJWTAuth':
        if self.settings is None:
            raise RuntimeError(
                'Settings not initialized. Call InitJWTAuth before use authentication'
            )

        return self.settings


ctx = Ctx()
