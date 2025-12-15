from lunar_python import Lunar, Solar, EightChar

def get_bazi_text(year, month, day, hour):
    """
    输入公历时间，返回详细的八字+大运排盘文本
    """
    # 1. 初始化时间
    solar = Solar.fromYmdHms(year, month, day, hour, 0, 0)
    lunar = solar.getLunar()
    
    # 2. 获取八字
    ganzhi_year = lunar.getYearInGanZhi()
    ganzhi_month = lunar.getMonthInGanZhi()
    ganzhi_day = lunar.getDayInGanZhi()
    ganzhi_time = lunar.getTimeInGanZhi()
    
    # 3. 计算大运 (关键升级)
    # 获取运 (Yun) 对象
    yun = lunar.getEightChar().getYun(1) # 1代表男顺女逆的计算逻辑，库会自动处理
    
    # 起运信息
    start_year = yun.getStartYear()
    start_age = yun.getStartAge()
    
    # 获取大运列表 (获取未来10步大运)
    da_yun_arr = yun.getDaYun()
    dayun_str_list = []
    
    # 循环提取大运：年份 + 干支
    for i in range(1, 10): # 通常取前9-10步大运
        dy = da_yun_arr[i]
        # 大运起运年
        dy_year = dy.getStartYear()
        # 大运干支
        dy_ganzhi = dy.getGanZhi()
        dayun_str_list.append(f"{dy_year}年起: 【{dy_ganzhi}】")

    dayun_text = "\n".join(dayun_str_list)

    # 4. 组装成给用户看（也给AI看）的文本
    bazi_text = f"""
【基本信息】
出生公历：{year}年{month}月{day}日 {hour}时
性别：(请在侧边栏确认)

【四柱八字】
年柱：{ganzhi_year}
月柱：{ganzhi_month}
日柱：{ganzhi_day}
时柱：{ganzhi_time}

【起运时间】
出生后 {start_age} 岁起运 (公历 {start_year} 年左右)

【大运排盘】 (年份-大运干支)
{dayun_text}
"""
    return bazi_text.strip()
