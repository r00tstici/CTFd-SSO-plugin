# CTFd-SSO-plugin

Plugin that allows login and registration via OAuth2

Works perfectly with KeyCloak

## Installation

1. To install clone this repository to the [CTFd/plugins](https://github.com/CTFd/CTFd/tree/master/CTFd/plugins) folder.
2. In [CTFd/config.ini](https://github.com/CTFd/CTFd/blob/master/CTFd/config.ini) add the following entries:
   - in the `[oauth]` section:
      - OAUTH_AUTHORIZATION_ENDPOINT =
      - OAUTH_TOKEN_ENDPOINT =
   - in the `[extra]` section:
      - OAUTH_API_ENDPOINT =
      - OAUTH_CLIENT_ID =
      - OAUTH_CLIENT_SECRET =
      - OAUTH_ALWAYS_POSSIBLE =
3. Set the values for that entries in [CTFd/config.ini](https://github.com/CTFd/CTFd/blob/master/CTFd/config.ini) or via environment variables
4. Edit your theme so the user can visit `/sso/login` to login via OAuth

## Config parameters
`[oauth]`
- `OAUTH_AUTHORIZATION_ENDPOINT`: OAuth2 endpoint for user login
- `OAUTH_TOKEN_ENDPOINT`: OAuth2 endpoint to get an access token

`[extra]`
- `OAUTH_API_ENDPOINT`: OAuth2 endpoint to get user info from the Identity Provider
- `OAUTH_CLIENT_ID`: Client ID for CTFd
- `OAUTH_CLIENT_SECRET`: Client secret for access token request
- `OAUTH_ALWAYS_POSSIBLE`: Allow registration via OAuth even if the registration is private

## Admin accounts

If you want to automatically create admin accounts via the Identity Provider, make sure that the API Endpoint returns a key `roles` containing an array. The first element of that array will be set as the user role in CTFd.

For example if an user should be admin, the Identity Provider should return something like: `{"preferred_username": "username", "email": "example@ctfd.org", "roles": ["admin"]}`
