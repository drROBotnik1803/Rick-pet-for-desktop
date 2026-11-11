
import tkinter as tk
import math
import random
import time
import platform

TRANSPARENT_COLOR = '#ff00ff'   
FPS               = 30
RICK_SCALE        = 1.0         
USE_TRANSPARENT_OVERLAY = True   
WINDOW_WIDTH      = 640
WINDOW_HEIGHT     = 520

QUOTES = [
    "Wubba lubba\ndub dub!",
    "Get schwifty!",
    "Sono il Rick piu'\nintelligente!",
    "MORTY!!",
    "*BURP* ...scienza.",
    "Andiamo Morty!",
    "Existence is pain.",
    "Nobody exists\non purpose.",
    "I'm Pickle Rick!",
    "Peace among worlds!",
    "Oh yeah! Can do!",
    "La vita e' breve.",
    "Ugh, che posto.",
    "Don't think about it.",
    "*BURP*",
    "Questo e' stupido\ne lo faccio lo stesso.",
    "Lick my boots!",
    "We're all gonna die.",
    "Szechuan sauce!!",
    "Grasshopper, it's\noverrated.",
]

MEMOS = [
    "AVVISO SCIENTIFICO:\nRick Sanchez era qui.\nDeal with it.\n\n         - R.S.",
    "NOTA IMPORTANTE:\nIl multiverso e' vasto.\nTu sei piccolo.\n\n         - R.S.",
    "MEMO:\nHai del lavoro da fare?\nNon importa.\nIo sono qui.\n\n         - R.S.",
    "PROMEMORIA:\nSei esistenza casuale\nin un universo caotico.\n\n         - R.S.",
    "AVVISO:\nGrande conquista oggi:\nnon ho distrutto niente.\n\n         - R.S.",
    "NOTA:\nSe leggi questo,\nsei abbastanza stupido\nda meritarmi.\n\n         - R.S.",
]

class Memo(tk.Toplevel):
    def __init__(self, parent, x, y, text):
        super().__init__(parent)
        self.overrideredirect(True)
        self.attributes('-topmost', True)
        self.configure(bg='#f0de1a')

        fnt_title = ('Courier New', 9, 'bold')
        fnt_body  = ('Courier New', 10)

        header = tk.Frame(self, bg='#d4c200', cursor='fleur')
        header.pack(fill='x')
        tk.Label(header, text='📋 NOTA DI RICK', bg='#d4c200',
                 fg='#1a1200', font=fnt_title, pady=3).pack(side='left', padx=6)
        tk.Button(header, text='✕', bg='#c84000', fg='white',
                  font=('Courier New', 8, 'bold'), relief='flat', bd=0,
                  padx=4, command=self.destroy, cursor='hand2').pack(side='right', padx=4)

        tk.Label(self, text=text, bg='#f0de1a', fg='#1a0f00',
                 font=fnt_body, justify='left',
                 padx=14, pady=10).pack()

        self.update_idletasks()
        sw = self.winfo_screenwidth()
        sh = self.winfo_screenheight()
        w  = self.winfo_width()
        h  = self.winfo_height()
        bx = max(0, min(sw - w, x))
        by = max(0, min(sh - h, y))
        self.geometry(f'+{bx}+{by}')

        self._ox = self._oy = 0
        header.bind('<Button-1>',   self._drag_start)
        header.bind('<B1-Motion>',  self._drag)

    def _drag_start(self, e):
        self._ox = e.x_root - self.winfo_x()
        self._oy = e.y_root - self.winfo_y()

    def _drag(self, e):
        self.geometry(f'+{e.x_root - self._ox}+{e.y_root - self._oy}')

