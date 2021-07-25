# CTFd-SSO-plugin

Plugin that allows login and registration via OAuth2

Works perfectly with KeyCloak

**Won't work with MajorLeagueCyber enabled**

## Installation

1. Clone this repository to [CTFd/plugins](https://github.com/CTFd/CTFd/tree/master/CTFd/plugins).
2. In [CTFd/config.ini](https://github.com/CTFd/CTFd/blob/master/CTFd/config.ini) update the following entries (see below for more information):

   - in the `[oauth]` section:
     - OAUTH_CLIENT_ID =
     - OAUTH_CLIENT_SECRET =
   - in the `[extra]` section:
     - OAUTH_AUTHORIZATION_ENDPOINT =
     - OAUTH_TOKEN_ENDPOINT =
     - OAUTH_API_ENDPOINT =
     - OAUTH_ALWAYS_POSSIBLE =

3. Login via SSO will be available visiting `/sso/login`. You may want to add a button to your theme.

## Config parameters

`[oauth]`

- `OAUTH_CLIENT_ID`: Client ID for CTFd
- `OAUTH_CLIENT_SECRET`: Client secret for access token request

`[extra]`

- `OAUTH_AUTHORIZATION_ENDPOINT`: OAuth2 endpoint for user login
- `OAUTH_TOKEN_ENDPOINT`: OAuth2 endpoint to get an access token
- `OAUTH_API_ENDPOINT`: OAuth2 endpoint to get user info from the Identity Provider
- `OAUTH_ALWAYS_POSSIBLE`: Allow registration via OAuth even if the registration is private

## Admin accounts

If you want to automatically create admin accounts via the Identity Provider, make sure that the API Endpoint returns a key `roles` containing an array. The first element of that array will be set as the user role in CTFd.

For example if an user should be admin, the Identity Provider should return something like: `{"preferred_username": "username", "email": "example@ctfd.org", "roles": ["admin"]}`

The allowed roles for CTFd are `admin` and `user`, but the latter is set by default.
