# Original code & tutorial from Mark Vanstone: https://education.technovisual.co.uk/ff-portfolio/coding-games-with-pygame-zero-part-five-space-invaders-2/

import pgzrun, math, re, time
from random import randint
player = Actor("player", (400, 550))
boss = Actor("boss")
gameStatus = 0 # 0 = game is at main menu/waiting for player name , 1 = game is playing, 2 = game is over
highScore = []

def draw(): # Pygame Zero draw function
    screen.blit('background', (0, 0))
    if gameStatus == 0: # display the title page
        drawCentreText("INVADERS OF SPACE\n\nLeft & Right Arrow keys move\nSpacebar to fire\nUp Arrow to fire Big Laser\n\nType your name then\npress Enter to start\n")
        screen.draw.text(player.name, center=(400, 500), owidth=0.5, ocolor=(255,0,0), color=(0,64,255), fontsize=60)
    if gameStatus == 1: # playing the game
        player.image = player.images[math.floor(player.status/6)]
        player.draw()
        if boss.active: boss.draw()
        drawLasers()
        drawAliens()
        drawBases()
        screen.draw.text(str(score) , topright=(780, 10), owidth=0.5, ocolor=(255,255,255), color=(0,64,255), fontsize=60)
        screen.draw.text("LEVEL " + str(level) , midtop=(400, 10), owidth=0.5, ocolor=(255,255,255), color=(0,64,255), fontsize=60)
        drawLives()
        drawBigLasers()
        drawPowerUps()
        drawShield()
        drawPoints()
        if player.status >= 30: # Has the player's ship finished exploding?
            if player.lives > 0:
                drawCentreText("YOU WERE HIT!\nPress Enter to re-spawn")
            else:
                drawCentreText("GAME OVER!\nPress Enter to continue")
        if len(aliens) == 0:
            drawCentreText("LEVEL CLEARED!\nPress Enter to go to the next level")
    if gameStatus == 2: # Game over show the leaderboard
        drawHighScore()

def drawCentreText(t):
    screen.draw.text(t , center=(400,300), owidth=0.5, ocolor=(255,255,255), color=(255,64,0), fontsize=60)

def update(): # Pygame Zero update function
    global moveCounter, player, gameStatus, lasers, bigLasers, powerUps, level, boss, bossJuke, pointsPopup, pointsYPOS
    if gameStatus == 0:
        if keyboard.RETURN and player.name != "":
            gameStatus = 1
    if gameStatus == 1:
        if player.status < 30 and len(aliens) > 0: # Is the game still active? 
            checkKeys()
            updateLasers()
            updateBoss()
            updatePowerUps()
            updatePoints()
            if moveCounter == 0: updateAliens() # Aliens move, their movement speed increases each level
            moveCounter += 1
            if moveCounter == moveDelay: # TO-DO: moveDelay should be updated each level instead of mid-level, will have better control over difficulty/aliens that way
                moveCounter = 0
            if player.status > 0: # Has the player been hit?  If so, play out 30 frames to give time for the ship explosion animation to finish
                player.status += 1
                if player.status == 30:
                    player.lives -= 1
        else:
            if keyboard.RETURN: 
                if player.lives > 0: # Player respawns and the game continues
                    player.status = 0
                    lasers = [] # clear the screen of all lasers, big lasers, and power ups.  Should the boss be cleared as well, or does that happen somewhere else?
                    bigLasers = []
                    powerUps = []
                    pointsPopup = []
                    pointsYPOS = []
                    if len(aliens) == 0: # Level has been cleared
                        level += 1
                        boss.active = False
                        bossJuke = 450/level # Reduce this number as the levels increase, this keeps the chance of the boss pulling a juke fairly consistent instead of the chances decreasing each level
                        initAliens()
                        initBases()
                else: # Player is out of lives, game over
                    readHighScore()
                    gameStatus = 2
                    writeHighScore()
    if gameStatus == 2:
        if keyboard.ESCAPE:
            init()
            gameStatus = 0

