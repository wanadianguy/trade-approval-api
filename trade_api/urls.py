from rest_framework.routers import DefaultRouter

from .views import TradeLogView, TradeView

router = DefaultRouter()
router.register(r"trades", TradeView, basename="trade")
router.register(r"trade_logs", TradeLogView, basename="trade-log")
urlpatterns = router.urls
