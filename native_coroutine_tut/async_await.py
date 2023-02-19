from collections import Awaitable

async def downloader(url):
    return "bobby"

async def download_url(url):
    html = await downloader(url)
    return html

if __name__ == "__main__":
    coro = download_url("http://www.baidu.com")
    coro.send(None)