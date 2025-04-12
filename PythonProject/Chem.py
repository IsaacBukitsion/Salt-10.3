#!/usr/bin/env python3
import pygame, sys, os, time, math, random

# Width screen. Pixels
screenWidth = 800
# Height screen
screenHeight = 600

screen = pygame.display.set_mode((screenWidth, screenHeight))

squareSize = 50
# Original upscaled (Frames per second)
fps = 30

enemyList = []
towerList = []
bulletList = []
iconList = []
senderList = []
# initalize empty arrays of items on new map

colors = {  # R,G,B
    'yellow': (255, 255, 0),
    'lime': (0, 255, 0),
    'darkblue': (0, 0, 255),
    'aqua': (0, 255, 255),
    'magenta': (255, 0, 255),
    'purple': (128, 0, 128),
    'green': (97, 144, 0),
    'lavender': (197, 125, 190),
    'brown': (110, 73, 32), }


# Optional music
def play_music(file, volume=0.65, loop=-1):
    pygame.mixer.music.load(file)
    # load music from file mp3
    pygame.mixer.music.set_volume(volume)
    pygame.mixer.music.play(loop)


# comment out if you don't want music

def stop_music(): pygame.mixer.music.stop()


#
def imgLoad(file, size=None):
    image = pygame.image.load(file).convert_alpha()
    return pygame.transform.scale(image, size) if size else image


class Player:
    towers = [  # Name of monkey tower
        'sodium',
        'caesium',
        'francium',
        'lithium',
        'potassium',
        'rubidium']

    def __init__(self):
        self.health = 100
        self.money = 650


player = Player()

class Target:
    enemies = [
        'yellow blob',
        'green blob',
        'purple blob',
        'yellow squid',
        'green squid',
        'purple squid'
        ]




# store images using a dictionary
EnemyImageArray = dict()
TowerImageArray = dict()


def loadImages():

    TowerImageArray.update({
        tower: pygame.transform.scale(
            imgLoad(f'towers/{tower.lower()}.png'),(40, 64))
            for tower in Player.towers})
    EnemyImageArray.update({
            enemy: pygame.transform.scale(
            imgLoad(f'enemies/{enemy.lower()}.png'),(40, 64))
            for enemy in Target.enemies})

def get_angle(a, b):
    return 180 - (math.atan2(b[0] - a[0], b[1] - a[1])) / (math.pi / 180)


class Map:
    # setup map
    def __init__(self):
        self.map = 'monkey lane'
        self.loadmap()

    def loadmap(self):
        self.targets = [(-10,284),(140,280),(165,278),(168,401), (351,402), (348,271), (345,170), (351,140), (580,145), (580,305), (461,309), (463,396), (670,392)]
        self.waves =  [
	        "5*1",
	        "10*1, 2*2",
	        "15*1, 5*2",
	        "20*1, 5*2",
	        "30*1, 5*2",
	        "5*1, 20*2",
	        "25*2",
	        "30*1, 20*2",
	        "20*2, 5*3",
	        "25*3",    #10 wave
	        "15*4",
	        "10*4, 5*5",
	        "15*4, 10*5",
	        "25*4, 20*5",
	        "50*4",
	        "45*5",
	        "20*5, 10*6",
	        "25*5, 15*6",
	        "5*5, 25*6",
	        "40*6",]



    def getmovelist(self):
        self.pathpoints = []
        for i in range(len(self.targets) - 1):
            a, b = self.targets[i:i + 2]
            self.pathpoints += [0]

    def get_background(self):
        # load from background png
        background = imgLoad('maps/Background 10.png')
        background = pygame.transform.scale(background,(700,510))
        background2 = imgLoad('maps/smiley2.png').convert_alpha()
        background2 = pygame.transform.scale(background2, (60, 70))
        background3 = imgLoad('maps/smiley3.png').convert_alpha()
        background3 = pygame.transform.scale(background3, (60, 70))
        for i in range(len(self.targets) - 1):
            pygame.draw.line(background, (0, 0, 0), self.targets[i], self.targets[i + 1])

        return background, background2, background3


