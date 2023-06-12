# RSS Reader coding challenge for SendCloud

## Requirements
- Support at least the following feeds:
    - http://www.nu.nl/rss/Algemeen
    - https://feeds.feedburner.com/tweakers/mixed
- A user of this API should be able to:
    - Follow and unfollow multiple feeds
    - List all feeds registered by them
    - List feed items belonging to one feed
    - Mark items as read
    - Filter read/unread feed items per feed and globally (e.g. get all unread items
from all feeds or one feed in particular). Order the items by the date of the last
update
    - Force a feed update
- Feeds (and feed items) should be updated in a background task, asynchronously, periodically and in an unattended manner. We use Dramatiq for Sendcloud tasks, but you may use whichever solution you’re comfortable with (e.g. asyncio, Celery).
- Implement a back-off mechanism for feed fetching
    - If a feed fails to be updated, the system should fall back for a while.
    - After a certain amount of failed tries, the system should stop updating the
feed automatically.
    - Users should be notified and able to retry the feed update if it is stalled after
these failed tries.

## User stories
- [x] Follow feed.
- [x] List feeds.
- [x] Unfollow feed.
- [x] List feed items.
- [x] Mark item as read.
- [x] List unread feed items ordered by date of last update.
- [x] List all unread items ordered by date of last update.
- [x] Refresh feed.
- [x] Refresh feeds periodically.
- [x] Notify user when feed refresh fails a certain number of times.
- [x] User Sign up.
- [x] User login.
- [x] User logout.

## Implementation
The app is implemented using Django.
Celery is used with Redis as a backend for task queueing and scheduling.
PostgreSQL is used for storage.
Nginx is used as reverse proxy and for serving static files.

## Design
The app design is based on the hexagonal architecture. Business logic is isolated
in services, data access is isolated in repositories wrapping Django's models,
and the delivery method, here REST APIs, is implemented using Django's views.
The business logic isn't aware of the data access or API implementations and doesn't
depend on them. Future changes to either shouldn't affect the business logic.

For testing, integration/end to end tests are the main method of testing used
since they're very easy to implement with Django. One unittest is implemented
as a demonstration of the isolation of the business logic from details like data
access and delivery method, but since the logic in this app is simple and all
functionalities are convered by integrtion tests, more unit tests were not
implemented since they don't add value.

## How to run
Apply migrations. This needs to run one time.
```sh
docker compose -f  prod.compose.yaml run --build rss-reader python manage.py migrate --noinput
```
To start services:
```sh
docker compose -f prod.compose.yaml up --build
```
The app is served on port `80` on the host.

To stop services:
```sh
docker compose -f prod.compose.yaml down
```
For admin UI usage, create a super user:
```sh
docker compose -f prod.compose.yaml run --build -it rss-reader python manage.py createsuperuser
```
To run tests:
```sh
docker compose -f  prod.compose.yaml run --build rss-reader python manage.py test
```

## API
To download OpenAPI schema, use `/api/schema/`.
You can also view it in Swagger UI at `/api/schema/swagger-ui/`
or redoc at `/api/schema/redoc/`.

Schema URLs are public and don't require authentication.

## How to use
1. Use the sign up API to create a user.
2. Use the login API to sign in using the previously created user.
The login API returns a token. The token is used with all following API calls
using Bearer authentication with the prefix `Token`.
Example: `Token xxxxxxxxxxxxxx`
3. Use the Feeds APIs to follow, unfollow, read and refresh feeds.
4. Use the Items APIs to list items and mark items as read/unread.
5. Feed items and Items list can be filtered to get unread items only.
6. Feeds are automatically refreshed in the background every hour.
If a scheduled refresh fails, it's retried 3 times with backoff then if it keeps
failing, the automatic refresh is disabled for that feed and an email is sent to
the user.

## Caveats
Some things that would be considered necessary for a production environment are
not implemented here:
- E-mail verification process on users sign up.
- Replace django's default integer user id generation with UUID.
- Business and app metrics.
