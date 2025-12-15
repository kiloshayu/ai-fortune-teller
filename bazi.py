from lunar_python import Solar

def get_bazi_text(year, month, day, hour, gender="男"):
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
    
    # 3. 计算大运 (修复 Bug 核心区域)
    # 性别转换：lunar_python 中 1为男，0为女
    gender_code = 1 if gender == "男" else 0
    
    # 获取运 (Yun) 对象
    yun = lunar.getEightChar().getYun(gender_code)
    
    # 起运信息
    start_year = yun.getStartYear()
    # 【修复】手动计算起运年龄，而不是调用 getStartAge()
    start_age = start_year - year
    
    # 获取大运列表 (获取未来10步大运)
    da_yun_arr = yun.getDaYun()
    dayun_str_list = []
    
    # 循环提取大运：年份 + 干支
    # 注意：da_yun_arr[0] 通常是起运前，从索引 1 开始取大运
    # 为了保险，我们遍历列表并显示
    for i in range(1, len(da_yun_arr)):
        if i > 10: break # 只取前10步
        dy = da_yun_arr[i]
        dy_year = dy.getStartYear()
        dy_ganzhi = dy.getGanZhi()
        dayun_str_list.append(f"{dy_year}年起: 【{dy_ganzhi}】")

    dayun_text = "\n".join(dayun_str_list)

    # 4. 组装文本
    bazi_text = f"""
【基本信息】
出生公历：{year}年{month}月{day}日 {hour}时
性别：{gender}

【四柱八字】
年柱：{ganzhi_year}
月柱：{ganzhi_month}
日柱：{ganzhi_day}
时柱：{ganzhi_time}

【起运时间】
出生后 {start_age} 岁起运 (公历 {start_year} 年左右)

【大运排盘】
{dayun_text}
"""
    return bazi_text.strip()