mapvar = Map()


class Enemy:
    layers = [  # Name Health Speed CashReward
        ('yellow blob', 1, 1.0, 20),
        ('green blob', 3, 1.0, 10),
        ('purple blob', 5, 1.2, 50),
        ('yellow squid', 5, 3.0, 75),
        ('green squid', 10, 2.0, 100),
        ('purple squid', 20, 2.0, 200), ]

    # initalize enemy
    def __init__(self, layer):
        self.layer = layer
        self.setLayer()
        self.targets = mapvar.targets
        self.pos = list(self.targets[0])
        self.target = 0
        self.next_target()
        self.rect = self.image.get_rect(center=self.pos)
        self.distance = 0
        enemyList.append(self)

    def setLayer(self):
        self.name, self.health, self.speed, self.cashprize = self.layers[self.layer]; self.image = EnemyImageArray[
            self.name]

    def nextLayer(self):
        self.layer -= 1; self.setLayer()

    def next_target(self):
        # check if bloons reached the ending
        if self.target < len(self.targets) - 1:
            self.target += 1;
            t = self.targets[self.target];
            self.angle = 180 - (math.atan2(t[0] - self.pos[0], t[1] - self.pos[1])) / (math.pi / 180)
            self.vx, self.vy = math.sin(math.radians(self.angle)), -math.cos(math.radians(self.angle))
        # end game / player if so (no health)
        else:
            self.kill(); player.health -= (self.layer + 1)

    def hit(self, damage):
        player.money += 1
        self.health -= damage
        if self.health <= 0:
            player.money += self.cashprize
            self.nextLayer() if self.layer > 0 else self.kill()

    def kill(self):
        enemyList.remove(self)

    def move(self, frametime):
        speed = frametime * fps * self.speed
        a, b = self.pos, self.targets[self.target]

        a[0] += self.vx * speed
        #
        a[1] += self.vy * speed

        if (b[0] - a[0]) ** 2 + (b[1] - a[1]) ** 2 <= speed ** 2: self.next_target()
        self.rect.center = self.pos
        self.distance += speed


class Tower:
    def __init__(self, pos):
        self.targetTimer = 0
        self.rect = self.image.get_rect(center=pos)
        towerList.append(self)

    def takeTurn(self, frametime, screen):
        self.startTargetTimer = self.firerate
        self.targetTimer -= frametime
        if self.targetTimer <= 0:
            enemypoint = self.target()
            if enemypoint:
                pygame.draw.line(screen, (255, 255, 255), self.rect.center, enemypoint)
                self.targetTimer = self.startTargetTimer

    def target(self):
        # for each enemy loop
        for enemy in sorted(enemyList, key=lambda i: i.distance, reverse=True):
            if (self.rect.centerx - enemy.rect.centerx) ** 2 + (
                    self.rect.centery - enemy.rect.centery) ** 2 <= self.rangesq:
                self.angle = int(get_angle(self.rect.center, enemy.rect.center))
                self.image = pygame.transform.rotate(self.imagecopy, -self.angle)
                self.rect = self.image.get_rect(center=self.rect.center)
                enemy.hit(self.damage)
                return enemy.rect.center


class createTower(Tower):
    # generate the tower
    def __init__(self, tower, pos, info):
        self.tower = tower
        self.cost, self.firerate, self.range, self.damage = info
        self.rangesq = self.range ** 2

        # set properties (damage, firerate, range)

        self.image = TowerImageArray[tower]
        self.imagecopy = self.image.copy()
        self.angle = 0
        Tower.__init__(self, pos)


