from fasthtml.common import *
import random
from collections import deque
import uuid
import json
from matchutils import get_animals_bypath,compare_animal_names,get_all_animals

# css = Style(':root {--pico-font-size:82%,--pico-font-family: Pacifico, cursive; }')
def before(session):
    if not 'sid' in session: session['sid'] = str(uuid.uuid4())
bware = Beforeware(before, skip=[r'/favicon/.ico', r'/static/.*', r'.*\.css', '/data/images/.*'])

app = FastHTMLWithLiveReload(ws_hdr=True,
                            before=bware,
                            pico=False,
                            hdrs=(
                                Script(src="https://cdn.tailwindcss.com"),
                                Link(rel="stylesheet", href="https://cdn.jsdelivr.net/npm/daisyui@4.11.1/dist/full.min.css"),
                                Script(src="autoscroll.js")),
                            )

app.static_route_exts(static_path='.')

# Load JSON data from a file
with open('static/image_references.json', 'r') as file:
    image_data = json.load(file)

IMAGES_NUMBER = 6
random_int = random.randint(1, IMAGES_NUMBER)

# All messages here, but only most recent 12 are stored
messages = deque(maxlen=12)
users = {}

# all players data here
db = database("db/players.db")
players = db.t.players
if players not in db.t:
    players.create(sid=str, nickname=str, logged=bool, score=int, pk="sid")
# Player type def
Player = players.dataclass()

login_redir = RedirectResponse('/login', status_code=303)

@app.get("/")
def home(session):

    # check user session id persist - redirect otherwise 
    player_id = session['sid']
    if player_id not in players:
        return login_redir

    inpHidden = Input(type="hidden", id="prompt2", name="sessionid", value=session['sid'])

    inp = Label(
        Div(
            Input(id="prompt", name="msg", placeholder='Enter a guess', cls='input input-bordered join-item grow'),
            Button("Guess", cls="btn join-item"),
            cls="join"
        ),
        cls='form-control'
    )
 
    return Title("Drakoon"),Div(
                                Div(
                                    P('Can you guess the two animals in this hybrid?', cls='text-3xl font-bold text-center'),
                                    cls='min-h-[100px] flex items-center justify-center'
                                ),
                                cls='gap-2 m-4'
                            ),Div(
                                Div(
                                    render_animals_helper(),
                                    cls='min-h-[100px] sm:text-right text-left text-gray-400'
                                ),
                                Div(
                                    Img(src=f"static/img{random_int}.jpeg",id='picins', cls='rounded-lg border-2 border-gray-600'),
                                    cls='min-h-[100px] flex justify-center'
                                ),
                                Div(
                                    render_updated_score(),
                                    cls='min-h-[100px] '
                                ),
                                cls='grid gap-2 m-4 sm:grid-cols-3'
                            ),Div(
                                Div(cls='min-h-[100px] sm:block hidden'),
                                Div(
                                    Form(Group(inp,inpHidden), ws_send=True, cls=""),
                                    Div(
                                        id='guessLog',
                                        cls="py-2",
                                    ),
                                    hx_ext='ws', ws_connect='ws',
                                    cls='pt-4 ',
                                ),
                                Div(cls='min-h-[100px] sm:block hidden'),
                                cls='grid gap-2 m-4 sm:grid-cols-3'
                            ),render_footer()
    

## RENDERS
def render_footer():
    return Footer(
            A(
                Span('Made with', 
                    style='vertical-align: middle; color: #333;margin-right: 8px;'),
                A(
                    Img(src='https://docs.fastht.ml/logo.svg', 
                        alt='fastHTML', 
                        width='60', 
                        height='60', 
                        style='vertical-align: middle; margin-right: 5px;'),
                    href='https://fastht.ml/',
                    target='_blank'
                ),
                A(
                    Img(src='https://github.githubassets.com/images/modules/logos_page/GitHub-Mark.png', 
                        alt='GitHub', 
                        width='25', 
                        height='25', 
                        style='vertical-align: middle; margin-right: 5px;'),
                    href='https://github.com/iluadd/Drakoon',
                    target='_blank'
                ),
                    target='_blank',
                    style='display: flex; align-items: center; text-decoration: none;'
            ),
            style="position: fixed; bottom: 10px; right: 10px; display: flex; align-items: center; padding: 5px 10px; border-radius: 5px;",
            onmouseover="this.style.backgroundColor='#e0e0e0';",
            onmouseout="this.style.backgroundColor='#ffffff';",
        )