def on_key_down(key):
    global player
    if gameStatus == 0 and key.name != "RETURN":
        if len(key.name) == 1:
            player.name += key.name
        else:
            if key.name == "BACKSPACE":
                player.name = player.name[:-1]

def readHighScore():
    global highScore, score, player
    highScore = []
    try:
        hsFile = open("highscores.txt", "r")
        for line in hsFile:
            highScore.append(line.rstrip())
    except:
        pass
    if score <= 0: 
        scoreSpacing = "                            "
    if score < 1000 and score > 0:
        scoreSpacing = "                       "
    if score >= 1000 and score < 10000:
        scoreSpacing = "                     "
    if score >= 10000 and score < 100000:
        scoreSpacing = "                   "
    if score >= 100000 and score < 1000000:
        scoreSpacing = "                 "
    if score >= 1000000:
        scoreSpacing = "               "
    highScore.append("     " + str(level) + "            " + str(score) + str(scoreSpacing) + player.name)
    highScore.sort(key=natural_key, reverse=True)

def natural_key(string_):
    return [int(s) if s.isdigit() else s for s in re.split(r'(\d+)', string_)]

def writeHighScore():
    global highScore
    hsFile = open("highscores.txt", "w")
    for line in highScore:
        hsFile.write(line + "\n")

def drawHighScore():
    global highScore
    y = 0
    screen.draw.text("TOP SCORES", midtop=(400, 30), owidth=0.5, ocolor=(255,255,255), color=(0,64,255), fontsize=60)
    screen.draw.text("LEVEL    SCORE           NAME", topleft=(10, 90), owidth=0.5, ocolor=(255,255,255), color=(0,64,255), fontsize=60)
    for line in highScore:
        if y < 400:
            screen.draw.text(line, topleft=(10, 150+y), owidth=0.5, ocolor=(0,0,255), color=(255,255,0), fontsize=50)
            y += 50
    screen.draw.text("Press Escape to play again" , center=(400, 550), owidth=0.5, ocolor=(255,255,255), color=(255,64,0), fontsize=60)

def drawLives():
    for l in range(player.lives):
        screen.blit("life", (10+(l*32),10))

def drawBigLasers():
    for l in range (player.bigLaserCount):
        screen.blit("biglaser", (106+(l*13),10)) # X position of 106 gives enough space to draw the Big Laser icons to the right of the player lives.  If I wanted this to be "cleaner" I could replace 106 with 10+(player.lives*32)

def drawAliens():
    for a in range(len(aliens)): aliens[a].draw()

def drawBases():
    for b in range(len(bases)):
        bases[b].drawClipped()

def drawLasers():
    for l in range(len(lasers)): lasers[l].draw()
    for l in range(len(bigLasers)): bigLasers[l].draw()

def drawPowerUps():
    for p in range(len(powerUps)): powerUps[p].draw()

def drawShield():
    if player.shieldActive == 1:
        screen.blit("playershield", (player.x-35, player.y-35))

def drawPoints():
    for p in range(len(pointsPopup)): pointsPopup[p].draw()

def checkKeys(): # Update this function to add a "big" laser or bomb shot or something when the player presses down or up.  Maybe up is a shield, and down is a bomb that travels to the centre of the screen and then explodes
    global player, score
    if keyboard.left:
        if player.x > 40: player.x -= 5
    if keyboard.right:
        if player.x < 760: player.x += 5
    if keyboard.space:
        if player.laserActive == 1:
            sounds.gun.play()
            player.laserActive = 0
            clock.schedule(makeLaserActive, 1.0)
            lasers.append(Actor("laser2", (player.x,player.y-32)))
            lasers[len(lasers)-1].status = 0
            lasers[len(lasers)-1].type = 1
            score -= 100
    if keyboard.up: # Shoot a Big Laser, this laser clips through the bases and doesn't decay when hitting an alien or the boss
        if player.bigLaserCount > 0:
            if player.bigLaserActive == 1:
                sounds.biglaser.play()
                player.bigLaserCount -= 1
                player.bigLaserActive = 0
                clock.schedule(makeBigLaserActive, 1.0)
                bigLasers.append(Actor("laser3", (player.x,player.y-32)))
                bigLasers[len(bigLasers)-1].status = 0
                bigLasers[len(bigLasers)-1].type = 1
                score -= 500 # Shooting a big laser comes with a larger score penalty

