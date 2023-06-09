from discord.ext import commands
from discord import FFmpegPCMAudio
from youtube_dl import YoutubeDL
from bs4 import BeautifulSoup as bs
import discord,sys,time,dotenv,os,nacl,mysql.connector,threading,asyncio

dotenv.load_dotenv(dotenv.find_dotenv())

exe = ""

if(sys.platform == "win32"):
    exe = "windows/bin/ffmpeg.exe"
else:
    exe = "linux/bin/ffmpeg"

intents = discord.Intents.default()
intents.message_content = True   

def tocar(ctx):
    global channel
    if(channel == True):
        r = db('musica')
        if(r != '' and len(r) >= 1):
            FFMPEG_OPTION = {'before_options':'-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5','options':'-vn'}
            ctx.voice_client.play(FFmpegPCMAudio(r[0][2],**FFMPEG_OPTION,executable=exe))
            rs = db('remove_musica',r[0][0])
            if(rs == 'ok'):
                print('Iniciando a musica')
                return f"Tocando: {r[0][1]}"
            else:
                pass
        else:
            return "Não a mais musicas para tocar"
    else:
        return "O bot não está na call"

channel = False

def db(fun,val='0'):
    con = mysql.connector.connect(host='localhost',user='root',password='',database='bot_musica_discord')
    if(con.is_connected):
        cursor = con.cursor()
        def query_noResult(query):
            cursor.execute(query)
            con.commit()
        def query_return(query):
            cursor.execute(query)
            return cursor.fetchall()
        if(fun == 'musica'):
            return query_return("select * from musicas order by id asc limit 1")
        elif(fun == 'add_musica'):
            vd = YoutubeDL({'format':'bestaudio'})
            vd_info = vd.extract_info(val,download=False)       
            url = vd_info['formats'][0]['url']
            tempo = vd_info['duration']
            title = vd_info['title']
            query_noResult(f"insert into musicas(nome,link,timer) values('{title}','{url}',{tempo})")
            return f"A musica foi adicionada a lista com sucesso - {title}"
        elif(fun == 'remove_musica'):
            query_noResult(f"delete from musicas where id={val}")
            return 'ok'
        else:
            return ''
    else:
        return ''

bot = commands.Bot(command_prefix='/', intents=intents)

@bot.event
async def on_ready():
    print("Oi")

@bot.event
async def on_message(message):
    if(message.author != bot.user):
        await bot.process_commands(message)
    else:
        pass

@bot.command(name='add')
async def add(ctx,message):
    rs = db('add_musica',message)
    if(rs != ''):
        await ctx.send(rs)
    else:
        await ctx.send('Não foi possivel adicionar essa musica')

@bot.command(name='play')
async def play(ctx):
    global channel
    try:
        if(channel != True):
            canal = ctx.message.author.voice.channel
            await canal.connect()
            channel = True
        else:
            pass
        while channel:
            if(ctx.voice_client.is_playing()):
                pass
            else:
                print("Fim da musica")
                d = tocar(ctx)
                if(d == "Não a musicas para tocar"):
                    channel = False
                    await ctx.send(d)
                    await ctx.voice_client.disconnect()
                    break
                else:
                    await ctx.send(d)
            await asyncio.sleep(5)
    except:
        await ctx.send('Você precisa estar em call')

@bot.command(name='stop')
async def sair_voz(ctx):
    global channel
    try:
        channel = False
        if(ctx.voice_client.is_playing()):
            ctx.voice_client.stop()
        else:
            pass
        await ctx.voice_client.disconnect()
    except:
        await ctx.send("O bot precisa está no canal para poder ser removido!")

@bot.command(name='regras')
async def regras(ctx):
    await ctx.send("testando....")


bot.run(os.getenv("token"))