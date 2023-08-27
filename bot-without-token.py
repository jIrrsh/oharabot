import discord
import re
import asyncio
import dc_api
import os
from datetime import datetime
 
TOKEN = ''
 
 
class MyClient(discord.Client):
    async def on_ready(self):
        print('Logged on as {0}!'.format(self.user))
        print("-----")
        await self.change_presence(status=discord.Status.online, activity=discord.Game("샤이니!"))
 
    async def on_message(self, message):
        if message.author == self.user:
            return

        if ".dcinside.com/" in  message.content: # 채팅에서 디씨 링크 여부 참조
            msg = message.content.replace("&", "/").split("/")
            if msg[2] == "m.dcinside.com": # 모바일 링크였을 경우
                gallname = msg[4]
                postnum = msg[5]

            elif msg[2] == "gall.dcinside.com" and msg[3] == "board": # 메이저 갤러리의 경우
                gallname = msg[5][4:]
                postnum = msg[6][3:]

            elif msg[2] == "gall.dcinside.com" and msg[3] == "mgallery": #마이너 갤러리의 경우
                gallname = msg[6][4:]
                postnum = msg[7][3:]

            print(f"{gallname}, {postnum}")
            nowtime = datetime.now().strftime('%y%m%d-%H%M%S')
            print(nowtime)

            async with dc_api.API() as api: #API 불러오기
                doc = await api.document(board_id=gallname, document_id=postnum)
                image_count = 0 
                comm_count = 0
                async for comm in api.comments(board_id=gallname, document_id=postnum): # 댓글 수 확인
                    comm_count = comm_count + 1 
                for img in doc.images: # 이미지 수 확인
                    if img.src[26] == ".":
                        if image_count == 0:
                            await img.download(f'./images/{gallname}-{nowtime}')
                        image_count = image_count + 1
                print(f"{doc.title}\n{doc.author}({doc.author_id})\n-----") # 제목

            if os.path.isfile(f'./images/{gallname}-{nowtime}.jpg'): # 이미지 확장자 검사
                ext = f'{gallname}-{nowtime}.jpg'
            elif os.path.isfile(f'./images/{gallname}-{nowtime}.png'):
                ext = f'{gallname}-{nowtime}.png'
            elif os.path.isfile(f'./images/{gallname}-{nowtime}.gif'):
                ext = f'{gallname}-{nowtime}.gif'
            elif gallname == "sunshine":
                ext = "zacal1.png" # 이미지가 없을 경우 자짤 선택
            elif gallname == "lilyfever":
                ext = "zacal2.png"
            else:
                ext = "zacal3.png"
                
            sunshine = discord.File(f"./images/{ext}", filename=ext) # 이미지를 디스코드 서버에 업로드해 링크화

            embed=discord.Embed(title=doc.title, url=f"https://m.dcinside.com/board/{gallname}/{postnum}", description=f"텍스트 {len(doc.contents.replace("- dc official App", ""))}자 이미지 {image_count}개", color=0x357df2)
            if len(doc.contents.replace("- dc official App", "")) <= 50: # 글이 50자 이하일 시 본문에서 개행 제거 후 임베드에 포함
                embed.add_field(name='', value=doc.contents.replace("\n", " ").replace("- dc official App", "")) # 임베드 조합
            embed.set_author(name=f"{doc.voteup_count} ⭐    {doc.votedown_count} ⬇️    {comm_count} 💬    {doc.view_count} 👁️")
            embed.set_image(url=f"attachment://{ext}")
            if doc.author_id == None:
                footer = doc.author # footer에 표시될 아이디 선별
            else:
                footer = f"{doc.author}({doc.author_id})"         
            if gallname == "sunshine":
                embed.set_footer(text=f"{footer} - 러브라이브 선샤인 갤러리") # 갤러리명 확인 후 갤러리 태그 부착
            elif gallname == "lilyfever":
                embed.set_footer(text=f"{footer} - 대세는 백합 갤러리")
            else:
                embed.set_footer(text=f"{footer} - {gallname} 갤러리")

            await message.channel.send(embed=embed, file=sunshine)

intents = discord.Intents.default()
intents.message_content = True
client = MyClient(intents=intents)
client.run(TOKEN)