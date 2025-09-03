# from django import template
# from pages.models import UserProfile
#
# register = template.Library()
#
# @register.simple_tag
# def get_profile(user):
#     if user.is_authenticated:
#         try:
#             return UserProfile.objects.get(user=user)
#         except UserProfile.DoesNotExist:
#             return None
#     return None