import discord
from discord.ext import commands
import certifi
import cloudscraper  # Cloudflare 우회 세션 생성
import os
import requests
from dotenv import load_dotenv
from bs4 import BeautifulSoup

import time_conversion_system

# certifi로 인증
os.environ["SSL_CERT_FILE"] = certifi.where()

# .env 파일 로드
load_dotenv()

# 환경 변수에서 API Key 가져오기
CA_API_Key = os.getenv("CA_API_Key")
discordBot_Token = os.getenv("discordBot_Token")

# intents 정의
intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix='!', intents=intents)

@bot.event
async def on_ready():
    print("CA_Bot ON!!")

@bot.event
async def on_message(message):
    # 봇 자신의 메시지는 무시
    if message.author == bot.user:
        return

    # 명령어 처리 (기본 커맨드 처리)
    await bot.process_commands(message)

    # /ca 명령 처리
    if message.content.startswith("/ca "):
        CA_id = message.content.replace("/ca ", "").strip()
        
        # CA API: 사용자 id 정보 가져오기
        CA_url = f'https://open.api.nexon.com/ca/v1/id?user_name={CA_id}&world_name=%ED%95%B4%ED%94%BC'
        CA_response = requests.get(CA_url, headers={"x-nxopen-api-key": CA_API_Key})
        if CA_response.status_code != 200:
            await message.channel.send("CA API 호출에 실패했습니다.")
            return

        CA_character_data = CA_response.json()
        CA_ouid = CA_character_data["ouid"]

        # 사용자 기본 정보
        CA_url2 = f'https://open.api.nexon.com/ca/v1/user/basic?ouid={CA_ouid}'
        CA_response2 = requests.get(CA_url2, headers={"x-nxopen-api-key": CA_API_Key})
        if CA_response2.status_code != 200:
            await message.channel.send("기본 정보 API 호출에 실패했습니다.")
            return

        # 길드 정보
        CA_url3 = f'https://open.api.nexon.com/ca/v1/user/guild?ouid={CA_ouid}'
        CA_response3 = requests.get(CA_url3, headers={"x-nxopen-api-key": CA_API_Key})

        # 홈페이지에서 캐릭터 이미지 가져오기 (Cloudflare 우회)
        scraper = cloudscraper.create_scraper()
        CA_img_url = f'https://ca.nexon.com/MyBlock/Information/{CA_id}/0'
        CA_response_url = scraper.get(CA_img_url)
        html = CA_response_url.text

        # BeautifulSoup으로 HTML 파싱
        soup = BeautifulSoup(html, 'html.parser')
        absolute_img_src = None
        avatar_div = soup.find('div', class_='avatar')
        if avatar_div:
            img_tag = avatar_div.find('img')
            if img_tag and img_tag.has_attr('src'):
                absolute_img_src = img_tag['src']
                
                print("passed here!") # for debug

        # JSON 데이터 파싱
        CA_login_data = CA_response2.json()
        CA_ID_birthday = CA_login_data["user_date_create"]
        CA_last_login = CA_login_data["user_date_last_login"]
        CA_last_logout = CA_login_data["user_date_last_logout"]

        CA_guild = CA_response3.json()
        CA_guild_name = CA_guild.get("guild_id") or "길드 X"

        # 온라인 여부 및 아이콘, 메시지 정보 (함수를 한 번만 호출)
        online_status = time_conversion_system.is_online(CA_last_login, CA_last_logout)
        embed_color = 0x00FF00 if online_status["status"] else 0xFF0000

        # 임베드 생성
        embed = discord.Embed(color=embed_color)
        embed.set_author(name=f"{CA_id} [{CA_guild_name}]")
        embed.add_field(
            name=f"{online_status['icon']} {online_status['message']}",
            value="\u200B",
            inline=False
        )
        if absolute_img_src:
            embed.set_image(url=absolute_img_src)
        embed.add_field(
            name="**마지막 로그인 시간!**",
            value=time_conversion_system.format_last_login_message(CA_last_login),
            inline=False
        )
        embed.add_field(
            name="**마지막 로그아웃 시간!**",
            value=time_conversion_system.format_last_logout_message(CA_last_logout),
            inline=False
        )
        embed.add_field(
            name="**이 아이디의 생성 날짜!**",
            value=f"{time_conversion_system.format_ID_birthday_message(CA_ID_birthday)}에 만들어졌어요!",
            inline=False
        )

        await message.channel.send(embed=embed)

bot.run(discordBot_Token)