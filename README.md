# osuRankListSpider
使用多进程爬虫技术将osu!mania排行榜前10000名(200页)存入mongodb中

之前用asyncio和aiohttp爬取页面太快导致IPBan，所以使用多进程


以下是效率对比(爬取200页*50个表格数据)


osuRankListSpider_mp.py 使用多进程技术 大概用时90秒


async.py 使用异步技术加上request.get()快速获取页面 (可以进一步优化)大概用时60秒

normal.py 正常爬取并存入mongodb 大概用时280s