def render_messages(messages):
    # Reverse the messages list
    messages = list(reversed(messages))

    colors=[]
    # green for right guess ,orange on half otherwise red
    for m in messages:
        if 'one' in m: colors.append("orange")
        elif 'not' in m: colors.append("red")
        else: colors.append("green")

    paragraphs = [
        P(m, style=f'color: {color}') for m, color in zip(messages, colors)
    ]
    return Div(*paragraphs, 
                id='guessLog',
                style='text-align: left',
            )

def render_new_pic(img_path):
    return Img(
                src=img_path, 
                id='picins', 
                cls='rounded border border-gray-600',
                hx_swap_oob="outerHTML",
            )

def render_updated_score():
    scores = [
        Li(f"{plr_i[0]} : {plr_i[1]}") 
        for plr_i in db.execute('SELECT NICKNAME, SCORE FROM players WHERE logged=1')
        ]       

    return Div(Ul(*scores), 
                id="score", 
                cls='min-w-[200px] '),

def render_animals_helper():
    paragraphs = [
        Li(f"{animal}") for animal in get_all_animals(image_data)
    ]
    return Div(Ul(*paragraphs), 
                id="animals", 
                cls='min-w-[200px] text-sm'),

## WEB-SOCKET 
async def on_connect(ws, send): 
    users[id(ws)] = send

    players.update(sid=ws.session["sid"], logged=True) # user Login
    for user in users.values():
        await user(render_updated_score())

async def on_disconnect(ws):
    users.pop(id(ws),None)

    players.update(sid=ws.session["sid"], logged=False) # user Logout
    for user in users.values():
        await user(render_updated_score())

@app.ws('/ws', conn=on_connect, disconn=on_disconnect)
async def ws(msg:str, sessionid:str, send):
    # await send(mk_input()) # reset the input field immediately
    messages.append(msg) 
    global random_int
    global score

    current_player = players[sessionid]
    username = current_player.nickname

    is_ok = False

    # check guess
    file_name = f"img{random_int}.jpeg"
    animals = get_animals_bypath(file_name, image_data)
    result = compare_animal_names(msg, animals[0], animals[1])

    if result == "all equal":
        messages[-1] = f"{username} : {messages[-1]} guess right"
        
        current_player.score = current_player.score + 1
        players.update(sid=sessionid,  score=current_player.score)

        random_int = random.randint(1, IMAGES_NUMBER)    #TODO replace with function
        imgpath = f"static/img{random_int}.jpeg"
        is_ok = True

    elif result == "one animal match":
        messages[-1] = f"{username} : {messages[-1]} you guessed one animal"
        
    else:
        messages[-1] = f"{username} : {messages[-1]} guess not right"

    for u in users.values():
        await u(render_messages(messages))
        if is_ok:
            await u(render_new_pic(imgpath))
            await u(render_updated_score())

## LOGIN

@app.get("/login")
def login():
    inpt = Label(
        Div(
            Input(id="log", name="logname", placeholder='Enter your name', cls='input input-bordered w-full max-w-xs join-item'),
            Button("OK", cls="btn join-item"),
            cls="join"
        ),
        cls='form-control w-full max-w-xs'
    )
    return Title("Drakoon"), \
           Div(
                H1('Enter your details to start...', 
                    cls="text-2xl font-bold pb-6"),
                Form(action='/login', method='post')(Group(inpt)),
                cls="mx-auto max-w-sm px-6 pt-20 rounded-box"
               )

@app.post("/login")
def loginname(logname : str, session):
    if not logname or logname.isspace():
        # Return redirect to login page if blank
        return login_redir

    # save name and register
    players.insert(Player(session['sid'], logname, True, score=0))

    return RedirectResponse('/', status_code=303)

serve(reload_includes=["*.css"])