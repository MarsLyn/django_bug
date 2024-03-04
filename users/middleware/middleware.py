from django.utils.deprecation import MiddlewareMixin


from datetime import datetime


from strategy.models import Strategy
from goods.models import Goods



class GetPriceStrategy(MiddlewareMixin):

    def process_request(self, request):

        if request.user.is_authenticated:
            # 获取用户的价格策略
            # 在消费记录中查找用户最近一次消费信息
            _object = Goods.objects.filter(by_user=request.user, status=1).order_by('-pk').first()
            if _object.end_date and datetime.now() < _object.end_date:
                # 如果记录未到期
                # 把最近的消费记录的策略传到request.strategy中
                request.strategy = _object.strategy
            else:
                # 如果记录到期或者结束时间是None
                # 把免费的策略传到request.strategy中
                request.strategy = Strategy.objects.filter(title='个人免费版').first()