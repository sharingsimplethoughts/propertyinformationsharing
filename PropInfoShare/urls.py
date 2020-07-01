"""PropInfoShare URL Configuration

The `urlpatterns` list routes URLs to views. For more  please see:
    https://docs.djangoproject.com/en/2.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path
from django.conf.urls import url, include
from accounts.views import activate
from django.conf import settings
from django.conf.urls.static import static
from accounts.api.views import AcceptInviteView


urlpatterns = [
    path('admin/', admin.site.urls),
    url(r'^activate/(?P<uidb64>[0-9A-Za-z_\-]+)/(?P<token>[0-9A-Za-z]{1,13}-[0-9A-Za-z]{1,20})/$', activate,
        name='activate'),  # Email Activation
    url('^', include('django.contrib.auth.urls')),  # email varification
    # path('charge/', charge, name='charge'),
    #django-invitations
    url(r'^invitations/accept-invite/(?P<key>\w+)/?$', AcceptInviteView.as_view(), name='accept-invite'),
    url(r'^invitations/', include('invitations.urls', namespace='invitations')),

    #apis
    path('api/v1/users/', include(('accounts.api.urls', 'accounts'), namespace="users-api")),
    path('api/v1/posts/', include(('posts.api.urls', 'posts'), namespace="posts-api")),
    path('api/v1/subscriptions/',include(('subscriptions.api.urls', 'subscriptions'), namespace="subscriptions-api")),
    path('api/v1/questions/', include(('questions.api.urls', 'questions'), namespace="questions-api")),
    path('api/v1/extra/', include(('extra.api.urls', 'extra'), namespace="extra-api")),
    path('api/v1/search/', include(('search.api.urls', 'extra'), namespace="search-api")),
    path('api/v1/payment/', include(('payment.api.urls', 'payment'), namespace="payment-api")),
    path('api/v1/chat/', include(('chat.api.urls', 'chat'), namespace="chat-api")),
    path('api/v1/notification/', include(('notifications.api.urls', 'notifications'), namespace='notification-api')),

    #admin_panel
    path('accounts/', include('accounts.urls', namespace='my_accounts')),
    path('admin_panel/', include('admin_panel.aaccounts.urls', namespace='ap_accounts')),
    path('api/admin_panel/', include('admin_panel.aaccounts.api.urls', namespace='ap_accounts_api')),
    path('admin_panel/settings_management/',include(('admin_panel.settings_management.urls'),namespace='ap_settings_management')),

    #web push notification
    # path('firebase-messaging-sw.js', ServiceWorkerView.as_view(), name='service_worker'),
]

if settings.DEBUG:
    # urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
# urlpatterns += [url(r'^debug/', include('silk.urls', namespace='silk'))]
urlpatterns += [url(r'^silk/', include('silk.urls', namespace='silk'))]
