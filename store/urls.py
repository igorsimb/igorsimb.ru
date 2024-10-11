from django.conf import settings
from django.conf.urls.static import static
from django.urls import path

from store_users.views import demo_user_login_view
from .views import updateItem, processOrder, index, shop, cart, checkout, \
    contact, about, ProductDetailView, CategoryView, confirmation, SearchResultsListView, SuccessView, EmailSentView

urlpatterns = [
    path('', index, name='index'),
    path('shop/', shop, name='shop'),
    path('product/<int:pk>/', ProductDetailView.as_view(), name='product'),
    path('cart/', cart, name='cart'),
    path('checkout/', checkout, name='checkout'),
    path('confirmation/', confirmation, name='confirmation'),
    path('contact/', contact, name='contact'),
    path('success/', SuccessView.as_view(), name='success'),
    path('email-sent/', EmailSentView.as_view(), name='email_sent'),
    path('about/', about, name='about'),
    path('category/<int:category_id>/', CategoryView.as_view(), name='category'),

    path('update-item/', updateItem, name='update_item'),
    path('process-order/', processOrder, name='process_order'),
    path('search/', SearchResultsListView.as_view(), name='search_results'),

    path('demo_login/', demo_user_login_view, name='demo_login'),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