class RickPet:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Rick Sanchez - Desktop Pet")

        if USE_TRANSPARENT_OVERLAY and platform.system() == 'Windows':
            try:
                import ctypes
                u32 = ctypes.windll.user32
                self.SW = u32.GetSystemMetrics(78)
                self.SH = u32.GetSystemMetrics(79)
                vx = u32.GetSystemMetrics(76)
                vy = u32.GetSystemMetrics(77)
            except Exception:
                self.SW = self.root.winfo_screenwidth()
                self.SH = self.root.winfo_screenheight()
                vx = 0
                vy = 0

            self.root.overrideredirect(True)
            self.root.geometry(f"{self.SW}x{self.SH}+{vx}+{vy}")
            self.root.configure(bg=TRANSPARENT_COLOR)
            self.root.update_idletasks()

            self._hwnd = self.root.winfo_id()

            try:
                self.root.attributes('-transparentcolor', TRANSPARENT_COLOR)
            except Exception:
                pass

            self.root.attributes('-topmost', True)
            self.root.lift()

            canvas_bg = TRANSPARENT_COLOR
        else:
            self.SW = WINDOW_WIDTH
            self.SH = WINDOW_HEIGHT
            self.root.geometry(f"{self.SW}x{self.SH}+100+100")
            self.root.configure(bg='#101010')
            self.root.resizable(False, False)
            self.root.attributes('-topmost', True)
            self.root.lift()
            self.root.deiconify()

            canvas_bg = self.root['bg']

        self.canvas = tk.Canvas(
            self.root, bg=canvas_bg, highlightthickness=0,
            width=self.SW, height=self.SH
        )
        self.canvas.pack()

        self.rx      = float(self.SW  // 2)
        self.ry      = float(self.SH // 2)
        self.tx      = self.rx
        self.ty      = self.ry
        self.right   = True
        self.frame   = 0
        self.visible = True

        self.state   = 'idle'
        self.st      = 0           

        self.portal_src  = None    
        self.portal_dst  = None
        self.beam_on     = False
        self.beam_end    = (0, 0)

        self.speech   = ''
        self.speech_t = 0          

        self.prints   = []         
        self.print_t  = 0
        self.print_alt = 0

        self.ai_t  = 0
        self.ai_iv = 2500

        self.last_ms = self._ms()

        self.canvas.bind('<Button-1>',        self._lclick)
        self.canvas.bind('<Button-3>',        self._rclick)
        self.canvas.bind('<Double-Button-1>', self._dblclick)
        self.root.bind('<Escape>', lambda _: self.root.destroy())
        self.root.protocol('WM_DELETE_WINDOW', self.root.destroy)

        self._ct_enabled = False

        self._tick()
        self.root.mainloop()

    def _ms(self):
        return int(time.time() * 1000)

    def _rpos(self):
        m = 90
        return (random.randint(m, self.SW - m),
                random.randint(m, self.SH - 130))

    def _attach_to_desktop(self):
        """Attacca la finestra di Rick al desktop di Windows per evitare una finestra separata."""
        try:
            import ctypes
            user32 = ctypes.windll.user32

            progman = user32.FindWindowW('Progman', None)
            result = ctypes.c_ulong()
            user32.SendMessageTimeoutW(
                progman, 0x052C, 0, 0,
                0x0002, 1000, ctypes.byref(result)
            )

            workerw = self._find_workerw()
            if not workerw:
                workerw = progman

            if workerw:
                user32.SetParent(self._hwnd, workerw)
                return True
        except Exception:
            pass
        return False

    def _find_workerw(self):
        import ctypes
        user32 = ctypes.windll.user32
        FindWindowEx = user32.FindWindowExW
        EnumWindows = user32.EnumWindows
        EnumWindowsProc = ctypes.WINFUNCTYPE(
            ctypes.c_bool, ctypes.c_void_p, ctypes.c_void_p
        )

        workerw = ctypes.c_void_p(0)

        def _enum_proc(hwnd, lparam):
            if FindWindowEx(hwnd, 0, 'SHELLDLL_DefView', None):
                w = FindWindowEx(hwnd, 0, 'WorkerW', None)
                if not w:
                    w = FindWindowEx(0, hwnd, 'WorkerW', None)
                workerw.value = w
                return False
            return True

        EnumWindows(EnumWindowsProc(_enum_proc), 0)
        return workerw.value

    def _enable_layered_transparency(self):
        """Imposta la trasparenza con color key su Windows per l'overlay desktop."""
        try:
            import ctypes
            user32 = ctypes.windll.user32
            GWL_EXSTYLE = -20
            WS_EX_LAYERED = 0x00080000
            WS_EX_TOOLWINDOW = 0x00000080
            WS_EX_NOACTIVATE = 0x08000000
            LWA_COLORKEY = 0x00000001

            style = user32.GetWindowLongW(self._hwnd, GWL_EXSTYLE)
            user32.SetWindowLongW(
                self._hwnd, GWL_EXSTYLE,
                style | WS_EX_LAYERED | WS_EX_TOOLWINDOW | WS_EX_NOACTIVATE
            )

            color = int(TRANSPARENT_COLOR[1:3], 16) | (
                int(TRANSPARENT_COLOR[3:5], 16) << 8) | (
                int(TRANSPARENT_COLOR[5:7], 16) << 16)
            user32.SetLayeredWindowAttributes(self._hwnd, color, 0, LWA_COLORKEY)
            return True
        except Exception:
            return False

    def _near_rick(self, ex, ey):
        return abs(ex - self.rx) < 60 and abs(ey - self.ry) < 78

    def _lclick(self, e):
        if self._near_rick(e.x, e.y):
            self._say()
        elif self.state in ('idle', 'walk'):
            self.tx, self.ty = e.x, e.y
            self.state = 'walk'
            self.st    = 0

    def _rclick(self, e):
        if self._near_rick(e.x, e.y):
            self.root.destroy()

    def _dblclick(self, e):
        if not self._near_rick(e.x, e.y) and self.state in ('idle', 'walk'):
            self._tp(e.x, e.y)

    def _say(self):
        self.speech   = random.choice(QUOTES)
        self.speech_t = 4000

    def _memo(self):
        text = random.choice(MEMOS)
        mx   = random.randint(50, self.SW - 280)
        my   = random.randint(50, self.SH - 200)
        Memo(self.root, mx, my, text)

    def _tp(self, tx, ty):
        self.state      = 'tp_aim'
        self.st         = 0
        self.portal_dst = [float(tx), float(ty), 0.0]
        self.portal_src = [float(self.rx), float(self.ry), 0.0]
        self.beam_on    = False
        self.beam_end   = (tx, ty)

    def _update(self, dt):
        self.frame  += 1
        self.st     += dt
        self.ai_t   += dt
        if self.speech_t > 0:
            self.speech_t -= dt
        self.print_t += dt
        self.prints = [(px, py, lf - dt) for px, py, lf in self.prints if lf - dt > 0]

        if self.state == 'idle':
            if self.ai_t > self.ai_iv:
                self.ai_t  = 0
                self.ai_iv = random.randint(1400, 4200)
                r = random.random()
                if   r < 0.28:
                    self.tx, self.ty = self._rpos()
                    self.state = 'walk'; self.st = 0
                elif r < 0.55:
                    self._tp(*self._rpos())
                elif r < 0.78:
                    self._say()
                else:
                    self._memo()

        elif self.state == 'walk':
            dx, dy = self.tx - self.rx, self.ty - self.ry
            d = math.hypot(dx, dy)
            if d < 4:
                self.rx, self.ry = self.tx, self.ty
                self.state = 'idle'; self.st = 0; self.ai_t = 0
                self.ai_iv = random.randint(1200, 3200)
            else:
                spd = 2.8 * RICK_SCALE
                self.rx += dx / d * spd
                self.ry += dy / d * spd
                self.right = dx > 0
                if self.print_t > 370:
                    self.print_t = 0
                    off = 13 if self.print_alt == 0 else -13
                    self.prints.append((
                        self.rx + off * (1 if self.right else -1),
                        self.ry + 53,
                        2400
                    ))
                    self.print_alt ^= 1

        elif self.state == 'tp_aim':
            self.right = self.portal_dst[0] >= self.rx
            if self.st > 650:
                self.state  = 'tp_shoot'; self.st = 0
                self.beam_on = True

        elif self.state == 'tp_shoot':
            prog = min(1.0, self.st / 480)
            self.portal_dst[2] = prog
            if self.st > 380:
                self.portal_src[2] = min(1.0, (self.st - 380) / 320)
                if self.st > 620:
                    self.beam_on = False
            if self.st > 950:
                self.beam_on = False; self.state = 'tp_out'; self.st = 0

        elif self.state == 'tp_out':
            if self.st > 300:
                self.visible = False
                self.portal_src[2] = max(0.0, 1.0 - (self.st - 300) / 250)
            if self.st > 680:
                self.rx, self.ry = self.portal_dst[0], self.portal_dst[1]
                self.portal_src[2] = 0.0
                self.state = 'tp_in'; self.st = 0

        elif self.state == 'tp_in':
            if self.st > 160:
                self.visible = True
            if self.st > 520:
                self.portal_dst[2] = max(0.0, 1.0 - (self.st - 520) / 480)
            if self.st > 1120:
                self.portal_src = None; self.portal_dst = None
                self.visible = True; self.state = 'idle'
                self.st = 0; self.ai_t = 0
                self.ai_iv = random.randint(800, 2200)
                if random.random() > 0.3:
                    self._say()

    def _draw(self):
        c = self.canvas; c.delete('all')

        for px, py, lf in self.prints:
            col = '#00aa44' if lf > 900 else '#004422'
            c.create_oval(px - 5, py - 2, px + 5, py + 5,
                          fill=col, outline='')

        if self.portal_src and self.portal_src[2] > 0.02:
            self._draw_portal(c, *self.portal_src)

        if self.portal_dst and self.portal_dst[2] > 0.02:
            self._draw_portal(c, *self.portal_dst)

        if self.beam_on:
            gx = self.rx + (46 if self.right else -46)
            gy = self.ry - 14
            bx, by = self.beam_end
            c.create_line(gx, gy, bx, by, fill='#003a18', width=8)
            c.create_line(gx, gy, bx, by, fill='#00ff88', width=2,
                          dash=(10, 5))

        if self.visible:
            self._draw_rick(c)

        if self.speech and self.speech_t > 0:
            self._draw_bubble(c, self.rx, self.ry - 78, self.speech)

    def _draw_portal(self, c, x, y, sc):
        s  = sc * RICK_SCALE
        pw = int(64 * s)
        ph = int(100 * s)
        if pw < 4:
            return
        f = self.frame

        for i in range(4, -1, -1):
            ew = pw + i * 8; eh = ph + i * 8
            shades = ['#001206', '#002810', '#00501e', '#008a38', '#00cc55']
            c.create_oval(x - ew, y - eh, x + ew, y + eh,
                          outline=shades[i], width=2)

        c.create_oval(x - pw + 5, y - ph + 5,
                      x + pw - 5, y + ph - 5,
                      fill='#001a0a', outline='')

        rot = f * 4   
        n_arms = 6
        for arm in range(n_arms):
            base_a = math.radians(rot + arm * (360 / n_arms))
            pts = []
            for s_i in range(10):
                t = s_i / 9
                angle = base_a + t * math.pi * 0.65
                r     = t * (pw - 10)
                pts.extend([
                    x + math.cos(angle) * r,
                    y + math.sin(angle) * r * (ph / max(pw, 1))
                ])
            if len(pts) >= 4:
                c.create_line(*pts, fill='#00ee77', width=1, smooth=True)

        c.create_oval(x - pw, y - ph, x + pw, y + ph,
                      outline='#00ff88', width=3)

    def _draw_rick(self, c):
        S  = RICK_SCALE
        x  = int(self.rx)
        y  = int(self.ry)
        fl = 1 if self.right else -1
        f  = self.frame

        bob  = int(math.sin(f * 0.08) * (2.5 * S if self.state == 'walk' else 1.2 * S))
        walk = math.sin(f * 0.25) if self.state == 'walk' else 0
        aim  = self.state in ('tp_aim', 'tp_shoot')

        def mx(ox): return x + int(fl * ox * S)
        def my(oy): return y + int(oy * S) + bob
        def sz(v):  return max(1, int(v * S))

        c.create_oval(x - sz(24), y + sz(46), x + sz(24), y + sz(55),
                      fill='#001500', outline='')

        for ox in [-13, 13]:
            sx = mx(ox)
            c.create_oval(sx - sz(12), my(44), sx + sz(12), my(54),
                          fill='#111111', outline='#000000')

        for i, ox in enumerate([-12, 12]):
            lx  = mx(ox)
            lo  = int(walk * sz(20) * (1 if i == 0 else -1))
            c.create_rectangle(lx - sz(6), my(21) + lo,
                                lx + sz(6), my(45) + lo,
                                fill='#3d72a4', outline='#2a5070', width=1)

        c.create_polygon([
            mx(-21), my(1),
            mx(-19), my(31),
            mx( 19), my(31),
            mx( 21), my(1)
        ], fill='#d0d5e2', outline='#9aa0b2', width=1)
        c.create_line(mx(-5), my(1),  mx(-9), my(31), fill='#aab0c0', width=1)
        c.create_line(mx( 5), my(1),  mx( 9), my(31), fill='#aab0c0', width=1)

        c.create_polygon([
            mx(-8), my(1), mx(8), my(1),
            mx(10), my(19), mx(-10), my(19)
        ], fill='#3e78c8', outline='')

        bax = mx(-21)
        c.create_rectangle(bax - sz(5), my(4), bax + sz(5), my(29),
                           fill='#d0d5e2', outline='#9aa0b2')
        c.create_oval(bax - sz(7), my(25), bax + sz(7), my(37),
                     fill='#e8b830', outline='#c09020')

        ax = mx(21); ay = my(5)
        if aim:
            hx = mx(36); hy = my(-18)
        else:
            hx = mx(27); hy = my(27)

        c.create_line(ax, ay, hx, hy,
                      fill='#d0d5e2', width=sz(9), capstyle='round')
        c.create_oval(hx - sz(7), hy - sz(5),
                      hx + sz(7), hy + sz(8),
                      fill='#e8b830', outline='#c09020')

        gx = hx + fl * sz(5); gy = hy
        c.create_rectangle(gx, gy - sz(5),
                           gx + fl * sz(22), gy + sz(6),
                           fill='#484852', outline='#2a2a34')
        c.create_rectangle(gx + fl * sz(19), gy - sz(3),
                           gx + fl * sz(37), gy + sz(3),
                           fill='#343440', outline='#1a1a22')
        c.create_rectangle(gx + fl * sz(2), gy + sz(4),
                           gx + fl * sz(11), gy + sz(14),
                           fill='#555560', outline='#333333')
        tip_x = gx + fl * sz(39)
        g_col = '#00ff88' if f % 16 < 10 else '#00dd77'
        c.create_oval(tip_x - sz(7), gy - sz(7),
                      tip_x + sz(7), gy + sz(7),
                      fill=g_col, outline='#00aa55', width=2)
        c.create_oval(tip_x - sz(3), gy - sz(3),
                      tip_x + sz(3), gy + sz(3),
                      fill='#bbffdd', outline='')

        c.create_oval(x - sz(19), my(-43),
                      x + sz(19), my(-1),
                      fill='#f0c030', outline='#d0a020')

        hp = [
            mx(-16), my(-28),
            mx(-23), my(-40),
            mx(-19), my(-53),
            mx(-9),  my(-47),
            mx(-5),  my(-56),
            mx(2),   my(-53),
            mx(6),   my(-56),
            mx(13),  my(-50),
            mx(18),  my(-44),
            mx(22),  my(-33),
            mx(17),  my(-26)
        ]
        c.create_polygon(hp, fill='#8fd8ff', outline='#82b4d9', smooth=True, width=1)
        c.create_polygon([
            mx(-14), my(-33),
            mx(-27), my(-59),
            mx(-5),  my(-44)
        ], fill='#8fd8ff', outline='')
        c.create_polygon([
            mx(13),  my(-37),
            mx(27),  my(-58),
            mx(17),  my(-28)
        ], fill='#8fd8ff', outline='')

        for ex_off in [-9, 9]:
            ex = x + int(ex_off * S)
            c.create_oval(ex - sz(7), my(-34),
                          ex + sz(7), my(-22),
                          fill='white', outline='#cccccc')
            c.create_oval(ex - sz(4), my(-33),
                          ex + sz(4), my(-24),
                          fill='#1a62a8', outline='')
            c.create_oval(ex - sz(2), my(-31),
                          ex + sz(2), my(-26),
                          fill='#060610', outline='')
            c.create_oval(ex - sz(5), my(-35),
                          ex - sz(3), my(-33),
                          fill='white', outline='')
            c.create_arc(ex - sz(7), my(-27),
                         ex + sz(7), my(-17),
                         start=198, extent=144,
                         style='arc', outline='#b08010', width=1)

        c.create_line(x - sz(16), my(-37), x - sz(6), my(-39),
                      fill='#888888', width=sz(2), capstyle='round')
        c.create_line(x + sz(6),  my(-39), x + sz(16), my(-37),
                      fill='#888888', width=sz(2), capstyle='round')

        c.create_arc(x - sz(7), my(-14), x + sz(7), my(-7),
                     start=205, extent=130,
                     style='arc', outline='#2a1508', width=sz(2))

        c.create_line(x - sz(2), my(-8), x - sz(2), my(1),
                      fill='#00bb44', width=sz(3), capstyle='round')
        dr = sz(3) + int(abs(math.sin(f * 0.09)) * sz(2))
        c.create_oval(x - sz(2) - dr, my(1),
                      x - sz(2) + dr, my(1) + dr * 2,
                      fill='#00bb44', outline='')

    def _draw_bubble(self, c, x, y, text):
        lines = text.split('\n')
        lh    = int(19 * RICK_SCALE)
        pad   = int(11 * RICK_SCALE)
        fsize = max(9, int(11 * RICK_SCALE))
        font  = ('Courier New', fsize, 'bold')

        bw = max(len(l) for l in lines) * (fsize - 1) + pad * 2
        bh = len(lines) * lh + pad * 2
        bx = max(5, min(self.SW - bw - 5, int(x) - bw // 2))
        by = max(5, int(y) - bh)

        c.create_rectangle(bx + 3, by + 3, bx + bw + 3, by + bh + 3,
                           fill='#000000', outline='')
        c.create_rectangle(bx, by, bx + bw, by + bh,
                           fill='#010f07', outline='#00ff88', width=2)
        c.create_polygon(int(x) - 7, by + bh,
                         int(x),     by + bh + 13,
                         int(x) + 7, by + bh,
                         fill='#010f07', outline='#00ff88')
        for i, line in enumerate(lines):
            c.create_text(bx + pad, by + pad + i * lh,
                          text=line, fill='#00ff88',
                          font=font, anchor='nw')

    def _tick(self):
        now = self._ms()
        dt  = min(now - self.last_ms, 60)
        self.last_ms = now

        self._update(dt)
        self._draw()

        self.root.after(1000 // FPS, self._tick)

if __name__ == '__main__':
    RickPet()
