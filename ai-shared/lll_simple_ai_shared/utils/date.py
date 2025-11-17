from datetime import datetime


def datetime_to_cn_format(dt_value):
    """
    将datetime对象转换为 'YYYY-MM-DD 时间段' 格式
    时间段规则：
    05:00-11:59 → 上午
    12:00-17:59 → 下午
    18:00-23:59 → 晚上
    00:00-04:59 → 凌晨
    """
    if not isinstance(dt_value, datetime):
        # 如果不是datetime类型，尝试转换
        try:
            if isinstance(dt_value, str):
                dt_value = datetime.fromisoformat(dt_value.replace("Z", "+00:00"))
            else:
                return str(dt_value)  # 无法转换则返回原值
        except (ValueError, TypeError):
            return str(dt_value)

    # 格式化日期部分
    date_str = dt_value.strftime("%Y-%m-%d")

    # 根据时间判断时间段
    hour = dt_value.hour
    if 5 <= hour < 12:
        time_period = "上午"
    elif 12 <= hour < 18:
        time_period = "下午"
    elif 18 <= hour < 24:
        time_period = "晚上"
    else:  # 0-4点
        time_period = "凌晨"

    return f"{date_str} {time_period}"