class Icon:
    # adjust icons of the towers here
    towers = {  # Cost Fire Rate Range Damage
        'sodium': [215, 1.3, 100, 1],
        'caesium': [360, 0.75, 70, 1],
        'francium': [430, 1.5, 120, 2],
        'lithium': [650, 1.2, 150, 2],
        'potassium': [1000, 0.5, 100, 2],
        'rubidium': [1650, 5.5, 300, 5], }

    #

    def __init__(self, tower):
        # initalize tower and it's properties
        self.tower = tower
        self.cost, self.firerate, self.range, self.damage = self.towers[tower]
        iconList.append(self)
        self.img = pygame.transform.scale(TowerImageArray[tower], (45, 70))
        i = player.towers.index(tower);
        x, y = i % 2, i // 2
        self.rect = self.img.get_rect(x=700 + x * (41 + 6) + 6, y=100 + y * (41 + 6) + 6)


def dispText(screen, wavenum):
    # font = pygame.font.Font('C:/Windows/Fonts/ARCHRISTY.ttf',18)
    font = pygame.font.SysFont('arial', 18)
    # Feel free to change the font here
    h = font.get_height() + 2
    strings = [('Round: %d/%d' % (wavenum, len(mapvar.waves)), (200, 20)),
               (str(player.money), (730, 15)),
               # adjust player values here
               (str(max(player.health, 0)), (730, 45))]
    # set player health
    for string, pos in strings:
        text = font.render(string, 2, (255, 255, 255))
        screen.blit(text, text.get_rect(midleft=pos))

    big_font = pygame.font.SysFont('arial', 28)  # Larger font
    bottom_message = "Press SPACE to start or to continue"
    bottom_text = big_font.render(bottom_message, True, (255, 255, 255))

    # Move it a bit higher from the bottom (e.g. 30px instead of 10px)
    bottom_rect = bottom_text.get_rect(midbottom=(screen.get_width() // 2, screen.get_height() - 30))

    screen.blit(bottom_text, bottom_rect)

# https://realpython.com/lessons/using-blit-and-flip/

# Block Transfer, and .blit() is how you copy the contents of one Surface to another
def drawTower(screen, tower, selected):
    screen.blit(tower.image, tower.rect)
    if tower == selected:
        rn = tower.range
        surface = pygame.Surface((2 * rn, 2 * rn)).convert_alpha();
        surface.fill((0, 0, 0, 0))
        pygame.draw.circle(surface, (0, 255, 0, 85), (rn, rn), rn)
        screen.blit(surface, tower.rect.move((-1 * rn, -1 * rn)).center)

    elif tower.rect.collidepoint(pygame.mouse.get_pos()):
        rn = tower.range
        surface = pygame.Surface((2 * rn, 2 * rn)).convert_alpha();
        surface.fill((0, 0, 0, 0))
        pygame.draw.circle(surface, (255, 255, 255, 85), (rn, rn), rn)
        screen.blit(surface, tower.rect.move((-1 * rn, -1 * rn)).center)


def selectedIcon(screen, selected):
    mpos = pygame.mouse.get_pos()
    # using active mouse position
    image = TowerImageArray[selected.tower]
    rect = image.get_rect(center=mpos)
    screen.blit(image, rect)

    collide = False
    rn = selected.range
    surface = pygame.Surface((2 * rn, 2 * rn)).convert_alpha();
    surface.fill((0, 0, 0, 0))
    pygame.draw.circle(surface, (255, 0, 0, 75) if collide else (0, 0, 255, 75), (rn, rn), rn)
    screen.blit(surface, surface.get_rect(center=mpos))


def selectedTower(screen, selected, mousepos):
    # testing
    selected.genButtons(screen)

    for img, rect, info, infopos, cb in selected.buttonlist:
        screen.blit(img, rect)
        if rect.collidepoint(mousepos): screen.blit(info, infopos)


def drawIcon(screen, icon, mpos, font):
    screen.blit(icon.img, icon.rect)

    if icon.rect.collidepoint(mpos):
        text = font.render("%s Tower (%d)" % (icon.tower, icon.cost), 2, (255, 255, 255))
        textpos = text.get_rect(right=700 - 6, centery=icon.rect.centery)
        screen.blit(text, textpos)


class Sender:
    def __init__(self, wave):
        self.wave = wave;
        self.timer = 0;
        self.rate = 1
        self.enemies = [];
        enemies = mapvar.waves[wave - 1].split(',')
        for enemy in enemies:
            amount, layer = enemy.split('*')
            self.enemies += [eval(layer) - 1] * eval(amount)
        senderList.append(self)

    def update(self, frametime, wave):
        if not self.enemies:
            if not enemyList: senderList.remove(self); wave += 1; player.money += 99 + self.wave
        elif self.timer > 0:
            self.timer -= frametime
        else:
            self.timer = self.rate; Enemy(self.enemies[0]); del self.enemies[0]
        return wave

questions_db = [
    {"question": "Which salt(s) are insoluble in water? \nA. All sodium salts           B. Potassium carbonate \nC. Silver chloride         D. All ammonium salts", "answer": "c"},
    {"question": "Copper (II) Carbonate (CuCo₃) + Nitric Acid (HNO₃) -> \nA. Cu(NO₃)₂           B. (NO₃)₂Cu \nC. NOCu           D. CuHNO","answer": "a"},
    {"question": "Anhydrous salts are non-hydrated salts, \nwhich are often in a _______ state.", "answer": "powdery"},
    {"question": "Water molecules in hydrated salts are called \nwater of _________.", "answer": "crystallisation"},
    {"question": "Descramble the letters. \nriPceionpitat", "answer": "precipitation"},
    {"question": "Descramble the letters. \niatnToirt", "answer": "titration"},
    {"question": "Descramble the letters. \nystilastCnolri", "answer": "crystallisation"},
    {"question": "All carbonates are insoluble. \nTrue/False?", "answer": "false"},
    {"question": "Acid + insoluble carbonate -> salt + water + _____", "answer": "carbon dioxide"},
]

def popup_screen(screen):
    font = pygame.font.SysFont("Arial", 14)
    input_text = ""
    active = True

    box_color = (50, 50, 50)
    text_color = (255, 255, 255)
    input_box_color = (100, 100, 100)

    selected = random.choice(questions_db)
    question = selected["question"]
    correct_answer = selected["answer"]

    popup_rect = pygame.Rect(150, 200, 500, 200)
    input_rect = pygame.Rect(200, 300, 400, 50)

    while active:
        screen.fill((0, 0, 0))

        # Draw popup box (optional)
        pygame.draw.rect(screen, box_color, popup_rect)
        pygame.draw.rect(screen, input_box_color, input_rect)
        pygame.draw.rect(screen, (255, 255, 255), input_rect, 2)

        # Multiple lines
        lines = question.split('\n')
        for i, line in enumerate(lines):
            line_surf = font.render(line, True, text_color)
            screen.blit(line_surf, (popup_rect.x + 20, popup_rect.y + 20 + i * (font.get_height() + 5)))

        # Render input text
        input_surf = font.render(input_text, True, text_color)
        screen.blit(input_surf, (input_rect.x + 10, input_rect.y + 10))

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RETURN:
                    if input_text.strip().lower() == correct_answer:
                        print("Correct!")
                        player.money += 1000
                        active = False
                    else:
                        print("Wrong, imagine. L")
                        active = False
                elif event.key == pygame.K_BACKSPACE:
                    input_text = input_text[:-1]
                else:
                    input_text += event.unicode

        pygame.display.update()


def workEvents(selected, wave, wavenum, speed, screen):
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit(); sys.exit()
        elif event.type == pygame.MOUSEBUTTONUP and event.button == 3:
            selected = None
        elif event.type == pygame.MOUSEBUTTONUP and event.button == 1:

            if selected in towerList:
                selected = None
            elif selected in iconList:
                if player.money >= selected.cost:
                    rect = selected.img.get_rect(center=event.pos)
                    collide = False
                    if not collide: player.money -= selected.cost; selected = createTower(selected.tower, event.pos,
                                                                                          selected.towers[
                                                                                              selected.tower])

            for obj in iconList + (towerList if not selected else []):
                if obj.rect.collidepoint(event.pos): selected = obj; break

        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_SPACE and not enemyList:
                if wave <= len(mapvar.waves):
                    Sender(wave)
                    if wavenum in [5,10,15]:
                        popup_screen(screen)
                    if wavenum < 20:
                        wavenum += 1

                else:
                    imgLoad('images/Untitled_Artwork 5-1.png')

            if event.key == pygame.K_k and selected in towerList: player.money += int(
                selected.cost * 0.9); towerList.remove(selected); selected = None
            if event.key == pygame.K_w and speed < 10: speed += 1
            if event.key == pygame.K_s and speed > 1: speed -= 1
    return selected, wave, wavenum, speed


# main file
def main():
    pygame.init()
    # https://www.pygame.org/docs/ref/pygame.html

    os.environ['SDL_VIDEO_CENTERED'] = '1'
    pygame.display.set_caption('Battles for the salts')
    screen = pygame.display.set_mode((screenWidth, screenHeight))
    clock = pygame.time.Clock()
    font = pygame.font.Font(None, 20)

    mapvar.getmovelist()

    background = pygame.Surface((800, 600));
    background.set_colorkey((0, 0, 0))
    # load values of heart (lives), money (cash to spend), and plank interface
    heart = imgLoad('images/hearts.png')
    heart = pygame.transform.scale(heart,(21,22))
    money = imgLoad('images/moneySign.png')
    money = pygame.transform.scale(money,(21,26))
    plank = pygame.image.load('images/plankBlank.png')
    plank = pygame.transform.scale(plank,(100,30))
    w, h = plank.get_size()
    for y in range(screenHeight // h): background.blit(plank, (screenWidth - w, y * h))
    for y in range(3):
        for x in range(screenWidth // w): background.blit(plank, (x * w, screenHeight - (y + 1) * h))
    background.blit(money, (screenWidth - w + 6, h // 2 - money.get_height() // 2))
    background.blit(heart, (screenWidth - w + 6, h + h // 2 - heart.get_height() // 2))

    level_img, t1, t2 = mapvar.get_background()
    loadImages()
    for tower in player.towers: Icon(tower)
    selected = None
    speed = 3
    wave = 1
    wavenum = 1
    # optional music
    play_music('music/maintheme.mp3')
    # application running
    while True:
        starttime = time.time()
        clock.tick(fps)
        frametime = (time.time() - starttime) * speed
        screen.blit(level_img, (0, 0))
        mpos = pygame.mouse.get_pos()

        if senderList: wave = senderList[0].update(frametime, wave)

        z0, z1 = [], []
        for enemy in enemyList:
            d = enemy.distance
            if d < 580:
                z1 += [enemy]
            elif d < 950:
                z0 += [enemy]
            elif d < 2392:
                z1 += [enemy]
            elif d < 2580:
                z0 += [enemy]
            else:
                z0 += [enemy]

        for enemy in z0: enemy.move(frametime); screen.blit(enemy.image, enemy.rect)
        screen.blit(t1, (0, 0))
        screen.blit(t2, (0, 0))
        for enemy in z1: enemy.move(frametime); screen.blit(enemy.image, enemy.rect)

        for tower in towerList: tower.takeTurn(frametime, screen); drawTower(screen, tower, selected)

        screen.blit(background, (0, 0))

        for icon in iconList: drawIcon(screen, icon, mpos, font)
        selected, wave, wavenum, speed = workEvents(selected, wave, wavenum, speed, screen)
        if selected and selected.__class__ == Icon: selectedIcon(screen, selected)
        dispText(screen, wave)

        pygame.display.flip()


if __name__ == '__main__':
    main()

#space