def makeLaserActive():
    global player
    player.laserActive = 1

def makeBigLaserActive():
    global player
    player.bigLaserActive = 1

def stopShield():
    global player
    player.shieldActive = 0

def checkBases():
    for b in range(len(bases)):
        if l < len(bases):
            if bases[b].height < 5:
                del bases[b]

def updateLasers():
    global lasers, bigLasers, aliens
    for l in range(len(lasers)):
        if lasers[l].type == 0:
            lasers[l].y += 2
            checkLaserHit(l)
            if lasers[l].y > 600:
                lasers[l].status = 1
        if lasers[l].type == 1:
            lasers[l].y -= 5
            checkPlayerLaserHit(l)
            if lasers[l].y < 10:
                lasers[l].status = 1
    for l in range(len(bigLasers)):
        if bigLasers[l].type == 1:
            bigLasers[l].y -= 8 # Big laser moves faster than the normal player laser
            checkBigLaserHit(l)
            if bigLasers[l].y < 10: # Has the Big Laser left the top of the screen?
                bigLasers[l].status = 1
    lasers = listCleanup(lasers)
    aliens = listCleanup(aliens)
    bigLasers = listCleanup(bigLasers)

def updatePowerUps(): # Scroll the power ups to the bottom of the screen, if they reach the bottom without colliding with the player, they despawn
    global powerUps
    for p in range(len(powerUps)):
        powerUps[p].y += 3 # TO-DO: Make sure that this is a good speed for the powerups to travel at
        checkPowerUpHit(p)
        if powerUps[p].y > 600:
            powerUps[p].status = 1
    powerUps = listCleanup(powerUps)

def updatePoints():
    global pointsPopup, pointsYPOS
    for p in range(min(len(pointsPopup), len(pointsYPOS))):
        pointsPopup[p].y -= 0.5
        if pointsPopup[p].y < pointsYPOS[p] - 30:
            pointsPopup[p].status = 1
    pointsPopup = pointsListCleanup(pointsPopup)

def listCleanup(l):
    newList = []
    for i in range(len(l)):
        if isinstance(l[i], Actor) and l[i].status == 0:
            newList.append(l[i])
    return newList

def pointsListCleanup(l): # Needed a separate function for cleaning up the pointsPopup list as the identical position in the pointsYPOS list needs to be deleted at the same time as a value in pointsPopup
    global pointsYPOS
    newList = []
    for i in range(len(l)):
        if l[i].status == 0:
            newList.append(l[i])
        else:
            del pointsYPOS[i]
    return newList

def checkLaserHit(l):
    global player
    if player.collidepoint((lasers[l].x, lasers[l].y)):
        if player.shieldActive == 1:
            #play a sound?
            lasers[l].status = 1
            stopShield() # Do I also need to cancel the clock timer from checkPowerUpHit()?
        if player.status == 0:
            sounds.explosion.play()
            player.status = 1
            lasers[l].status = 1
    for b in range(len(bases)):
        if bases[b].collideLaser(lasers[l]):
            bases[b].height -= 10
            lasers[l].status = 1

def checkPowerUpHit(p):
    global score, player
    if player.collidepoint((powerUps[p].x, powerUps[p].y)) and player.status == 0: # Player can only collect a power up if their ship isn't currently exploding
        powerUps[p].status = 1
        score += 200
        if powerUps[p].type == 1: # Player has collected a Big Laser power up
            player.bigLaserCount += 1
            #sounds.powerupbl.play() # TO-DO: Need to create this sfx
        if powerUps[p].type == 2: # Player has collected a Shield power up
            if player.shieldActive == 1:
                score += 1000 # Player already has a shield, receives 1000 bonus points
            else:
                player.shieldActive = 1
                # sounds.powerups.play() TO-DO: Add this sfx

