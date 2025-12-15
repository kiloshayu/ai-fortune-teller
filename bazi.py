# bazi.py
from lunar_python import Lunar, Solar

def get_bazi_text(year, month, day, hour):
    """
    输入公历时间，返回八字排盘的文本描述
    """
    solar = Solar.fromYmdHms(year, month, day, hour, 0, 0)
    lunar = solar.getLunar()
    
    # 获取四柱
    ganzhi_year = lunar.getYearInGanZhi()
    ganzhi_month = lunar.getMonthInGanZhi()
    ganzhi_day = lunar.getDayInGanZhi()
    ganzhi_time = lunar.getTimeInGanZhi()
    
    # 简单的文本描述，喂给AI用的
    bazi_text = f"""
    出生公历：{year}年{month}月{day}日 {hour}时
    四柱八字：
    年柱：{ganzhi_year}
    月柱：{ganzhi_month}
    日柱：{ganzhi_day}
    时柱：{ganzhi_time}
    """
    return bazi_text
