from django.urls import reverse
from django.shortcuts import redirect
from django.contrib import messages


class RedirectIfAuthenticatedMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):

        if request.user.is_authenticated:  # check if user is logged in
            if request.path == reverse("accounts:login_page"):
                messages.info(request, "You are already logged in")
                return redirect(reverse("accounts:customer_profile"))
            elif request.path == reverse("accounts:register_page"):
                messages.info(request, "Please logout first and then register")
                return redirect(reverse("accounts:customer_profile"))

        response = self.get_response(request)
        # Code to be executed after the view
        return response


class AdminRequiredMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):

        if request.user.is_authenticated and request.path == reverse(
            "accounts:admin_dashboard"
        ):
            if not request.user.is_staff:  # check if user is logged in
                messages.warning(request, "You are not authorized to access admin page")
                return redirect(reverse("accounts:customer_profile"))

        response = self.get_response(request)
        # Code to be executed after the view
        return response
