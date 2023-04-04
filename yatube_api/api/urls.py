from django.urls import include, path
from rest_framework.routers import DefaultRouter
from api.views import PostViewSet, GroupViewSet
from api.views import CommentViewSet
from api.views import FollowViewSet

app_name = 'api'

router = DefaultRouter()
router.register('posts', PostViewSet)
router.register('groups', GroupViewSet)
router.register('follow', FollowViewSet, basename='follow')
router.register(
    r'posts/(?P<post_id>\d+)/comments',
    CommentViewSet,
    basename='comments'
)
router.register(
    r'posts/(?P<post_id>\d+)/comments/(?P<comment_id>\d+)',
    CommentViewSet, basename='comment_detail'
)

urlpatterns = [
    path('v1/', include(router.urls)),
    path('v1/', include('djoser.urls')),
    path('v1/', include('djoser.urls.jwt')),
]
