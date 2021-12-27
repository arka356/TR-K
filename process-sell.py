def processStopLoss(self, jongmok_code):
    jongmok_name = self.getMasterCodeName(jongmok_code)
    if (self.isTradeAvailable() == False):
        print('-1', end='')
        return

    # 예외 처리 리스트이면 종료
    if (jongmok_code in user_setting.EXCEPTION_LIST):
        # print('-2', end = '')
        return

    # 잔고에 없는 종목이면 종료
    if (jongmok_code not in self.jangoInfo):
        # print('-3', end = '')
        return
    current_jango = self.jangoInfo[jongmok_code]

    bunhal_maedo_info_list = current_jango.get('분할매도이력', [])
    bunhal_maesu_info_list = current_jango.get('분할매수이력', [])

    bunhal_maedo_count = len(bunhal_maedo_info_list)
    bunhal_maesu_count = len(bunhal_maesu_info_list)

    first_bunhal_maesu_time_str = bunhal_maesu_info_list[0].split(':')[0]  # 날짜:가격:수량
    first_maeip_price = int(bunhal_maesu_info_list[0].split(':')[1])  # 날짜:가격:수량

    last_bunhal_maesu_time_str = bunhal_maesu_info_list[-1].split(':')[0]  # 날짜:가격:수량
    last_maeip_price = int(bunhal_maesu_info_list[-1].split(':')[1])  # 날짜:가격:수량

    if (
            '손절가' not in current_jango
            or '매매가능수량' not in current_jango
            or '매도호가총잔량' not in current_jango
            or '현재가' not in current_jango
            or '현재가' not in self.upjongInfo['코스닥']
            or '현재가' not in self.upjongInfo['코스피']
            or '분봉' not in self.upjongInfo['코스닥']
            or '분봉' not in self.upjongInfo['코스피']
    ):
        print('-4', end='')
        return

    # 중요: 매도 시 매도 호가가 빠지는 등의 이유로 가격의 왜곡이 생기므로 최우선 매수 호가를 기준 삼지 않는다.
    # 손절시는 current_price 참고
    # 익절시는 maesuHoga1 참고  (치고 올라가기 때문에  매수/매도 호가 괴리가 생기므로 매수호가 기준 )
    current_price = abs(int(current_jango['현재가']))
    maesuHoga1 = abs(int(current_jango['(최우선)매수호가']))
    current_trade_power = abs(float(current_jango['체결강도']))

    # # 매수호가 기준
    # if( jongmok_code in self.kospiCodeList ):
    #     current_price = kw_util.getHogaPrice(current_price, -1, 'kospi')
    # else:
    #     current_price = kw_util.getHogaPrice(current_price, -1, 'kosdaq')

    jangosuryang = int(current_jango['매매가능수량'])
    stop_plus = int(current_jango['이익실현가'])
    stop_loss = int(current_jango['손절가'])
    maeipga = int(current_jango['매입가'])

    updown_percentage = float(current_jango['등락율'])

    time_span = datetime.timedelta(days=1)

    total_maedohoga_amount = int(current_jango['매도호가총잔량'])
    total_maesuhoga_amount = int(current_jango['매수호가총잔량'])

    # 업종 정보 생성
    jongmok_jang_type = ''
    if (jongmok_code in self.kosdaqCodeList):
        jongmok_jang_type = 'kosdaq'
    else:
        jongmok_jang_type = 'kospi'

    _upjong_20_candle_avr = 0
    key_upjong_name = ''
    if (jongmok_jang_type == 'kospi'):
        key_upjong_name = '코스피'
    else:
        key_upjong_name = '코스닥'

    current_upjong_price = abs(round(float(self.upjongInfo[key_upjong_name]['현재가']), 2))
    open_upjong_price = abs(round(float(self.upjongInfo[key_upjong_name]['시가']), 2))

    candle_list = self.upjongInfo[key_upjong_name]['분봉']
    price_list = [abs(round(float(item.split(':')[0]), 2)) for item in candle_list]
    # 분봉데이터는 소숫점 둘째자리까지 표현되는데 * 100 한 값의 문자열임
    _upjong_20_candle_avr = round(((sum(price_list[1:20]) / 100) + current_upjong_price) / 20, 2)

    ##########################################################################################################
    current_time_str = util.cur_time()
    server_hoga_time_str = current_jango['호가시간']
    expected_one_hoga_amount = round(total_maesuhoga_amount) / 10

    _yesterday_date = (self.currentTime - time_span).date()
    _today_date = (self.currentTime).date()

    _today_open_price = abs(int(current_jango['시가']))
    _today_close_price = abs(int(current_jango['현재가']))
    _today_low_price = abs(int(current_jango['저가']))
    _today_high_price = abs(int(current_jango['고가']))
    _today_amount = abs(int(current_jango['누적거래량']))

    maesuHoga1_amount = abs(int(current_jango['매수호가수량1']))
    maesuHoga2_amount = abs(int(current_jango['매수호가수량2']))
    maedoHoga1_amount = abs(int(current_jango['매도호가수량1']))
    maedoHoga2_amount = abs(int(current_jango['매도호가수량2']))

    _yesterday_close_price = int(self.GetMasterLastPrice(jongmok_code))
    _percent = abs(float(current_jango['전일거래량대비(비율)']))
    _yesterday_amount = 0
    if (_percent != 0):
        _yesterday_amount = int(_today_amount / (_percent / 100))

    maedo_type = ""

    first_bunhal_maesu_date_time = datetime.datetime.strptime(first_bunhal_maesu_time_str, '%Y%m%d%H%M%S').date()
    first_bunhal_stoploss_percent = 1.023

    if (_yesterday_date >= first_bunhal_maesu_date_time):
        ##########################################################################################################
        # 분할 매수 스윙 종목
        stop_plus = 99999999
        maedo_type = "(스윙매수기본손절)"


    else:
        ##########################################################################################################
        # 당일 매수 종목
        last_bunhal_maesu_date_time = datetime.datetime.strptime(last_bunhal_maesu_time_str, "%Y%m%d%H%M%S")
        stop_plus = 9999999
        bunhal_maedo_base_amount = 0
        maedo_type = "(당일매수기본손절)"

        # time cut 적용
        time_span = datetime.timedelta(minutes=1)

    ########################################################################################

    isSell = False
    printData = jongmok_code + ' {0:20} '.format(jongmok_name)

    # 손절 / 익절 계산
    isSijanga = False
    sell_amount = jangosuryang

    # 20180410150510 실시간 매수 호가가 0으로 나오는 경우 오류 처리
    if (stop_loss >= current_price and current_price > 0):
        isSijanga = True
        isSell = True
    elif (stop_plus < maesuHoga1):
        isSell = True
    printData += maedo_type

    printData += ' 손절가: {}, 이익실현가: {}, 매입가: {}, 잔고수량: {}, 호가시간: {}, 현재가: {}, 매수호가수량1: {}, 매수호가수량2: {}'.format(
        stop_loss, stop_plus, maeipga, jangosuryang,
        server_hoga_time_str,
        current_price,
        maesuHoga1_amount, maesuHoga2_amount
    )

    order_num = current_jango.get('매도주문번호', '')

    if (isSell == True):
        low_price = current_price * 0.9
        low_price = kw_util.getHogaPrice(low_price, 0, jongmok_jang_type)
        result = self.sendOrder("sell_" + jongmok_code, kw_util.sendOrderScreenNo, objKiwoom.account_list[0],
                                kw_util.dict_order["매도정정"],
                                jongmok_code, sell_amount, low_price, kw_util.dict_order["지정가"], order_num)

        print("S {} 잔고수량: {}, 매도타입: {}, 매도 주문번호:{},  {}".format(
            jongmok_name, jangosuryang, maedo_type, order_num, result), sep="")
        pass