# -*- coding:utf-8 -*-

AUTO_TRADING_OPERATION_TIME = [ [ [9, 0], [15, 28] ] ]  # 매도호가 정보의 경우 동시호가 시간에도  올라오므로 주의

# 조건검색식 적용시간
CONDITION_INFO = {
    "danta-buy": {
        "start_time": {
            "hour": 9,
            "minute": 2,
            "second": 0, 
        },
        "end_time": {
            "hour": 14,
            "minute": 50,
            "second": 0,
        }
    },
    "danta-sell": {
        "start_time": {
            "hour": 9,
            "minute": 2,
            "second": 0,
        },
        "end_time": {
            "hour": 14,
            "minute": 55,
            "second": 0,
        }
    }
}

CONDITION_INFO_SELL = {
    "danta-sell": {
        "start_time": {
            "hour": 9,
            "minute": 2,
            "second": 0,
        },
        "end_time": {
            "hour": 14,
            "minute": 50,
            "second": 0,
        }
    }
}

MAESU_UNIT = 200000     # 매수 기본 단위 (매수금액 원)

BUNHAL_MAESU_LIMIT = 5      # 분할 매수 횟수 제한

MAX_STOCK_POSSESION_COUNT = 5       # 제외 종목 리스트 불포함한 최대 종목 보유 수

STOP_LOSS_CALCULATE_DAY = 1         # 최근 ? 일간 특정 가격 기준으로 손절 계산

REQUEST_MINUTE_CANDLE_TYPE = 3          # 운영중 요청할 분봉 종류

MAX_SAVE_CANDLE_COUNT = (STOP_LOSS_CALCULATE_DAY +1) * 140      # 3분봉 기준 저장 분봉 갯수

MAESU_TOTAL_PRICE =         [ MAESU_UNIT * 1,                   MAESU_UNIT * 1,                     MAESU_UNIT * 1,                     MAESU_UNIT * 1]
# 추가 매수 진행시 stoploss 및 stopplus 퍼센티지 변경
# 추가 매수 어느 단계에서든지 손절금액은 확정적이여야 함 
# 세금 수수료 별도 계산  
BASIC_STOP_LOSS_PERCENT = -0.6
STOP_PLUS_PER_MAESU_COUNT = [  10,                             10,                                 10,                                 10           ] 
STOP_LOSS_PER_MAESU_COUNT = [  BASIC_STOP_LOSS_PERCENT,        BASIC_STOP_LOSS_PERCENT,            BASIC_STOP_LOSS_PERCENT,            BASIC_STOP_LOSS_PERCENT ]

EXCEPTION_LIST = [''] # 장기 보유 종목 번호 리스트  ex) EXCEPTION_LIST = ['034220']

###################################################################################################
TEST_MODE = False    # 주의 TEST_MODE 를 True 로 하면 1주 단위로 삼o 


###################################################################################################
# for slack  bot
SLACK_BOT_ENABLED = None
SLACK_BOT_TOKEN = "xoxb-2845065365328-2821363566434"        ### 본인 것으로 수정
SLACK_BOT_CHANNEL = "키움-트레이딩"                                          ### 본인 것으로 수정

###################################################################################################
# for google spread
GOOGLE_SPREAD_AUTH_JSON_FILE = 'gspread-334616-ceeb3906e1a0.json'                  ### 본인 것으로 수정
GOOGLE_SPREAD_SHEET_NAME = 'kiwoombot'                                              ### 본인 것으로 수정