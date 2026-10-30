from app.url_parser import parse_urls

def test_split_and_deduplicate():
    assert parse_urls('https://a.cn/v?a=1&b=2，https://b.cn/\nhttps://a.cn/v?a=1&b=2 www.c.cn') == ['https://a.cn/v?a=1&b=2', 'https://b.cn/', 'https://www.c.cn']

def test_reject_invalid():
    assert parse_urls('文字 ftp://a.cn file:///etc/passwd https:// http://[bad') == []
