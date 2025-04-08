from django.urls import path
from . import views

urlpatterns = [
	path("monthly/", views.show_monthly_sales, name="monthly_sales"),
	path("country/", views.show_sales_by_country, name="sales_by_country"),
	path("customer/", views.show_avg_sales_per_customer, name="avg_sales_per_customer"),
	path("top10/", views.show_top10_products, name="top10_products"),
	path("timeslot/", views.show_sales_by_timeslot, name="sales_by_timeslot"),
]
