from fasthtml.common import *
import random
from collections import deque, defaultdict
import uuid

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

    inpHidden = Input(type="hidden", id="prompt2", name="username", value=user_names[session['sid']])
    logname = P(user_names[session['sid']])
    inp = Label(
        Div(
            Input(id="prompt", name="msg", placeholder='Enter a guess', cls='input input-bordered join-item grow'),
            Button("Guess", cls="btn join-item"),
            cls="join"
        ),
        cls='form-control'
    )

    return Title("Drakoon"), Div(
        H1("Guess the picture! What could it be?", cls="text-2xl font-bold pb-6"),
        Div(
            Img(src=f"static/img{random_int}.png", cls='rounded border border-2 border-gray-600'),
            id='pic'
        ),
        Div(
            Div(
                Form(Group(inp,inpHidden), ws_send=True, cls=""),
                hx_ext='ws', ws_connect='ws',
                cls='pt-4 max-w-lg'
            ),
            Div(
                id='guessLog',
                cls='py-6',
            ),
            cls=''
        ),
        cls='mx-auto max-w-lg px-6 pt-20 rounded-box',
    )

def render_messages(messages):
    # Reverse the messages list
    messages = list(reversed(messages))

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
                cls='py-6',
                style='text-align: left',
            )

def render_new_pic(img_path):
    return Div(
                Img(src=img_path),
                id='pic',
                cls='rounded border border-2 border-gray-600',
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
    inpt = Label(
        Div(
            Input(id="log", name="logname", placeholder='Enter your name', cls='input input-bordered w-full max-w-xs join-item'),
            Button("OK", cls="btn join-item"),
            cls="join"
        ),
        cls='form-control w-full max-w-xs'
    )
    return Title("Drakoon"), Div(H1('Enter your details to start...', cls="text-2xl font-bold pb-6"), Form(action='/login', method='post')(Group(inpt)), cls="mx-auto max-w-sm px-6 pt-20 rounded-box")

@app.post("/login")
def loginname(logname : str, session):
    if not logname or logname.isspace():
        # Return redirect to login page if blank
        return login_redir

    # save name and register
    user_names[session['sid']] = logname
    user_logs[session['sid']] = True

    return RedirectResponse('/', status_code=303)

serve(reload_includes=["*.css"])