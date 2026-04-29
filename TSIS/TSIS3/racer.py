import pygame, sys, random, time
from pygame.locals import *
from persistence import load_settings, save_settings, load_leaderboard, save_score

# ── Init ──────────────────────────────────────────────────────────────────────
pygame.init()
W, H = 400, 600
FPS  = 60
DISPLAY = pygame.display.set_mode((W, H))
pygame.display.set_caption("Road Racer")
clock = pygame.time.Clock()

# ── Colors ────────────────────────────────────────────────────────────────────
WHITE=(255,255,255); BLACK=(0,0,0); RED=(220,40,40); GOLD=(255,215,0)
GREEN=(50,210,80); GRAY=(150,150,150); DARK=(20,20,20); ACCENT=(255,200,0)
BLUE=(80,140,255)

# ── Fonts ─────────────────────────────────────────────────────────────────────
F_BIG   = pygame.font.SysFont("Verdana", 52, bold=True)
F_MID   = pygame.font.SysFont("Verdana", 26, bold=True)
F_SM    = pygame.font.SysFont("Verdana", 18)
F_XS    = pygame.font.SysFont("Verdana", 14)

# ── Assets ────────────────────────────────────────────────────────────────────
BG         = pygame.transform.scale(pygame.image.load("assets/AnimatedStreet.png").convert(), (W, H))
ENEMY_IMG  = pygame.image.load("assets/Enemy.png").convert_alpha()
PLAYER_IMG = pygame.image.load("assets/Player.png").convert_alpha()
CRASH_SFX  = pygame.mixer.Sound("assets/crash.mp3")

CAR_TINTS  = {"blue":(80,140,255),"red":(220,50,50),"green":(50,200,80),"white":(220,220,220)}
LANES      = [70, 170, 270, 360]
DIFF = {
    "easy":   {"spd":4, "inc":0.3, "enemies":1, "obs_ms":4000},
    "medium": {"spd":5, "inc":0.5, "enemies":2, "obs_ms":2800},
    "hard":   {"spd":7, "inc":0.7, "enemies":3, "obs_ms":1800},
}

cfg = load_settings()

# ── Helpers ───────────────────────────────────────────────────────────────────
def tint(img, rgb):
    # Overlay colour only on non-transparent pixels, preserving alpha
    t = img.copy()
    overlay = pygame.Surface(t.get_size(), pygame.SRCALPHA)
    overlay.fill(rgb + (60,))          # semi-transparent tint layer
    t.blit(overlay, (0,0), special_flags=pygame.BLEND_RGBA_ADD)
    return t

def txt(surface, text, font, color, cx, cy):
    s = font.render(text, True, color); surface.blit(s, s.get_rect(center=(cx,cy)))

def button(surface, rect, label, font, hover=True):
    mx,my = pygame.mouse.get_pos()
    col = (60,60,60) if (hover and rect.collidepoint(mx,my)) else DARK
    pygame.draw.rect(surface, col, rect, border_radius=8)
    pygame.draw.rect(surface, ACCENT, rect, 2, border_radius=8)
    txt(surface, label, font, WHITE, rect.centerx, rect.centery)

def btn_clicked(event, rect):
    return event.type==MOUSEBUTTONDOWN and event.button==1 and rect.collidepoint(event.pos)

def panel(surface, x, y, w, h):
    s = pygame.Surface((w,h), pygame.SRCALPHA); s.fill((0,0,0,170))
    surface.blit(s,(x,y)); pygame.draw.rect(surface,ACCENT,(x,y,w,h),2,border_radius=10)

# ── Scrolling BG ──────────────────────────────────────────────────────────────
class ScrollBG:
    def __init__(self): self.y1=0; self.y2=-H
    def update(self, spd): 
        self.y1+=spd*0.6; self.y2+=spd*0.6
        if self.y1>=H: self.y1=-H
        if self.y2>=H: self.y2=-H
    def draw(self,surf): surf.blit(BG,(0,int(self.y1))); surf.blit(BG,(0,int(self.y2)))

# ── Sprites ───────────────────────────────────────────────────────────────────
MAX_HP = 3   # oil spill / barrier hits before game over

