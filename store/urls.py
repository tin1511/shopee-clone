from django.urls import path
from . import views
from django.conf import settings
from django.conf.urls.static import static

urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
urlpatterns = [

    path('', views.home),

    path("register/seller/",views.register_seller,name="register_seller"),
    
    path("dashboard/",views.dashboard),

    path("seller/",views.seller_dashboard),

    path("seller/add/",views.seller_add),

    path("add-product/",views.add_product),

    path("delete-product/<int:id>/",views.delete_product),

    path("edit-product/<int:id>/",views.edit_product),

    path("dashboard/", views.dashboard),

    path("login/", views.login_view),

    path("register/", views.register_view),

    path('logout/', views.logout_view),

    path("product/<int:id>/", views.product_detail),

    path("add_to_cart/<int:id>/", views.add_to_cart),

    path("cart/", views.view_cart),

    path("login/",views.login_view),
    
    path("seller/chat/",views.seller_chat_list,name="seller_chat_list"),

    path("chat/<int:user_id>/",views.chat,name="chat"),

    path("delete-product/<int:id>/", views.delete_product),

]