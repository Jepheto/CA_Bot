from datetime import datetime, timedelta

def _format_timestamp(timestamp):
    """
    ISO 포맷의 타임스탬프에 9시간을 더한 후,
    "YYYY년 M월 D일 H시 M분" 형식의 문자열로 반환.
    """
    dt = datetime.fromisoformat(timestamp.replace('Z', '+00:00'))
    dt += timedelta(hours=9)
    return f'{dt.year}년 {dt.month}월 {dt.day}일 {dt.hour}시 {dt.minute}분'

def format_last_login_message(timestamp):
    return _format_timestamp(timestamp)

def format_last_logout_message(timestamp):
    return _format_timestamp(timestamp)

def format_ID_birthday_message(timestamp):
    return _format_timestamp(timestamp)

def is_online(last_login, last_logout):
    """
    로그인/로그아웃 시간을 비교하여 사용자의 온라인 여부를 판단.
    
    - 만약 두 시간이 거의 동일(1초 이하 차이)하다면, 현재 접속 중일 가능성이 높다고 간주.
    - 마지막 로그인 시간이 마지막 로그아웃 시간보다 이전이면 오프라인,
      그렇지 않으면 온라인으로 간주.
    """
    if not last_login or not last_logout:
        return {"status": False, "message": "로그인 또는 로그아웃 정보가 없습니다.", "icon": "❌"}

    login_time = datetime.fromisoformat(last_login.replace('Z', '+00:00'))
    logout_time = datetime.fromisoformat(last_logout.replace('Z', '+00:00'))
    diff = (login_time - logout_time).total_seconds()

    if abs(diff) <= 1:
        return {"status": True, "message": "접속 중일 가능성이 높습니다", "icon": "🟢"}
    elif diff < 0:  # 로그인 시간이 로그아웃 시간보다 이전이면 오프라인
        return {"status": False, "message": "오프라인", "icon": "🔴"}
    else:
        return {"status": True, "message": "온라인", "icon": "🟢"}