class Player(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.image = tint(PLAYER_IMG, CAR_TINTS.get(cfg["car_color"], CAR_TINTS["blue"]))
        self.rect  = self.image.get_rect(center=(W//2, 560))
        self.shield= False; self.nitro_end=0
        self.hp    = MAX_HP
        self.hit_cd= 0   # cooldown timer (frames) so one obstacle doesn't drain HP instantly
    def move(self):
        k=pygame.key.get_pressed(); spd=8 if time.time()<self.nitro_end else 5
        if k[K_LEFT]  and self.rect.left>10:     self.rect.x-=spd
        if k[K_RIGHT] and self.rect.right<W-10:  self.rect.x+=spd
        if k[K_UP]    and self.rect.top>H//2:    self.rect.y-=spd
        if k[K_DOWN]  and self.rect.bottom<H-10: self.rect.y+=spd

class Car(pygame.sprite.Sprite):
    def __init__(self): 
        super().__init__(); self.image=ENEMY_IMG
        self.rect=self.image.get_rect(center=(random.choice(LANES),-40))
    def update(self, spd):
        self.rect.y+=spd
        if self.rect.top>H+20: self.rect.center=(random.choice(LANES),-40)

class Coin(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.image=pygame.Surface((18,18),pygame.SRCALPHA)
        pygame.draw.circle(self.image,GOLD,(9,9),9)
        pygame.draw.circle(self.image,(180,140,0),(9,9),9,2)
        self.rect=self.image.get_rect(center=(random.choice(LANES),random.randint(-800,-80)))
    def update(self,spd):
        self.rect.y+=spd
        if self.rect.top>H+10: self.rect.center=(random.choice(LANES),-40)

class Obstacle(pygame.sprite.Sprite):
    KINDS=[("oil",1),("pothole",3),("barrier",1)]   # (kind, damage)
    def __init__(self):
        super().__init__()
        self.kind, self.damage = random.choice(self.KINDS)
        self._make()
        self.rect=self.image.get_rect(center=(random.choice(LANES),-60))
    def _make(self):
        if self.kind=="oil":
            self.image=pygame.Surface((52,22),pygame.SRCALPHA)
            pygame.draw.ellipse(self.image,(30,30,100,200),(0,0,52,22))
        elif self.kind=="pothole":
            self.image=pygame.Surface((34,34),pygame.SRCALPHA)
            pygame.draw.circle(self.image,(50,35,15,220),(17,17),17)
            pygame.draw.circle(self.image,(20,15,5,180),(17,17),10)
        else:
            self.image=pygame.Surface((58,16),pygame.SRCALPHA)
            pygame.draw.rect(self.image,(210,50,50,230),(0,0,58,16),border_radius=4)
            for i in range(3): pygame.draw.rect(self.image,GOLD+(255,),(6+i*18,0,10,16),border_radius=2)
    def update(self,spd):
        self.rect.y+=spd
        if self.rect.top>H+30: self.rect.center=(random.choice(LANES),-60)

class PowerUp(pygame.sprite.Sprite):
    KINDS=["nitro","shield","repair"]
    COLS={"nitro":(255,120,20),"shield":(80,180,255),"repair":(50,210,80)}
    def __init__(self):
        super().__init__(); self.kind=random.choice(self.KINDS)
        self.image=pygame.Surface((32,32),pygame.SRCALPHA)
        c=self.COLS[self.kind]
        pygame.draw.rect(self.image,c+(210,),(0,0,32,32),border_radius=7)
        pygame.draw.rect(self.image,(255,255,255,180),(0,0,32,32),2,border_radius=7)
        lbl=F_XS.render(self.kind[0].upper(),True,WHITE)
        self.image.blit(lbl,lbl.get_rect(center=(16,16)))
        self.rect=self.image.get_rect(center=(random.choice(LANES),-50))
        self.born=time.time()
    def update(self,spd):
        self.rect.y+=spd
        if self.rect.top>H+20 or time.time()-self.born>8: self.kill()

# ── Screens ───────────────────────────────────────────────────────────────────
def ask_username():
    name=cfg.get("username",""); bg=ScrollBG()
    while True:
        bg.update(3); bg.draw(DISPLAY)
        ov=pygame.Surface((W,H),pygame.SRCALPHA); ov.fill((0,0,0,160)); DISPLAY.blit(ov,(0,0))
        txt(DISPLAY,"Enter Name",F_MID,ACCENT,W//2,180)
        box=pygame.Rect(80,240,240,44)
        pygame.draw.rect(DISPLAY,(50,50,50),box,border_radius=8)
        pygame.draw.rect(DISPLAY,ACCENT,box,2,border_radius=8)
        txt(DISPLAY,name+"|",F_MID,WHITE,W//2,262)
        txt(DISPLAY,"Press ENTER to start",F_XS,GRAY,W//2,310)
        pygame.display.update(); clock.tick(FPS)
        for e in pygame.event.get():
            if e.type==QUIT: pygame.quit(); sys.exit()
            if e.type==KEYDOWN:
                if e.key==K_RETURN and name.strip():
                    cfg["username"]=name.strip(); save_settings(cfg); return name.strip()
                elif e.key==K_BACKSPACE: name=name[:-1]
                elif len(name)<14 and e.unicode.isprintable(): name+=e.unicode

def main_menu():
    bg=ScrollBG()
    bw,bh=200,44; cx=W//2
    rects={n:pygame.Rect(cx-bw//2,y,bw,bh) for n,y in
           [("play",230),("board",285),("settings",340),("quit",395)]}
    labels={"play":"PLAY","board":"LEADERBOARD","settings":"SETTINGS","quit":"QUIT"}
    while True:
        bg.update(3); bg.draw(DISPLAY)
        ov=pygame.Surface((W,H),pygame.SRCALPHA); ov.fill((0,0,0,140)); DISPLAY.blit(ov,(0,0))
        txt(DISPLAY,"RACER",F_BIG,ACCENT,cx,120)
        txt(DISPLAY,"Dodge · Collect · Survive",F_XS,GRAY,cx,170)
        for k,r in rects.items(): button(DISPLAY,r,labels[k],F_SM)
        pygame.display.update(); clock.tick(FPS)
        for e in pygame.event.get():
            if e.type==QUIT: pygame.quit(); sys.exit()
            for k,r in rects.items():
                if btn_clicked(e,r): return k

def leaderboard_screen():
    board=load_leaderboard(); back=pygame.Rect(W//2-80,545,160,40)
    while True:
        DISPLAY.fill(DARK); panel(DISPLAY,30,70,W-60,460)
        txt(DISPLAY,"TOP 10",F_MID,ACCENT,W//2,45)
        if not board: txt(DISPLAY,"No scores yet",F_SM,GRAY,W//2,290)
        else:
            hdr=F_XS.render(f"{'#':<3}{'Name':<13}{'Score':>7}{'Dist':>7}m",True,ACCENT)
            DISPLAY.blit(hdr,(50,85))
            pygame.draw.line(DISPLAY,ACCENT,(50,105),(350,105),1)
            for i,e in enumerate(board):
                c=GOLD if i==0 else (WHITE if i<3 else GRAY)
                row=F_XS.render(f"{i+1:<3}{e['name']:<13}{e['score']:>7}{e['dist']:>7}",True,c)
                DISPLAY.blit(row,(50,112+i*32))
        button(DISPLAY,back,"BACK",F_SM); pygame.display.update(); clock.tick(FPS)
        for e in pygame.event.get():
            if e.type==QUIT: pygame.quit(); sys.exit()
            if btn_clicked(e,back): return

def settings_screen():
    diffs=["easy","medium","hard"]; cols=["blue","red","green","white"]
    back=pygame.Rect(W//2-80,545,160,40)
    while True:
        DISPLAY.fill(DARK); panel(DISPLAY,30,70,W-60,455)
        txt(DISPLAY,"SETTINGS",F_MID,ACCENT,W//2,45)
        # Sound
        txt(DISPLAY,"Sound:",F_SM,WHITE,130,115)
        sv=pygame.Rect(230,100,120,34); sc=GREEN if cfg["sound"] else RED
        button(DISPLAY,sv,"ON" if cfg["sound"] else "OFF",F_SM,False)
        pygame.draw.rect(DISPLAY,sc,sv,2,border_radius=8)
        # Difficulty
        txt(DISPLAY,"Difficulty:",F_SM,WHITE,115,175)
        pd=pygame.Rect(200,160,30,34); nd=pygame.Rect(340,160,30,34)
        button(DISPLAY,pd,"<",F_SM); button(DISPLAY,nd,">",F_SM)
        txt(DISPLAY,cfg["difficulty"].capitalize(),F_SM,ACCENT,285,177)
        # Car Color
        txt(DISPLAY,"Car Color:",F_SM,WHITE,115,235)
        pc=pygame.Rect(200,220,30,34); nc=pygame.Rect(340,220,30,34)
        button(DISPLAY,pc,"<",F_SM); button(DISPLAY,nc,">",F_SM)
        sw=pygame.Surface((60,28)); sw.fill(CAR_TINTS[cfg["car_color"]])
        DISPLAY.blit(sw,sw.get_rect(center=(285,237)))
        pygame.draw.rect(DISPLAY,ACCENT,sw.get_rect(center=(285,237)),2)
        button(DISPLAY,back,"SAVE & BACK",F_SM); pygame.display.update(); clock.tick(FPS)
        di=diffs.index(cfg["difficulty"]); ci=cols.index(cfg["car_color"])
        for e in pygame.event.get():
            if e.type==QUIT: pygame.quit(); sys.exit()
            if btn_clicked(e,sv): cfg["sound"]=not cfg["sound"]
            if btn_clicked(e,pd): cfg["difficulty"]=diffs[(di-1)%3]
            if btn_clicked(e,nd): cfg["difficulty"]=diffs[(di+1)%3]
            if btn_clicked(e,pc): cfg["car_color"]=cols[(ci-1)%4]
            if btn_clicked(e,nc): cfg["car_color"]=cols[(ci+1)%4]
            if btn_clicked(e,back): save_settings(cfg); return

def game_over_screen(score,coins,dist,name,hp=0):
    save_score(name,score,dist,coins,hp)
    retry=pygame.Rect(W//2-115,430,100,40); menu=pygame.Rect(W//2+15,430,100,40)
    while True:
        DISPLAY.fill(DARK); panel(DISPLAY,40,90,W-80,320)
        txt(DISPLAY,"GAME OVER",F_BIG,RED,W//2,55)
        for i,(k,v,c) in enumerate([("Player",name,WHITE),("Score",str(score),GOLD),
                                     ("Coins",str(coins),GOLD),("Distance",f"{dist}m",GRAY),
                                     ("HP left",str(hp),GREEN if hp>0 else RED)]):
            ks=F_SM.render(k+":",True,GRAY); vs=F_SM.render(v,True,c)
            DISPLAY.blit(ks,(70,115+i*44)); DISPLAY.blit(vs,(W-70-vs.get_width(),115+i*44))
        button(DISPLAY,retry,"RETRY",F_SM); button(DISPLAY,menu,"MENU",F_SM)
        pygame.display.update(); clock.tick(FPS)
        for e in pygame.event.get():
            if e.type==QUIT: pygame.quit(); sys.exit()
            if btn_clicked(e,retry): return "retry"
            if btn_clicked(e,menu):  return "menu"

# ── Game Loop ─────────────────────────────────────────────────────────────────
def run_game(username):
    d=DIFF[cfg.get("difficulty","medium")]
    speed=d["spd"]; SCORE=0; COINS=0; DIST=0.0
    pu_kind=None; pu_end=0

    player=Player()
    enemies=pygame.sprite.Group(*[Car() for _ in range(d["enemies"])])
    coinsg =pygame.sprite.Group(*[Coin() for _ in range(2)])
    obs    =pygame.sprite.Group()
    pups   =pygame.sprite.Group()
    bg=ScrollBG()

    INC_SPD=USEREVENT+1; SPAWN_OBS=USEREVENT+2; SPAWN_PUP=USEREVENT+3
    pygame.time.set_timer(INC_SPD,1000)
    pygame.time.set_timer(SPAWN_OBS,d["obs_ms"])
    pygame.time.set_timer(SPAWN_PUP,6000)

    while True:
        clock.tick(FPS); DIST+=speed*0.018
        for e in pygame.event.get():
            if e.type==QUIT: pygame.quit(); sys.exit()
            if e.type==INC_SPD: speed+=d["inc"]; SCORE+=1
            if e.type==SPAWN_OBS: o=Obstacle(); obs.add(o)
            if e.type==SPAWN_PUP: p=PowerUp(); pups.add(p)

        # Tick down hit cooldown
        if player.hit_cd > 0:
            player.hit_cd -= 1

        player.move()
        enemies.update(speed); coinsg.update(speed)
        obs.update(speed); pups.update(speed)
        bg.update(speed)

        # Safe spawn — don't land on player
        for sp in list(enemies)+list(obs):
            if sp.rect.colliderect(player.rect) and sp.rect.top<0:
                sp.rect.center=(random.choice(LANES),-80)

        # Coin collect
        for c in pygame.sprite.spritecollide(player,coinsg,False):
            COINS+=1; SCORE+=5; c.rect.center=(random.choice(LANES),-40)

        # Power-up collect
        for p in pygame.sprite.spritecollide(player,pups,True):
            if pu_kind: continue  # one at a time
            pu_kind=p.kind
            if p.kind=="nitro":   player.nitro_end=time.time()+4; pu_end=player.nitro_end
            elif p.kind=="shield":player.shield=True; pu_end=time.time()+9999
            elif p.kind=="repair":
                player.hp=min(player.hp+1, MAX_HP)   # repair restores 1 HP
                pu_kind=None  # instant

        if pu_kind and time.time()>pu_end: pu_kind=None; player.shield=False; player.nitro_end=0

        # Enemy collision → instant death (as before)
        if pygame.sprite.spritecollideany(player,enemies):
            if player.shield: player.shield=False; pu_kind=None
            else:
                if cfg["sound"]: CRASH_SFX.play()
                time.sleep(0.4); return SCORE,COINS,int(DIST),player.hp

        # Obstacle collision → damage (oil & barrier lose 1 HP, pothole loses 3)
        hit_obs = pygame.sprite.spritecollide(player, obs, False)
        if hit_obs and player.hit_cd == 0:
            ob = hit_obs[0]
            if player.shield:
                player.shield=False; pu_kind=None
                ob.rect.center=(random.choice(LANES),-60)   # push obstacle away
            else:
                player.hp -= ob.damage
                if cfg["sound"]: CRASH_SFX.play()
                ob.rect.center=(random.choice(LANES),-60)   # push obstacle past the hit
                if player.hp <= 0:
                    time.sleep(0.4); return SCORE,COINS,int(DIST),0
                player.hit_cd = 60  # 1-second cooldown at 60 FPS

        # ── Draw ──────────────────────────────────────────────────────
        bg.draw(DISPLAY)
        for g in (obs,coinsg,enemies,pups): g.draw(DISPLAY)
        if player.shield:  # draw shield ring
            s=pygame.Surface((80,80),pygame.SRCALPHA)
            pygame.draw.ellipse(s,(80,180,255,80),(0,0,80,80))
            pygame.draw.ellipse(s,(80,180,255,200),(0,0,80,80),3)
            DISPLAY.blit(s,s.get_rect(center=player.rect.center))
        # Flash car red briefly when hit (during cooldown start)
        if 30 < player.hit_cd <= 60:
            flash=pygame.Surface(player.image.get_size(), pygame.SRCALPHA)
            flash.fill((255,0,0,100))
            DISPLAY.blit(flash, player.rect)
        DISPLAY.blit(player.image,player.rect)

        # HUD
        DISPLAY.blit(F_SM.render(f"Score:{SCORE}",True,WHITE),(8,8))
        DISPLAY.blit(F_SM.render(f"Coins:{COINS}",True,GOLD),(W-120,8))
        DISPLAY.blit(F_XS.render(f"{int(DIST)}m  spd:{speed:.1f}",True,GRAY),(8,30))

        # Health bar
        hp_col = GREEN if player.hp >= MAX_HP else (GOLD if player.hp == 2 else RED)
        for i in range(MAX_HP):
            hx = W//2 - (MAX_HP*20)//2 + i*22
            hy = 8
            filled = i < player.hp
            pygame.draw.rect(DISPLAY, hp_col if filled else GRAY, (hx, hy, 16, 16), border_radius=3)
            pygame.draw.rect(DISPLAY, WHITE, (hx, hy, 16, 16), 1, border_radius=3)

        if pu_kind:
            rem=max(0,pu_end-time.time()) if pu_end<9990 else 0
            col={"nitro":(255,140,20),"shield":(80,180,255)}.get(pu_kind,GREEN)
            label=f"[{pu_kind.upper()}]"+(f" {rem:.1f}s" if rem>0 else "")
            txt(DISPLAY,label,F_SM,col,W//2,30)
        pygame.display.update()

# ── Entry Point ───────────────────────────────────────────────────────────────
def main():
    username=cfg.get("username","Player")
    while True:
        action=main_menu()
        if action=="quit": pygame.quit(); sys.exit()
        if action=="board": leaderboard_screen(); continue
        if action=="settings": settings_screen(); continue
        if action=="play":
            username=ask_username()
            while True:
                sc,cn,dist,hp=run_game(username)
                if game_over_screen(sc,cn,dist,username,hp)=="menu": break

if __name__=="__main__":
    main()
