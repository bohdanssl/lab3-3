from django.urls import path
from .views import (
    TrainRevenueAnalyticsView,      
    RoutePriceAnalyticsView,      
    TrainTicketTypesAnalyticsView,  
    TopSpendersAnalyticsView,       
    SocialStatsAnalyticsView,       
    LuxuryOnlyAnalyticsView,
    DashboardPlotlyView,
    DashboardBokehView
)
urlpatterns = [
    path('analytics/revenue/trains/', TrainRevenueAnalyticsView.as_view(), name='revenue-trains'),
    path('analytics/routes/pricing/', RoutePriceAnalyticsView.as_view(), name='routes-pricing'),
    path('analytics/trains/classes/', TrainTicketTypesAnalyticsView.as_view(), name='trains-classes'),
    path('analytics/passengers/top-spenders/', TopSpendersAnalyticsView.as_view(), name='passengers-top'),
    path('analytics/trains/social/', SocialStatsAnalyticsView.as_view(), name='trains-social'),
    path('analytics/passengers/luxury-segment/', LuxuryOnlyAnalyticsView.as_view(), name='passengers-luxury'),
    path('dashboard/v1/', DashboardPlotlyView.as_view(), name='dashboard-plotly'),
    path('dashboard/v2/', DashboardBokehView.as_view(), name='dashboard-bokeh'),
]
