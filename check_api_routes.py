import requests

def test_url(url):
    try:
        r = requests.get(f"http://127.0.0.1:5001{url}")
        print(f"URL: {url} | Status: {r.status_code} | Success field: {'success' in r.text}")
    except Exception as e:
        print(f"URL: {url} | Error: {e}")

test_url("/api/opportunities/")
test_url("/api/opportunities")
test_url("/api/referrals/my")
test_url("/api/referrals/incoming")
