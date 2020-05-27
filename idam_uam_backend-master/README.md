## The backend implementation of IdAM UAM

It mainly depends on Django Rest Framework, Django-Polymorphic models
To start the project, do the following:
1.  Go to the home folder of the project
2.  Type the following command to create a python virtual environment and start the environment

>>For Linux
```console
virtualenv localenv
source localenv/bin/activate
```

>>For Windows
```console
virtualenv localenv
localenv\scripts\activate
```

3.  Install all dependencies
```console
pip install -r requirements.txt
```

4.  Run the test
```console
python manage.py test
```

5.  To start the server
```console
python manage.py runserver
```

## Background
The application is divided into several apps:
1.  uam_requests - Implementation of all UAM Requests(e.g. New Account Request, Review Account Request ...)
2.  uam_users - Implementation of target user related activity (e.g. Saving the UAM user information, provide enquiry functions)
3.  codetables - Implementation of code tables

To start to create a UAM request, one have to create 1 serializer for the model and 1 view for HTTP request (under uam_requests.serializer.py and views.py correspondingly)
For the View part, an AbstractRequestViewSet (in uam_requests.utils) and several mixins (i.e. AllowDraftMixin, AllowDraftOnCreateMixin, AllowRejectMixin) are prepared
For the Serializer part, an AbstractRequestSerializer (also in uam_requests.utils) is also prepared.

For example, to create a request, one shall at minimal implement a viewset extending AbstractRequestViewSet and a serializer extending AbstractRequestSerializer.
To perform validation for the request, one shall implement _validate_confirm(self, data) to perform the validation (if invalid data was detected, raise an ValidationErrors. Otherwise, return the data)
To perform additional update (i.e. in addition to updating the corresponding model), one shall implement _update_confirm()
The corresponding viewset shall be registered at uam2.urls for mapping URLs to the viewset

The mixins are described as below:
1.  **AllowDraftMixin** - The viewset shall extend this mixin if the corresponding request could be saved as draft (Only update is allowed. Insert is not working, using AllowDraftOnCreateMixin instead).  If additional validation is required during saving the draft, **_validate_draft** shall be implemented at the corresponding **serializer**.  If additional update is required during saving the draft, **_update_draft** shall be implemented at the corresponding **serializer** too.
2.  **AllowDraftOnCreateMixin** - This mixin extended AllowDraftMixin.  Additionally, this mixin allows creating a new request as draft.
3.  **AllowRejectMixin** - The viewset shall extend this mixin if the corresponding request could be rejected.  Similar to the above mixins, if additional validation is required during reject, implement **_validate_reject** at the **serializer**.  If additional update is required, implement **_update_reject** at the **serializer**.

For example, CreateAccountRequestSubmit is for creating a new user account request, which could be
1.  saved as draft during creation -> Extend AllowDraftOnCreateMixin at the viewset.
2.  saved as draft during update -> No need to extend AllowDraftMixin since AllowDraftOnCreateMixin already extend it
mplement _validate_confirm if additional validation is required during request submission.  Implement _update_confirm if additional update is required during request submission.

As a second example, CreateAccountRequestReview is for reviewer to review a new user account request, which could be:
1.  saved as draft during update -> Extend AllowDraftMixin at the viewset.  Implement _validate_draft at the serializer if additional validation is required during saving the draft.  Implement _update_draft at the serializer if additional update is required.
2.  rejected -> Extend AllowRejectMixin at the viewset.  Implement _validate_reject at the serializer if additional validation is required during reject.  Implement _update_reject at the serializer if additional update is required during reject.
Implement _validate_confirm if additional validation is required during endorsement of the review.  Implement _update_confirm if additional update is required during request endorsement.