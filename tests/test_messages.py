import pytest
from app.messages import friendly_error

@pytest.mark.parametrize('error,word', [('DRM protected','DRM'),('login required','登录'),('VIP only','会员'),('geo restricted','地区'),('Unsupported URL','不支持'),('Connection timed out','网络'),('ffmpeg missing','合并'),('unknown','日志')])
def test_messages(error, word):
    assert word in friendly_error(error)
