from fasthtml.common import *
import random
from collections import deque, defaultdict
import uuid

# css = Style(':root {--pico-font-size:82%,--pico-font-family: Pacifico, cursive; }')
def before(session):
    if not 'sid' in session: session['sid'] = str(uuid.uuid4())
bware = Beforeware(before, skip=[r'/favicon/.ico', r'/static/.*', r'.*\.css', '/data/images/.*'])

app = FastHTML(ws_hdr=True,
                hdrs=(picolink,
                    Link(rel="stylesheet", href="/style.css", type="text/css"),
                    Script(src="autoscroll.js")),
                    before=bware
                )

app.static_route_exts(static_path='.')

data = {"img1" : "plane",
        "img2" : "plane",
        "img3" : "plane",
        "img4" : "plane"}

random_int = random.randint(1, 4)

# All messages here, but only most recent 150 are stored
messages = deque(maxlen=150)
users = {}
user_logs = defaultdict(lambda: False)
user_names = dict()

login_redir = RedirectResponse('/login', status_code=303)


@app.get("/")
def home(session):

    # register a user session
    user_logs[session['sid']]

    if not user_logs[session['sid']]:
        return login_redir


    inp = Input(id="prompt", name="msg", placeholder="Enter a guess")
    inpHidden = Input(type="hidden", id="prompt2", name="username", value=user_names[session['sid']])
    logname = P(user_names[session['sid']])

    return Body(
                Div(
                    Div(
                        Img(src=f"static/img{random_int}.png"),
                        id='pic',
                        cls='block_1'
                        ),
                    Div(
                        Div(
                            id='guessLog',
                            cls='block_2',
                        ),
                        Div(
                            Form(Group(inp,inpHidden, Button('Guess')), ws_send=True),
                                hx_ext='ws', ws_connect='ws',
                                cls='guess-input'
                        ),
                        cls='wrapper_left-blocks'
                    ),
                    cls='main-wrapper',
                ),
            )

def render_messages(messages):

    # green for right guess , otherwise red
    colors=[]
    for m in messages:
        colors.append("red" if 'not' in m else "green")

    paragraphs = [
        P(m, style=f'color: {color}') 
        for m, color in zip(messages, colors)
    ]
    return Div(*paragraphs, 
                id='guessLog',
                cls='block_2',
                style='text-align: left',
            )

def render_new_pic(img_path):
    return Div(
                Img(src=img_path),
                id='pic',
                cls='block_1',
                hx_swap_oob="outerHTML"
            )

def on_connect(ws, send): 
        users[id(ws)] = send


def on_disconnect(ws):users.pop(id(ws),None)

@app.ws('/ws', conn=on_connect, disconn=on_disconnect)
async def ws(msg:str,username:str, send):
    # await send(mk_input()) # reset the input field immediately
    messages.append(msg) 
    global random_int

    is_ok = False
    # check guess
    if data[f'img{random_int}'] == msg:
        messages[-1] = f"{username} : {messages[-1]} guess right"
        random_int = random.randint(1, 4)
        imgpath = f"static/img{random_int}.png"
        is_ok = True

    else:
        messages[-1] = f"{username} : {messages[-1]} guess not right"

    for u in users.values():
        await u(render_messages(messages))
        if is_ok:
            await u(render_new_pic(imgpath))


@app.get("/login")
def login():
    inpt = Input(id="log", name="logname", placeholder="Enter a name")
    button = Button("Ok")
    return Titled(P("Enter your name !"), Form(action='/login', method='post')(Group(inpt, button)))

@app.post("/login")
def loginname(logname : str, session):
    # save name and register
    user_names[session['sid']] = logname
    user_logs[session['sid']] = True

    return RedirectResponse('/', status_code=303)

serve()