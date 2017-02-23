# from django.shortcuts import redirect
# from django.http import Http404
# from
#
#
# class NonceAuthentication(object):
#     def __init__(self, get_response):
#         self.get_response = get_response
#         # One-time configuration and initialization.
#
#     def __call__(self, request):
#         # Code to be executed for each request before
#         # the view (and later middleware) are called.
#
#         response = self.get_response(request)
#
#         # Code to be executed for each request/response after
#         # the view is called.
#         if not request.user.is_authenticated:
#             return redirect('auth')
#
#         authenticated, nonce, key = Authenticate.check_authentication(request)
#         if not authenticated:
#             return redirect('auth')
#         return response