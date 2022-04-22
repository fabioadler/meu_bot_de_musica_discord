from discord.ext import commands
from discord import FFmpegPCMAudio
from youtube_dl import YoutubeDL
from bs4 import BeautifulSoup as bs
from selenium import webdriver
import os,dotenv,sys,threading,asyncio

dotenv.load_dotenv(dotenv.find_dotenv())

exe = ""
wd = ""

if(sys.platform == "win32"):
    exe = "windows/bin/ffmpeg.exe"
    wd = "msedgedriver.exe"
else:
    exe = "linux/bin/ffmpeg"
    wd = 'edgedriver_linux64/msedgedriver'

chat = 0

async def music(ctx,url):
    await ctx.send(f"Tocando: {url}")
    def tocar():
        ydl = {'format':'bestaudio'}
        FFMPEG_OPTION = {'before_options':'-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5','options':'-vn'}
        with YoutubeDL(ydl) as y:
            info = y.extract_info(url,download=False)
            url2 = info['formats'][0]['url']
            src = FFmpegPCMAudio(url2,**FFMPEG_OPTION,executable=exe)
            ctx.voice_client.play(src)
    t = threading.Thread(target=tocar)
    t.start()
    
    

async def web(ctx,url):
    drive = webdriver.Edge(executable_path=wd)
    drive.get(url)
    await asyncio.sleep(10)
    pag = bs(drive.page_source,'html.parser')
    drive.quit()
    cont_list = pag.find_all('a',{'class','yt-simple-endpoint style-scope ytd-playlist-panel-video-renderer'})
    for c in cont_list:
        num = ((str(c.find('a').text).replace(' ','')).split('\n')[5]).split(':')
        mi = int((int(num[0])*60)+int(num[1]))
        tag = (((((str(c).split(' '))[4]).replace('href=',"")).replace('"','')).split('&')[0])
        ms = 'http://www.youtube.com'+tag
        await ctx.send(f'Tocando {ms}')
        def tocar():
            ydl = {'format':'bestaudio'}
            FFMPEG_OPTION = {'before_options':'-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5','options':'-vn'}
            with YoutubeDL(ydl) as y:
                info = y.extract_info(ms,download=False)
                url2 = info['formats'][0]['url']
                src = FFmpegPCMAudio(url2,**FFMPEG_OPTION,executable=exe)
                ctx.voice_client.play(src)
        
        t = threading.Thread(target=tocar)
        t.start()
        await asyncio.sleep(mi)
        ctx.voice_client.stop()
        await asyncio.sleep(1)
        await ctx.send(f'Terminamos de tocar a musica de uma musica, vamos para a proxima!')
        

bot = commands.Bot("/")

@bot.event
async def on_ready():
    print('Bot de musica on')

@bot.event
async def on_message(message):
    if(message.author != bot.user):
        await bot.process_commands(message)
    else:
        pass

@bot.command(name='entrar')
async def entrar(ctx):
    global chat
    try:
        chat = 1
        canal = ctx.author.voice.channel
        await canal.connect()
    except:
        await ctx.send("Você não está em um chat de voz!")
        chat = 0

@bot.command(name="sair")
async def sair(ctx):
    try:
        await ctx.voice_client.disconnect()
        chat = 0
    except:
        ctx.send("O bot precisa está no canal para poder ser removido!")
        chat = 0

@bot.command(name="play")
async def play(ctx,url):
    if(chat == 1):
        await music(ctx,url)
    else:
        await ctx.send('Adicione o bot no chat de voz antés de dar play!')

@bot.command(name="play_list")
async def play_list(ctx,url):
    if(chat == 1):
        await web(ctx,url)
    else:
        await ctx.send('Adicione o bot no chat de voz antés de dar play!')
    

bot.run(os.getenv('token'))