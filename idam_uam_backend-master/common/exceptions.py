from rest_framework.views import exception_handler
from rest_framework.views import Response
from rest_framework import status


class ConcurrentUpdate(Exception):
    pass


class MissingLastModificationDate(Exception):
    pass


class UserBeingUpdated(Exception):
    pass


def custom_exception_handler(exc, context):
    response = exception_handler(exc, context)
    if isinstance(exc, ConcurrentUpdate):
        tmp_response = Response(status=status.HTTP_400_BAD_REQUEST)
        tmp_response.data = {}
        tmp_response.data['Error'] = 'The current record was modified by others since last retrieval'
        return tmp_response
    elif isinstance(exc, MissingLastModificationDate):
        tmp_response = Response(status=status.HTTP_400_BAD_REQUEST)
        tmp_response.data = {}
        tmp_response.data['Error'] = 'Current record has no modification time recorded'
        return tmp_response
    elif isinstance(exc, UserBeingUpdated):
        tmp_response = Response(status=status.HTTP_400_BAD_REQUEST)
        tmp_response.data = {}
        tmp_response.data['Error'] = 'Current user is being updated by another request'
        return tmp_response
    return response
