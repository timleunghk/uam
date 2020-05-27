from rest_framework import viewsets
from rest_framework.decorators import action
from .serializers import AbstractRequestSerializer

class AbstractRequestViewSet(viewsets.ModelViewSet):

    def _add_extra_serializer_context(self, context):
        '''
            Subclass shall override this if additional information need to be added to the context
            The context will be passed to the serializer for further processing
        '''
        return context

    def get_serializer_context(self):
        custom_context = super(AbstractRequestViewSet,
                               self).get_serializer_context()
        # Execute all super classes' _add_extra_serializer_context methods
        for base in self.__class__.__bases__:
            if callable(getattr(base, '_add_extra_serializer_context', None)):
                # base._add_extra_serializer_context(self, custom_context)
                getattr(base, '_add_extra_serializer_context')(
                    self, custom_context)
        return custom_context


class AllowDraftMixin(object):

    @action(detail=True, methods=['put'], url_path='draft')
    def save_draft(self, request, pk=None):
        self.is_draft = True
        return self.update(request, pk)

    def _add_extra_serializer_context(self, context):
        if getattr(self, 'is_draft', False):
            current_actions = context.get(
                AbstractRequestSerializer.CURRENT_ACTION_KEY, [])
            current_actions.append('draft')
            context[AbstractRequestSerializer.CURRENT_ACTION_KEY] = current_actions


class AllowDraftOnCreateMixin(AllowDraftMixin):
    @action(detail=False, methods=['post'], url_path='draft')
    def create_draft(self, request):
        self.is_draft = True
        return self.create(request)


class AllowRejectMixin(object):

    @action(detail=True, methods=['put'])
    def reject(self, request, pk=None):
        self.is_reject = True
        return self.update(request, pk)

    def _add_extra_serializer_context(self, context):
        if getattr(self, 'is_reject', False):
            current_actions = context.get(
                AbstractRequestSerializer.CURRENT_ACTION_KEY, [])
            current_actions.append('reject')
            context[AbstractRequestSerializer.CURRENT_ACTION_KEY] = current_actions
