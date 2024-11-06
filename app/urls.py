from django.urls import path 
from .views import  dashboardview, homeview,aboutview,faqview,planview,contactview,registrationview,biodataview,admindashboardview,galleryview,blogview,views
from django.contrib.auth import views as auth_views


urlpatterns = [
    path('',homeview.home,name='home'),
    path('service/',homeview.service,name='service'),
    path('about/',aboutview.about,name='about'),
    path('faq/',faqview.faq,name='faq'),
    path('plan/',planview.plan,name='plan'),
    path('contact/',contactview.contact,name='contact'),
    path('photo-gallery/',galleryview.photogallery,name='photo_gallery'),

    # blog

    path('blog-detail/<int:pk>/',blogview.blog_detail,name='blog_detail'),
    path('blog-list/', blogview.blog_list, name='blog_list'),
    path('blog-create/', blogview.blog_create, name='blog_create'),
    path('blog-update/<int:pk>/', blogview.blog_update, name='blog_update'),
    path('blog-delete/<int:pk>/', blogview.blog_delete, name='blog_delete'),


    # registration urls
    path('register/', registrationview.register, name='register'),
    path('login/', registrationview.loginview, name='login'),
    path('logout/', registrationview.logoutview, name='logout'),
    path('activate/<uidb64>/<token>/', registrationview.activate, name='activate'),
    path('edit-account/', registrationview.edit_account, name='edit_account'),
    path('password-reset/', registrationview.password_reset_request, name='password_reset'),
    path('password-reset/done/', registrationview.password_reset_done, name='password_reset_done'),
    path('password-reset-confirm/<uidb64>/<token>/', registrationview.password_reset_confirm, name='password_reset_confirm'),
    path('password-reset-complete/', registrationview.password_reset_complete, name='password_reset_complete'),
    path('biodata/', biodataview.create_biodata, name='biodata'),
    
    # profile urls
    path('allprofiles/', biodataview.allprofiles, name='allprofiles'),
    path('profile-detail/<int:pk>/', biodataview.profile_detail, name='profile_detail'),
    path('biodata/update/', biodataview.biodata_update_view, name='biodata_update'),
    path('search/',biodataview.searchprofile, name='search'),
    # dashboard urls
    path('dashboard/', dashboardview.dashboard, name='dashboard'),
    path('dashboard-profile/', dashboardview.dashboardprofile, name='dashboardprofile'),
    path('dashboard-setting/', dashboardview.dashboardsetting, name='dashboardsetting'),

    # other URL patterns
     path('post/<int:pk>/like/', biodataview.LikeToggleView.as_view(), name='like_toggle'),
     path('post/<int:pk>/interest/', biodataview.InterestToggleView.as_view(), name='like_toggle'),


    # admin dashboard
    path('admin-home/', admindashboardview.adminhome, name='adminhome'),
    path('admin-adduser/', admindashboardview.adminadduser, name='adminadduser'),
    path('admin-alluser/', admindashboardview.adminalluser, name='adminalluser'),
    path('admin-freeuser/', admindashboardview.adminfreeuser, name='adminfreeuser'),
    path('admin-premiumuser/', admindashboardview.adminpremiumuser, name='adminpremiumuser'),
    path('edit_user/<int:user_id>/', admindashboardview.adminupdateuser, name='edit_user'),
    path('admin-new-user-requests/', admindashboardview.adminnewuserrequests, name='adminnewuserrequests'),
    path('toggle-approval/<int:user_id>/', admindashboardview.toggle_approval, name='toggle_approval'),
    path('toggle-approvals/<int:user_id>/', admindashboardview.toggle_approvals, name='toggle_approvals'),
    path('admin-advanced-search/',admindashboardview.adminadvancedsearch,name='adminadvancedsearch'),
    # 
    path('search-page/',views.search_page, name='search-page'),
    path('searchusers/',views.search_users, name='search-users'),
]