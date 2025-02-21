import os
import asyncio
from crawl4ai import AsyncWebCrawler, BrowserConfig, CrawlerRunConfig, CacheMode
from crawl4ai.extraction_strategy import LLMExtractionStrategy
from pydantic import BaseModel, Field


# async def main():
#     async with AsyncWebCrawler() as crawler:
#         result = await crawler.arun(
#             url="https://elevenlabs.io/careers",
#         )
#         # 将结果保存为 markdown 文件
#         with open('output.md', 'w', encoding='utf-8') as f:
#             f.write(result.markdown)
#         print("内容已保存到 output.md")


class OpenAIModelFee(BaseModel):
    model_name: str = Field(..., description="Name of the OpenAI model.")
    input_fee: str = Field(..., description="Fee for input token for the OpenAI model.")
    output_fee: str = Field(..., description="Fee for output token for the OpenAI model.")

class HotelInfo(BaseModel):
    hotel_name: str = Field(..., description="酒店名称")
    room_type: str = Field(..., description="房间类型")
    price: str = Field(..., description="房间价格")
    amenities: str = Field(..., description="设施服务")
    rating: str = Field(None, description="酒店评分（如果有）")
    location: str = Field(..., description="酒店位置")

async def main():
    browser_config = BrowserConfig(verbose=True)
    run_config = CrawlerRunConfig(
        word_count_threshold=1,
        extraction_strategy=LLMExtractionStrategy(
            provider="openai/gpt-4o-mini", api_token=os.getenv('OPENAI_API_KEY'),
            schema=HotelInfo.schema(),
            extraction_type="schema",
            instruction="""从爬取的网页内容中，提取所有酒店相关的信息。对于每个酒店，提取以下信息：
            - 酒店名称
            - 可用的房间类型
            - 房间价格
            - 主要设施和服务
            - 酒店评分（如果有）
            - 具体位置
            
            提取的JSON格式应该类似这样：
            {
                "hotel_name": "海景大酒店",
                "room_type": "豪华海景双床房",
                "price": "￥888/晚",
                "amenities": "免费WiFi, 游泳池, 健身房, 餐厅",
                "rating": "4.5/5",
                "location": "市中心滨海路123号"
            }
            
            请确保提取所有可见的酒店信息，保持数据的完整性和准确性。""",
            base_url="https://api.zhizengzeng.com/v1",
        ),
        cache_mode=CacheMode.BYPASS,
    )

    async with AsyncWebCrawler(config=browser_config) as crawler:
        result = await crawler.arun(
            url='https://hk.trip.com/hotels/list?city=58&cityName=%E9%A6%99%E6%B8%AF&provinceId=32&countryId=1&checkIn=2025-02-20&checkOut=2025-02-21&lat=0&lon=0&districtId=0&barCurr=HKD&searchType=H&searchWord=%E9%A6%99%E6%B8%AF%E9%BA%97%E6%99%B6%E9%85%92%E5%BA%97',
            config=run_config
        )
        print(result.extracted_content)
        import json
        with open('hotel_info.json', 'w', encoding='utf-8') as f:
            json.dump(result.extracted_content, f, ensure_ascii=False, indent=4)
        print("酒店信息已保存到 hotel_info.json")


if __name__ == "__main__":
    asyncio.run(main())