def checkPlayerLaserHit(l):
    global score, boss, powerUpSpawn, pointsPopup
    for b in range(len(bases)):
        if bases[b].collideLaser(lasers[l]):
            lasers[l].status = 1
    for a in range(len(aliens)):
        if aliens[a].collidepoint((lasers[l].x, lasers[l].y)):
            lasers[l].status = 1
            aliens[a].status = 1
            createPoints("1kpoints", aliens[a].x, aliens[a].y)
            score += 1000
            powerUpSpawn -= 1
            if powerUpSpawn == 0:
                powerUpSpawn = randint (0,5)+ 5 #This +5 should eventually be replaced with a constant to allow for better tracking/difficulty changes at higher levels
                if randint(0, 5) < 4: # 0, 1, 2, 3 spawn a big laser. 4, 5 spawn a shield
                    powerUps.append(Actor("laserpowerup", (aliens[a].x, aliens[a].y)))
                    powerUps[len(powerUps)-1].status = 0
                    powerUps[len(powerUps)-1].type = 1 # 1 = Big Laser
                else:
                    powerUps.append(Actor("shieldpowerup", (aliens[a].x, aliens[a].y)))
                    powerUps[len(powerUps)-1].status = 0
                    powerUps[len(powerUps)-1].type = 2 # 2 = Shield
    if boss.active:
        if boss.collidepoint((lasers[l].x, lasers[l].y)):
            lasers[l].status = 1
            createPoints("5kpoints", boss.x, boss.y)
            boss.active = 0
            score += 5000

def checkBigLaserHit(l): # The Big Laser doesn't collide with the base segments and doesn't decay if it hits an alien. It continues until it has reached the top of the screen. Aliens don't spawn a power up when hit with the Big Laser
    global score, boss
    for a in range(len(aliens)):
        if aliens[a].collidepoint((bigLasers[l].x, bigLasers[l].y)): # Did the Big Laser hit an alien?
            aliens[a].status = 1
            createPoints("1kpoints", aliens[a].x, aliens[a].y)
            score += 1000 # Should this be higher when using the Big Laser?  Should I add a "combo" effect to landing multiple consecutive hits with the Big Laser?
    if boss.active:
        if boss.collidepoint((bigLasers[l].x, bigLasers[l].y)): # Did the Big Laser hit the boss?
            boss.active = 0
            createPoints("5kpoints", boss.x, boss.y)
            score += 5000 # Should this be higher when using the Big Laser?

def createPoints(t,x,y): # Create a pointsPopup at the location that the alien/boss ship was hit by a laser/Big Laser, track the initial Y position of this popup which will be used to check when to delete it from its list
    pointsPopup.append(Actor(t,(x,y)))
    pointsPopup[len(pointsPopup)-1].status = 0
    pointsYPOS.append(y)

def updateAliens():
    global moveSequence, lasers, moveDelay
    movex = movey = 0
    if moveSequence < 10 or moveSequence > 30:
        movex = -15
    if moveSequence == 10 or moveSequence == 30:
        movey = 40 + (5*level)
        moveDelay -= 1
        if moveDelay < 1: moveDelay = 1 # If moveDelay becomes 0, the game stops
    if moveSequence > 10 and moveSequence < 30:
        movex = 15
    for a in range(len(aliens)):
        animate(aliens[a], pos=(aliens[a].x + movex, aliens[a].y + movey), duration=0.5, tween='linear')
        if randint(0, 1) == 0:
            aliens[a].image = "alien1"
        else:
            aliens[a].image = "alien1b"
            if randint(0, 5) == 0:
                lasers.append(Actor("laser1", (aliens[a].x,aliens[a].y)))
                lasers[len(lasers)-1].status = 0
                lasers[len(lasers)-1].type = 0
                sounds.laser.play()
        if aliens[a].y > 500 and player.status == 0: # Has an alien made it to the bottom of the screen?
            sounds.explosion.play()
            player.status = 1
            player.lives = 1 # The player game overs if this happens
    moveSequence += 1
    if moveSequence == 40: moveSequence = 0

