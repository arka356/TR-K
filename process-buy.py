@pyqtSlot()
    def determineBuyProcessBuyStateEntered(self):
        jongmok_info_dict = self.getConditionOccurList()

        # 조건 검색에 걸린 종목도 같이 리스트업 됨
        if (jongmok_info_dict != None):
            # 기본, 실시간 정보 등 필요  정보가 없는 경우 매수 금지
            if (
                    jongmok_info_dict.get('등락율', '') == ''
                    or jongmok_info_dict.get('호가시간', '') == ''
                    or self.upjongInfo['코스피'].get('현재가', '') == ''
                    or self.upjongInfo['코스닥'].get('현재가', '') == ''
            ):
                self.shuffleConditionOccurList()
                self.sigNoWaitTr.emit()
                # print("1", end= '')
                return
        else:
            self.sigNoWaitTr.emit()
            # print("3", end= '')
            return

        if (self.isTradeAvailable() == False):
            # print("4", end= '')
            self.sigNoWaitTr.emit()
            return

        is_log_print_enable = False
        return_vals = []
        printLog = ''

        jongmok_code = jongmok_info_dict['종목코드']
        jongmok_name = jongmok_info_dict['종목명']

        jongmok_jang_type = ''
        if (jongmok_code in self.kosdaqCodeList):
            jongmok_jang_type = 'kosdaq'
        else:
            jongmok_jang_type = 'kospi'

        key_upjong_name = ''
        if (jongmok_jang_type == 'kospi'):
            key_upjong_name = '코스피'
        else:
            key_upjong_name = '코스닥'

        # 매도 호가기준
        current_price = abs(int(jongmok_info_dict['(최우선)매도호가']))
        current_price = kw_util.getHogaPrice(current_price, 0, jongmok_jang_type)

        maesuHoga1 = abs(int(jongmok_info_dict['(최우선)매수호가']))
        open_price = abs(int(jongmok_info_dict['시가']))
        high_price = abs(int(jongmok_info_dict['고가']))
        low_price = abs(int(jongmok_info_dict['저가']))
        total_maedohoga_amount = abs(int(jongmok_info_dict['매도호가총잔량']))
        total_maesuhoga_amount = abs(int(jongmok_info_dict['매수호가총잔량']))
        maesuHoga1_amount = int(jongmok_info_dict['매수호가수량1'])
        maesuHoga2_amount = int(jongmok_info_dict['매수호가수량2'])
        maedoHoga1_amount = int(jongmok_info_dict['매도호가수량1'])
        maedoHoga2_amount = int(jongmok_info_dict['매도호가수량2'])

        # 호가 정보는 문자열로 기준가 대비 + , - 값이 붙어 나옴

        ##########################################################################################################
        # 최근 매수가/분할 매수 횟수  정보 생성
        bunhal_maesu_list = []
        maesu_count = 0

        if (jongmok_code in self.jangoInfo):
            bunhal_maesu_list = self.jangoInfo[jongmok_code].get('분할매수이력', [])
            maesu_count = len(bunhal_maesu_list)

        ##########################################################################################################
        # 전일 종가를 얻기 위한 기준가 정보 생성
        gijunga = int(self.GetMasterLastPrice(jongmok_code))

        ##########################################################################################################
        # 제외 종목인지 확인
        if (jongmok_code in user_setting.EXCEPTION_LIST):
            printLog += "(제외종목)"
            return_vals.append(False)

        ##########################################################################################################
        # 최대 보유 할 수 있는 종목 보유수를 넘었는지 확인
        jango_jongmok_code_list = self.jangoInfo.keys()

        for exception_jongmok_code in user_setting.EXCEPTION_LIST:
            if (exception_jongmok_code in jango_jongmok_code_list):
                jango_jongmok_code_list.remove(exception_jongmok_code)
        if (len(jango_jongmok_code_list) + len(self.maesu_wait_list) < user_setting.MAX_STOCK_POSSESION_COUNT):
            pass
        else:
            if (jongmok_code not in self.jangoInfo):
                printLog += "(종목최대보유중)"
                return_vals.append(False)
                pass
        pass

        ##########################################################################################################
        # 데이트레이딩 중지
        day_trading_end_time = datetime.time(hour=14, minute=59)

        if (self.current_condition_name != '장후반' and self.currentTime.time() > day_trading_end_time):
            printLog += "(데이트레이딩종료)"
            return_vals.append(False)

        ##########################################################################################################
        # 업종 추세가 좋지 않은 경우 매수 금지 장이 좋지 않은 경우 매수 금지

        _upjong_20_candle_avr = 0
        current_upjong_price = abs(round(float(self.upjongInfo[key_upjong_name]['현재가']), 2))
        open_upjong_price = abs(round(float(self.upjongInfo[key_upjong_name]['시가']), 2))

        candle_list = self.upjongInfo[key_upjong_name]['분봉']
        price_list = [abs(round(float(item.split(':')[0]), 2)) for item in candle_list]
        # 분봉데이터는 소숫점 둘째자리까지 표현되는데 * 100 한 값의 문자열임
        _upjong_20_candle_avr = round(((sum(price_list[1:20]) / 100) + current_upjong_price) / 20, 2)

        # if( _upjong_20_candle_avr > current_upjong_price
        #     and self.current_condition_name !='장후반'):
        #     printLog += '(업종추세하락)'
        #     return_vals.append(False)

        # if( open_upjong_price > current_upjong_price
        #     and self.current_condition_name !='장후반'):
        #     printLog += '(업종시가하향)'
        #     return_vals.append(False)

        ##########################################################################################################
        #  추가 매수 횟수 제한
        if (maesu_count < user_setting.BUNHAL_MAESU_LIMIT):
            pass
        else:
            printLog += '(분할매수한계)'
            return_vals.append(False)

        if (jongmok_code in self.jangoInfo):
            if ('매도중' in self.jangoInfo[jongmok_code]):
                printLog += '(매도중)'
                return_vals.append(False)

        ##########################################################################################################
        #  최근 매도 종목 매수 금지

        if (jongmok_code not in self.lastMaedoInfo):
            pass
        else:
            last_maedo_time_str = self.lastMaedoInfo[jongmok_code]["time"]
            last_price = self.lastMaedoInfo[jongmok_code]["price"]
            last_qty = self.lastMaedoInfo[jongmok_code]["qty"]

            time_span = datetime.timedelta(minutes=3)
            current_time = self.currentTime.time()
            last_maedo_time = datetime.datetime.strptime(last_maedo_time_str, "%H%M%S")
            if (current_time < (last_maedo_time + time_span).time()):
                printLog += '(최근매도종목)'
                return_vals.append(False)

        ##########################################################################################################
        #  매수 대기중인 경우
        if (jongmok_code in self.maesu_wait_list):
            printLog += '(매수대기중)'
            return_vals.append(False)

        ##########################################################################################################
        # 불필요한 추가 매수를 막기 위함인 경우
        if (self.maesuProhibitCodeList.count(jongmok_code) == 0):
            pass
        else:
            printLog += '(거래금지종목)'
            return_vals.append(False)

        ##########################################################################################################
        # 종목 등락율을 조건 적용
        #  +, - 붙는 소수이므로 float 으로 먼저 처리
        updown_percentage = float(jongmok_info_dict['등락율'])
        if (updown_percentage > 0 and updown_percentage < 25):
            pass
        else:
            printLog += '(종목등락율미충족: 등락율 {0})'.format(updown_percentage)
            return_vals.append(False)
        pass

        ##########################################################################################################
        # 증거금 조건 적용
        margin_percent = int(jongmok_info_dict['증거금률'])
        margin_key_name = '{}주문가능금액'
        ##########################################################################################################
        # 첫 매수시만 적용되는 조건
        if (jongmok_code not in self.jangoInfo):
            # 시간제약
            # 장 시작시 첫봉은 동시호가 적용이므로 제외, 그 후 1봉은 봐야 되므로 그 시간 이후 매수
            start_time = datetime.time(hour=9, minute=user_setting.REQUEST_MINUTE_CANDLE_TYPE)
            stop_end_time = datetime.time(hour=12, minute=0)
            if (self.currentTime.time() < start_time
                    # or self.currentTime.time() > stop_end_time
            ):
                # print("{} {} ".format(util.cur_time(),  jongmok_name), end= '')
                printLog += '(매수시간미충족)'
                return_vals.append(False)
                pass

            # stoploss 용 실시간 조건 리스트 종목에 걸린 경우
            for jongmok_list in self.conditionStoplossList.values():
                if (jongmok_code in jongmok_list):
                    # print("{} {} ".format(util.cur_time(),  jongmok_name), end= '')
                    printLog += '(매수조건미충족)'
                    return_vals.append(False)
                    break


        ##########################################################################################################
        # 추가 매수시만 적용되는 조건
        else:
            ##########################################################################################################
            # 최근 매입가 대비 비교하여 추매
            time_span = datetime.timedelta(days=1)
            _yesterday_date = (self.currentTime - time_span).date()
            _today_date = self.currentTime.date()

            current_jango = self.jangoInfo[jongmok_code]

            bunhal_maedo_info_list = current_jango.get('분할매도이력', [])
            bunhal_maesu_info_list = current_jango.get('분할매수이력', [])
            maeipga = int(current_jango['매입가'])

            bunhal_maedo_count = len(bunhal_maedo_info_list)
            bunhal_maesu_count = len(bunhal_maesu_info_list)

            first_bunhal_maesu_time_str = bunhal_maesu_info_list[0].split(':')[0]  # 날짜:가격:수량
            first_maeip_price = int(bunhal_maesu_info_list[0].split(':')[1])  # 날짜:가격:수량

            last_bunhal_maesu_time_str = bunhal_maesu_info_list[-1].split(':')[0]  # 날짜:가격:수량
            last_maeip_price = int(bunhal_maesu_info_list[-1].split(':')[1])  # 날짜:가격:수량

            first_bunhal_maesu_date = datetime.datetime.strptime(first_bunhal_maesu_time_str, '%Y%m%d%H%M%S').date()
            last_bunhal_maesu_date = datetime.datetime.strptime(last_bunhal_maesu_time_str, '%Y%m%d%H%M%S').date()

            temp = '({} {})'.format(
                jongmok_name,
                current_price)
            # print( util.cur_time_msec() , temp)
            printLog += temp

            return_vals.append(False)
            pass

        ##########################################################################################################
        # 매수
        # 매도 호가가 0인경우 상한가임
        if (return_vals.count(False) == 0 and current_price != 0):
            qty = 0
            if (user_setting.TEST_MODE == True):
                qty = 1
            else:
                # 기존 테스트 매수 수량을 조절하기 위함
                if (jongmok_code in self.jangoInfo):

                    first_chegyeol_time_str = ""
                    if (len(bunhal_maesu_list)):
                        first_chegyeol_time_str = bunhal_maesu_list[0].split(':')[0]  # 날짜:가격:수량

                    if (first_chegyeol_time_str != ''):
                        base_time = datetime.datetime.strptime("20200806010101", "%Y%m%d%H%M%S")

                        first_maesu_time = datetime.datetime.strptime(first_chegyeol_time_str, "%Y%m%d%H%M%S")
                        total_price = user_setting.MAESU_TOTAL_PRICE[maesu_count]
                        qty = int(total_price / current_price)
                        # if( base_time < first_maesu_time ):
                        #     pass
                    else:
                        pass
                else:
                    # 신규 매수
                    total_price = user_setting.MAESU_TOTAL_PRICE[maesu_count]
                    qty = int(total_price / current_price) + 1

            # result = self.sendOrder("buy_" + jongmok_code, kw_util.sendBuyOrderScreenNo,
            #                     objKiwoom.account_list[0], kw_util.dict_order["신규매수"], jongmok_code,
            #                     qty, 0 , kw_util.dict_order["시장가"], "")
###
            result = self.sendOrder("buy_" + jongmok_code, kw_util.sendBuyOrderScreenNo,
                                    objKiwoom.account_list[0], kw_util.dict_order["신규매수"], jongmok_code,
                                    qty, current_price, kw_util.dict_order["지정가IOC"], "")

            self.addProhibitList(jongmok_code)

            # IOC 로 인해 취소 되는 경우 대비
            QTimer.singleShot(1000, lambda: self.removeProhibitList(jongmok_code))

            printLog = '{} **** [매수수량: {}, 매수가: {}, 매수호가 {}, 매도호가수량1: {}, 매도호가수량2: {}, 매수횟수: {}] ****'.format(
                jongmok_name,
                qty,
                current_price,
                maesuHoga1,
                maedoHoga1_amount,
                maedoHoga2_amount,
                maesu_count
            )
            print(printLog)

            util.save_log(printLog, '매수요청', folder="log")
            self.sigWaitTr.emit()
        else:
            # print(printLog)
            self.sigNoWaitTr.emit()
            pass

        self.shuffleConditionOccurList()

        if (is_log_print_enable):
            util.save_log(printLog, '조건진입', folder="log")
        pass
