from django.urls import path
from django.conf import settings
from django.conf.urls.static import static
from .views import api, pages

urlpatterns = [
    # PAGES
    path('', pages.clusters.index),
    path('user/<str:username>/', pages.clusters.index),
    path('login/', pages.login.index),
    path('new_user/', pages.new_user.index),
    path('<int:entry_id>/', pages.entry_viewer.index),

    # API
    path('api/clusters/', api.clusters.ClusterView.as_view()),
    path('api/entries/', api.entry.EntryView.as_view()),
    path('api/entry-links/', api.entry_link.EntryLinkView.as_view()),
    path('api/create-entry/', api.entry.CreateEntryView.as_view()),
    path('api/delete-entry/', api.entry.DeleteEntryView.as_view()),
    path('api/users/', api.user.UserView.as_view()),
    path('api/create-user/', api.create_user.CreateUserView.as_view()),
    path('api/follow/', api.follow.FollowView.as_view()),
    path('api/feed/', api.feed.FeedView.as_view()),
    path('api/openai/', api.openai.OpenAIView.as_view()),
    path('api/imports/', api.imports.ImportView.as_view()),
    path('api/login/', api.authentication.AuthenticationView.as_view()),
    path('api/logout/', api.authentication.LogoutView.as_view()),
] + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
