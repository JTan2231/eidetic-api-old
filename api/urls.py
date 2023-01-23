from django.urls import path
from django.conf import settings
from django.conf.urls.static import static
from knox import views as knox_views
from .views import api, pages

urlpatterns = [
    # PAGES
    path('', pages.index.index),
    path('login/', pages.login.index),
    path('new_user/', pages.new_user.index),

    # API
    path('api/entries/', api.entry.EntryView.as_view()),
    path('api/create-entry/', api.entry.CreateEntryView.as_view()),
    path('api/imports/', api.imports.ImportView.as_view()),
    path('api/users/', api.user.UserView.as_view()),
    path('api/create-user/', api.create_user.CreateUserView.as_view()),
    path('api/collections/', api.collection.CollectionView.as_view()),
    path('api/collectionentries/', api.collection_entry.CollectionEntryView.as_view()),
    path('api/entriesbycollection/', api.entries_by_collection.EntriesByCollectionView.as_view()),
    path('api/login/', api.authentication.AuthenticationView.as_view(), name='knox_login'),
    path('api/logout/', api.authentication.LogoutView.as_view(), name='knox_logout'),
    path('api/logoutall/', knox_views.LogoutAllView.as_view(), name='knox_logoutall'),
] + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
