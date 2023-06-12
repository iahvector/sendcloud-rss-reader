from rest_framework.exceptions import APIException


class InvalidRssFeedException(APIException):
    status_code = 400
    default_code = 'inalid_rss_feed'

class FeedAlreadyExistsException(APIException):
    status_code = 400
    default_code = 'feed_already_exists'

class FeedNotFoundException(APIException):
    status_code = 404
    default_code = 'feed_not_found'

class ItemNotFoundExcpetion(APIException):
    status_code = 404
    default_code = 'item_not_found'