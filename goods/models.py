from django.db import models
from django.utils.translation import gettext_lazy as _
from django.conf import settings

from strategy.models import Strategy

class Goods(models.Model):

    space = models.UUIDField(_('订单号'), unique=True)
    status = models.SmallIntegerField(_('状态'), choices=((0,'未支付'),(1,'已支付')))
    by_user = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='goods', on_delete=models.CASCADE, verbose_name=_('用户'))
    strategy = models.ForeignKey(Strategy, related_name='goods', on_delete=models.CASCADE, verbose_name=_('策略'))
    amount = models.DecimalField(_('实际支付'), max_digits=5, decimal_places=2)
    start_date = models.DateTimeField(_('开始时间'), null=True)
    end_date = models.DateTimeField(_('结束时间'), null=True)
    num = models.PositiveIntegerField(_('购买数量(年)'))
    create_date = models.DateTimeField(_('创建时间'), auto_now_add=True)