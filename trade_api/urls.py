from rest_framework.routers import DefaultRouter

from .views import TradeLogView, TradeView

router = DefaultRouter()
router.register(r"trades", TradeView, basename="trades")
router.register(r"trade_logs", TradeLogView, basename="trade_logs")
urlpatterns = router.urls
