from social.backends.google import GoogleOAuth2


class CustomGoogleOAuth2(GoogleOAuth2):
    def get_scope(self):
        scope = super(CustomGoogleOAuth2, self).get_scope()
        if self.data.get('extrascope'):
            scope = scope + ['https://www.googleapis.com/auth/gmail.send']
        return scope
