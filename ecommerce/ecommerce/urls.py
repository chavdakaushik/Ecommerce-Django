from core.views import CartView, FilterCategoryView, HomePageView, \
    ItemDetailView, ProfileView, SearchView, SignupView, \
    remove_user_cart, checkout, update_user_cart, ActivateAccount

from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.contrib.auth.views import LoginView, LogoutView, \
    PasswordResetView, PasswordChangeView, PasswordResetDoneView, \
    PasswordResetConfirmView, PasswordResetCompleteView
from django.urls import path

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', HomePageView.as_view(), name='home'),
    path('cart/', CartView.as_view(), name='cart'),
    path('search/', SearchView.as_view(), name='search'),
    path('single_item/<int:pk>/', ItemDetailView.as_view(),
         name='singleItem'),
    path('filter_category/<str:choice>/<int:pk>/',
         FilterCategoryView.as_view(), name='filter_category'),
    path('update_item/', update_user_cart, name='updateItem'),
    path('remove_item/', remove_user_cart, name='removeItem'),
    path('checkout/', checkout, name='send'),
    path('login/',
         LoginView.as_view(template_name='registration/login.html',
                           redirect_authenticated_user=True), name='login'),
    path('logout/',
         LogoutView.as_view(template_name='registration/logout.html',
                            next_page='login'), name='logout'),
    path('signup/', SignupView.as_view(), name='signup'),
    path('activate/<uidb64>/<token>/', ActivateAccount.as_view(),
         name='activate'),
    path('profile/<int:pk>/', ProfileView.as_view(), name='profile'),
    path('change-password/',
         PasswordChangeView.as_view(template_name='password/changepassword.html', success_url='/'), name='change_password'),
    path('password-reset/',
         PasswordResetView.as_view(template_name='password/password_reset.html', subject_template_name='password/password_reset_subject.txt',
                                   email_template_name='password/password_reset_email.html'),
         name='password_reset'),
    path('password-reset/done/',
         PasswordResetDoneView.as_view(template_name='password/password_reset_done.html'
                                       ), name='password_reset_done'),
    path('password-reset-confirm/<uidb64>/<token>/',
         PasswordResetConfirmView.as_view(template_name='password/password_reset_confirm.html'
                                          ), name='password_reset_confirm'),
    path('password-reset-complete/',
         PasswordResetCompleteView.as_view(template_name='password/password_reset_complete.html'
                                           ), name='password_reset_complete'),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
