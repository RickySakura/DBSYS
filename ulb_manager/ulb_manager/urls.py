"""ulb_manager URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.0/topics/http/urls/
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
from django.views.generic import TemplateView # 添加模板视图模块

# 为了让前后端接口交互，引入
from django.urls import include
# url地址模板
urlpatterns = [
    path('admin/', admin.site.urls), # 原生Django的介绍页面，可以删除
    path('',TemplateView.as_view(template_name="index.html")), # 添加指向index.html页面的路由
    # 将后台应用中配置的urls文件中配置的路由作为子路由暴露在容器中的api/路径下，这样在backend中配置的路由都能在api/下进行访问。
    # 在backend.urls中配置了testapi的路由，这里用include将testapi包含在api/路由后，形成父子路由关系了，访问时需要用api/testapi
    path('api/',include('backend.urls')),
]