def updateBoss():
    global boss, level, player, lasers
    if boss.active:
        boss.y += (0.3*level) # Note: X and Y coordinates can be decimals, good to know
        if boss.direction == 0:
            boss.x -= (0.5*level) + 1 # Eventually replace this with a constant
        else: boss.x += (0.5*level) + 1
        # add the logic to randomly change boss' direction here, start doing this in level 3.  Is there a better way to do this than an If/Else?
        if level >= 3:
            if randint(0, bossJuke) == 0:
                if boss.direction == 0:
                    boss.direction = 1
        if boss.x < 100: boss.direction = 1 # This lets the boss move left and then right.
        if boss.x > 700: boss.direction = 0
        if boss.y > 500: # Boss has reached the bottom of the screen, player doesn't immediately game over like they do with an alien reaching the bottom
            sounds.explosion.play()
            player.status = 1
            boss.active = False
        if randint(0, 30) == 0:
            lasers.append(Actor("laser1", (boss.x,boss.y)))
            lasers[len(lasers)-1].status = 0
            lasers[len(lasers)-1].type = 0
    else: # TO-DO: Add in the scaling of the size of the boss png based off of the current level number, if that is even possible
        if randint(0, 1200) == 0:
            boss.spawnPoint = randint(0,3) # Boss spawns in at one of four spawn points, chosen randomly
            boss.active = True
            if boss.spawnPoint == 0:
                boss.x = 800
                boss.y = 100
                boss.direction = 0
            if boss.spawnPoint == 1:
                boss.x = 50
                boss.y = 100
                boss.direction = 1
            if boss.spawnPoint == 2:
                boss.x = 300
                boss.y = 25
                boss.direction = randint(0,1) # Choose a random direction of left or right since this spawns boss in the middle of the stage
            if boss.spawnPoint == 3:
                boss.x = 800
                boss.y = 200
                boss.direction = 0

def init():
    global lasers, powerUps, bigLasers, score, player, moveSequence, moveCounter, moveDelay, level, boss, powerUpSpawn, bossJuke, pointsPopup, pointsYPOS
    level = 1
    initAliens()
    initBases()
    moveCounter = moveSequence = player.status = score = player.shieldActive = 0
    lasers = []
    bigLasers = []
    powerUps = []
    pointsPopup = []
    pointsYPOS = []
    boss.active = False
    bossJuke = 450
    player.images = ["player", "explosion1", "explosion2", "explosion3", "explosion4", "explosion4", "explosion5"]
    player.laserActive = player.bigLaserActive = 1 # Big laser is ready to fire
    player.lives = player.bigLaserCount = 3 # The player starts with three Big Lasers to fire
    powerUpSpawn = randint(0,5)+ 5 #This +5 should eventually be replaced with a constant to allow for better tracking/difficulty changes at higher levels
    player.name = ""


def initAliens():
    global aliens, moveCounter, moveSequence, moveDelay, level
    aliens = []
    moveDelay = 30 - level*2 # prevents the game from speeding up at an unreasonable rate.  Can experiment with how much to decrease per level to find a "sweet spot" of difficulty.  Maybe 2*level
    if moveDelay < 1: moveDelay = 1 # If moveDelay becomes 0, the game stops
    moveCounter = moveSequence = 0
    for a in range(18):
        aliens.append(Actor("alien1", (210+(a % 6)*80,100+(int(a/6)*64))))
        aliens[a].status = 0

def drawClipped(self):
    screen.surface.blit(self._surf, (self.x-32, self.y-self.height+30),(0,0,64,self.height))

def collideLaser(self, other):
    return (
        self.x-20 < other.x+5 and
        self.y-self.height+30 < other.y and
        self.x+32 > other.x+5 and
        self.y-self.height+30 + self.height > other.y
    )

def initBases():
    global bases
    bases = []
    bc = 0
    for b in range(3):
        for p in range(3):
            bases.append(Actor("base1", midbottom=(150+(b*200)+(p*40),520)))
            bases[bc].drawClipped = drawClipped.__get__(bases[bc])
            bases[bc].collideLaser = collideLaser.__get__(bases[bc])
            bases[bc].height = 60
            bc += 1

init()
pgzrun.go()