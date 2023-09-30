import discord
import dc_api
import os
from datetime import datetime, timedelta, timezone
 
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
            option_val = msg[-1].split(" ")[1:]
            msg[-1] = msg[-1].split(" ")[0]
            option = {'image': 0, 'content': False, 'noimage': False, 'nocontent': False, 'zacal': False, 'yesenter': False}

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
            nowtime = datetime.utcnow().astimezone(timezone(timedelta(hours=9))).strftime('%y%m%d-%H%M%S')
            print(nowtime)

            async with dc_api.API() as api: #API 불러오기
                for i in option_val: # 옵션 내용 확인
                    if i[:5] == "-imag":
                        option['image'] = int(i[6:]) - 1
                    if i[:5] == "-cont":
                        option['content'] = True
                    if i[:5] == "-noco":
                        option['nocontent'] = True
                    if i[:5] == "-zaca":
                        option['zacal'] = True
                    if i[:5] == "-noim":
                        option['noimage'] = True
                    if i[:5] == "-yese":
                        option['yesenter'] = True
                        
                doc = await api.document(board_id=gallname, document_id=postnum)
                image_count = 0 
                comm_count = 0
                async for comm in api.comments(board_id=gallname, document_id=postnum): # 댓글 수 확인
                    comm_count = comm_count + 1 
                for img in doc.images: # 이미지 수 확인
                    if img.src[26] == ".":
                        if image_count == option['image']:
                            await img.download(f'./images/{gallname}-{nowtime}')
                        image_count = image_count + 1
                print(f"{doc.title}\n{doc.author}({doc.author_id})\n-----") # 제목

            if os.path.isfile(f'./images/{gallname}-{nowtime}.jpg'): # 이미지 확장자 검사
                ext = f'{gallname}-{nowtime}.jpg'
            elif os.path.isfile(f'./images/{gallname}-{nowtime}.png'):
                ext = f'{gallname}-{nowtime}.png'
            elif os.path.isfile(f'./images/{gallname}-{nowtime}.gif'):
                ext = f'{gallname}-{nowtime}.gif'
            elif option["zacal"]: # 자짤 옵션이 켜져있을 경우 갤 이름으로 자짤 검색
                if os.path.isfile(f"./images/{gallname}.png"):
                    ext = f"{gallname}.png"
                else: # 자짤이 없을 경우 기본 자짤 사용
                    ext = "zacal.png"
            else:
                option["noimage"] = True

            if not option["noimage"]:
                sunshine = discord.File(f"./images/{ext}", filename=ext) # 이미지를 디스코드 서버에 업로드해 링크화

            conwlink = doc.contents.replace("\n", " ").replace("- dc official App", "").strip().split(" ")
            for index in range (0, (len(conwlink)), 1): # 본문에서 링크 제거
                if conwlink[index][:4] == "http":
                    conwlink[index] = ""
            content = " ".join(conwlink).replace("  ", " ").strip()

            embed=discord.Embed(title=doc.title, url=f"https://m.dcinside.com/board/{gallname}/{postnum}", description=f"텍스트 {len(content)}자 이미지 {image_count}개", color=0x357df2)
            if option['nocontent'] == True: # nocontent 옵션이 1일 경우
                print("")
            elif option["yesenter"]:
                embed.add_field(name='', value=doc.contents[:99] + "…")
            elif 0 <= len(content) <= 100 or (option['content'] and len(content) <= 950): # 글 길이가 100자 이하거나 content 옵션이 1이고 글 길이가 950자 이하인 경우
                embed.add_field(name='', value=content)
            elif not option['content']: # 글 길이가 100자 초과하며 content 옵션이 0인 경우
                embed.add_field(name='', value=content[:99] + "…")
            else: # 글 길이가 950자를 초과하며 content 옵션이 1인 경우
                embed.add_field(name='', value=content[:950] + "…")
            embed.set_author(name=f"{doc.voteup_count} ⭐    {doc.votedown_count} ⬇️    {comm_count} 💬    {doc.view_count} 👁️")
            if not option['noimage']: embed.set_image(url=f"attachment://{ext}")
            if doc.author_id == None:
                footer = doc.author # footer에 표시될 아이디 선별
            else:
                footer = f"{doc.author}({doc.author_id})"      

            gallkey = {'sunshine': "러브라이브 선샤인", 
                       'npb': "일본야구", 
                       'lilyfever': "대세는 백합", 
                       'nokanto': "일본여행 - 관동이외", 
                       'bandress': "방도리 성우", 
                       'theardaysvat': "밀리시타 성우", 
                       'alternative_history': "대체역사", 
                       'revuestarlight': "레뷰 스타라이트", 
                       'llstar': "러브라이브! 스쿠스타", 
                       'jr': "일본 철도"
                       }   
            try:
                embed.set_footer(text=f"{footer} - {gallkey[gallname]} 갤러리") # 갤러리명 확인 후 갤러리 태그 부착
            except:
                embed.set_footer(text=f"{footer} - {gallname} 갤러리")

            if option['noimage']: await message.channel.send(embed=embed)
            else: await message.channel.send(embed=embed, file=sunshine)

intents = discord.Intents.default()
intents.message_content = True
client = MyClient(intents=intents)
client.run(TOKEN)
