# Copyright 2019 by Blackjet
# Graphics done using Aseprite
# Sfx done using BFXR and Audacity
# Code by Jaco van der Walt
# Original game 'Quartet' by Photon Storm

# The source code in this file is released under the MIT license.
# Go to http://opensource.org/licenses/MIT for the full license details.

import upygame as pygame
import urandom as random
import umachine             # For on-screen text
import file as gfx          # Graphics
import audio                # Audio
#import gc

#gc.collect()
#print ("free",gc.mem_free())

# Setup the screen buffer
pygame.display.init(False)
pygame.display.set_palette_16bit([
    000000, 0xdb64, 0xd4ec, 0xe612, 0xf766, 0x65c5, 0x4b25, 0x5b7b, 0x64df, 0xffff, 0x9556, 0x83f0, 0x634c, 0x52a9, 0xa186, 0xd2ac
    
]);
screen = pygame.display.set_mode() # full screen

# Init audio
g_sound = pygame.mixer.Sound()

# Variables
version = 20                    # Version number of current game build

menuSong = ""
gameSong = ""
pauseSong = ""

# Test for real h/w to prevent simulator from hanging
gpioPin = umachine.Pin ( umachine.Pin.EXT2, umachine.Pin.ANALOG_IN )
gpioPinValue = gpioPin.value()
if(gpioPinValue == 0):
    isThisRealHardware = False
else:
    isThisRealHardware = True
    menuSong = "bloids/menuSong.wav"
    gameSong = "bloids/gameSong.wav"
    pauseSong = "dummy123.raw"
    

# Delta timing variables
targetFPS = 40

musicEnabled = True
musicIsPlaying = True
showVersion = False
gameState = 0                   # 0 = MENU, 1 = GAME
gameOver = False                # Is player dead
gameOverPlayed = False          # Boolean for sound played
btnPos = 0                      # Face position
error = False                   # Used if player places facepiece over another
lives = 4           
score = 0
oldScore = 0                    # Used to compare the current score to give the player 3 coins for every 1000 points
totalTimer = 50                 # Timer value
timer = 0                       # Used to show remaining time for each turn in game
TotalCoins = 6
coins = TotalCoins              # Coins are life-savers!
coinSoundPlayed = False
showInstructions = False
keyPressed = False              # keydown prevention
faceWin = False
fullFaceWin = False
cross = False
faceWinArray = [0, 0, 0, 0]
flashCenter = False
flashCenterCounterVal = 12
flashCenterCounter = flashCenterCounterVal
updateFaceResult = False        # Used to check updateFaces() result
boardCleared = False            # When player hits button to clear board
pauseTimerLength = 30
pauseTimer = pauseTimerLength
gameOverPauseTimerLength = 3   # Using the pause timer when it's game over so it counts down the coins to score slower
centerFaceVal = [0, 0]          # Holds the face and piece value to compare to the other 4 boxes where player moves
topFaceVal = [0, 0, 0, 0]       # faceID, topleft, topright, btmleft, btmright
btmFaceVal = [0, 0, 0, 0]
leftFaceVal = [0, 0, 0, 0]
rightFaceVal = [0, 0, 0, 0]

# Methods

# The splash screen logo
class Logo:
    def __init__(self):
        self.logoX = 0
        self.logoY = 0
        
    def drawLogo(self):
        screen.blit(gfx.logo, self.logoX, self.logoY)
        
    def moveLogo(self, x, y):
        self.logoX += x
        self.logoY += y
        
# This is the interface graphics around the faces
class Interface:
    def __init__(self):
        global version
        
        self.x = 0
        self.y = 0
        
    def updateDelta(self, fps):
        global targetFPS, isThisRealHardware
        
        result = 1000 // fps
        
        if (isThisRealHardware == True):
            umachine.wait(1000 // fps)
        else:
            umachine.wait(1000 // result)
        
    # Game version
    def showVersion(self):
        global version
        
        umachine.draw_text(1, 1, "v0." + str(version), 9)
    
    # Draw bg
    def drawInterface(self):
        screen.blit(gfx.interface, self.x, self.y)
        
    # Draw instructions
    def showInstructions(self):
        screen.blit(gfx.instructions, self.x, self.y)
        
    # Draw all stats
    def drawStats(self):
        global lives, score
        
        if (score < 10):
            umachine.draw_text(7, 13, "000" + str(score), 9)
            
        elif (score < 100):
            umachine.draw_text(7, 13, "00" + str(score), 9)
            
        elif (score < 1000):
            umachine.draw_text(7, 13, "0" + str(score), 9)
            
        else:
            umachine.draw_text(7, 13, str(score), 9)
        
        # Lives
        umachine.draw_text(85, 13, str(lives), 9)
        
        # Time
        umachine.draw_text(15, 76, str(timer), 9)
        
        # Coins
        umachine.draw_text(90, 76, str(coins), 9)
        
    # Reset stats for a new game
    def reset(self):
        global score, lives, timer, totalTimer, gameOver, coins, menuSong, gameSong
        global topFaceVal, btmFaceVal, leftFaceVal, rightFaceVal
        
        score = 0
        lives = 3
        coins = TotalCoins
        timer = totalTimer
        topFaceVal = [0, 0, 0, 0]
        btmFaceVal = [0, 0, 0, 0]
        leftFaceVal = [0, 0, 0, 0]
        rightFaceVal = [0, 0, 0, 0]
        faceWin = False
        fullFaceWin = False
        cross = False
        gameOver = False
        
    # Play sfx
    def playMove(self):
        g_sound.play_sfx(audio.moveSound, len(audio.moveSound), False)
        
    def playFullFace(self):
        g_sound.play_sfx(audio.fullfaceSound, len(audio.fullfaceSound), False)
        
    def playFace(self):
        g_sound.play_sfx(audio.faceSound, len(audio.faceSound), False)
        
    def playCross(self):
        g_sound.play_sfx(audio.crossSound, len(audio.crossSound), False)
        
    def playGameOver(self):
        g_sound.play_sfx(audio.gameoverSound, len(audio.gameoverSound), False)
        
    def playCoin(self):
        g_sound.play_sfx(audio.coinSound, len(audio.coinSound), False)
        
    def playClear(self):
        g_sound.play_sfx(audio.clearSound, len(audio.clearSound), False)
        
    def stopMusic(self):
        global isThisRealHardware
        
        if (isThisRealHardware == True):
            g_sound.play_from_sd("dummy.raw")   # This file does not exist
        
    def playMenuMusic(self):
        global isThisRealHardware
        
        if (isThisRealHardware == True):
            g_sound.play_from_sd(menuSong)
        
    def playGameMusic(self):
        global isThisRealHardware
        
        if (isThisRealHardware == True):
            g_sound.play_from_sd(gameSong)
    
# The face graphics
class Faces:
    def __init__(self):
        self.face = []      # Faces array
        self.files = []     # Face piece graphics array
        self.topFace = [43, 55, 3, 15] # x1, x2, y1, y2 positions
        self.rightFace = [73, 85, 32, 44]
        self.btmFace = [43, 55, 61, 73]
        self.leftFace = [13, 25, 32, 44]
        self.rnd = 0
        self.faceRnd = 0
        self.oldRnd = 0
        self.oldFaceRnd = 0
        self.x1 = 43
        self.x2 = 55
        self.y1 = 32
        self.y2 = 44
        self.value = 0  # To match face id's
        
    # Pull image data into lists (arrays)
    def setupImages(self):
        global pygame
        
        self.files.append([gfx.face1_0Pixels, gfx.face1_1Pixels, gfx.face1_2Pixels, gfx.face1_3Pixels])
        self.files.append([gfx.face2_0Pixels, gfx.face2_1Pixels, gfx.face2_2Pixels, gfx.face2_3Pixels])
        self.files.append([gfx.face3_0Pixels, gfx.face3_1Pixels, gfx.face3_2Pixels, gfx.face3_3Pixels])
        self.files.append([gfx.face4_0Pixels, gfx.face4_1Pixels, gfx.face4_2Pixels, gfx.face4_3Pixels])
        self.files.append([gfx.face5_0Pixels, gfx.face5_1Pixels, gfx.face5_2Pixels, gfx.face5_3Pixels])
        
        for x in range (5):
            self.face.append([])
            
            for y in range (4):
                self.face[x].append(pygame.surface.Surface(12, 12, self.files[x][y]))
        
    # Render all faces on screen
    def drawAll(self):
        global topFaceVal, rightFaceVal, btmFaceVal, leftFaceVal
        
        if (gameOver == False):
             
            # Top
            self.index = 1
            self.pieceRange = 5
            
            for piece in range(self.pieceRange):
                if (topFaceVal[self.index - 1] == piece + 1):
                    screen.blit(self.face[piece + 1][0], self.topFace[0], self.topFace[2])
                
            self.index += 1
            
            for piece in range(self.pieceRange):
                if (topFaceVal[self.index - 1] == piece + 1):
                    screen.blit(self.face[piece + 1][1], self.topFace[1], self.topFace[2])
                
            self.index += 1
            
            for piece in range(self.pieceRange):
                if (topFaceVal[self.index - 1] == piece + 1):
                    screen.blit(self.face[piece + 1][2], self.topFace[0], self.topFace[3])
                
            self.index += 1
            
            for piece in range(self.pieceRange):
                if (topFaceVal[self.index - 1] == piece + 1):
                    screen.blit(self.face[piece + 1][3], self.topFace[1], self.topFace[3])
                    
            # Right
            self.index = 1
            
            for piece in range(self.pieceRange):
                if (rightFaceVal[self.index - 1] == piece + 1):
                    screen.blit(self.face[piece + 1][0], self.rightFace[0], self.rightFace[2])
                
            self.index += 1
            
            for piece in range(self.pieceRange):
                if (rightFaceVal[self.index - 1] == piece + 1):
                    screen.blit(self.face[piece + 1][1], self.rightFace[1], self.rightFace[2])
                
            self.index += 1
            
            for piece in range(self.pieceRange):
                if (rightFaceVal[self.index - 1] == piece + 1):
                    screen.blit(self.face[piece + 1][2], self.rightFace[0], self.rightFace[3])
                
            self.index += 1
            
            for piece in range(self.pieceRange):
                if (rightFaceVal[self.index - 1] == piece + 1):
                    screen.blit(self.face[piece + 1][3], self.rightFace[1], self.rightFace[3])
                    
            # Bottom
            self.index = 1
            
            for piece in range(self.pieceRange):
                if (btmFaceVal[self.index - 1] == piece + 1):
                    screen.blit(self.face[piece + 1][0], self.btmFace[0], self.btmFace[2])
                
            self.index += 1
            
            for piece in range(self.pieceRange):
                if (btmFaceVal[self.index - 1] == piece + 1):
                    screen.blit(self.face[piece + 1][1], self.btmFace[1], self.btmFace[2])
                
            self.index += 1
            
            for piece in range(self.pieceRange):
                if (btmFaceVal[self.index - 1] == piece + 1):
                    screen.blit(self.face[piece + 1][2], self.btmFace[0], self.btmFace[3])
                
            self.index += 1
            
            for piece in range(self.pieceRange):
                if (btmFaceVal[self.index - 1] == piece + 1):
                    screen.blit(self.face[piece + 1][3], self.btmFace[1], self.btmFace[3])
                    
            # Left
            self.index = 1
            
            for piece in range(self.pieceRange):
                if (leftFaceVal[self.index - 1] == piece + 1):
                    screen.blit(self.face[piece + 1][0], self.leftFace[0], self.leftFace[2])
                
            self.index += 1
            
            for piece in range(self.pieceRange):
                if (leftFaceVal[self.index - 1] == piece + 1):
                    screen.blit(self.face[piece + 1][1], self.leftFace[1], self.leftFace[2])
                
            self.index += 1
            
            for piece in range(self.pieceRange):
                if (leftFaceVal[self.index - 1] == piece + 1):
                    screen.blit(self.face[piece + 1][2], self.leftFace[0], self.leftFace[3])
                
            self.index += 1
            
            for piece in range(self.pieceRange):
                if (leftFaceVal[self.index - 1] == piece + 1):
                    screen.blit(self.face[piece + 1][3], self.leftFace[1], self.leftFace[3])
 
    
    # Randomize
    def randomizeFace(self):
        global centerFaceVal, topFaceVal, rightFaceVal, btmFaceVal, leftFaceVal
        
        # Generate face piece
        self.rnd = random.getrandbits(2)
        
        # Generate face
        self.faceRnd = random.getrandbits(3)
        
        if (self.faceRnd >= 5):
            #self.randomizeFace()
            self.faceRnd = 4
        if (self.faceRnd == 0):
            self.faceRnd = 1
            
        # Ensure old random and new random isn't the same
        if (self.oldRnd == self.rnd):
            if (self.rnd > 0):
                self.rnd -=1
            else:
                self.rnd += 1
        
        # Store face and piece to compare later
        centerFaceVal = [self.faceRnd, self.rnd]
        self.oldRnd = self.rnd
        self.oldFaceRnd = self.faceRnd

    # Draw random face piece in middle
    def drawRandomFacePiece(self):
        global totalTimer, timer
        
        # Only draw a new face at start of time
        if (timer == totalTimer):
            self.randomizeFace()
            
        # Draw the face piece based on the random value
        for x in range (1, 6):
            if (self.faceRnd == x):
                
                if (self.rnd == 0):
                    screen.blit(self.face[self.faceRnd][0], self.x1, self.y1)   # top left
                elif (self.rnd == 1):
                    screen.blit(self.face[self.faceRnd][1], self.x2, self.y1)   # top right
                elif (self.rnd == 2):
                    screen.blit(self.face[self.faceRnd][2], self.x1, self.y2)   # btm left
                elif (self.rnd == 3):
                    screen.blit(self.face[self.faceRnd][3], self.x2, self.y2)   # btm right
        
    # Update the face of the button pressed
    def updateFaces(self):
        global totalTimer, timer, lives, gameOver, coins, coinSoundPlayed, oldScore
        global centerFaceVal, topFaceVal, btmFaceVal, leftFaceVal, rightFaceVal
        global error, score, btnPos, keyPressed, faceWin, fullFaceWin, cross, faceWinArray
        
        # Compare values for validation
        if (btnPos > 0):
            error = False
                
            if (btnPos == 1 and keyPressed == True):   # Up
                if (topFaceVal[centerFaceVal[1]] > 0):
                    error = True
                else:
                    topFaceVal[centerFaceVal[1]] = centerFaceVal[0] # Set faceID
                    faceWinArray = self.updateMatches(topFaceVal, btnPos)
                    
            if (btnPos == 2 and keyPressed == True):   # Right
                if (rightFaceVal[centerFaceVal[1]] > 0):
                    error = True
                else:
                    rightFaceVal[centerFaceVal[1]] = centerFaceVal[0] # Set faceID
                    faceWinArray = self.updateMatches(rightFaceVal, btnPos)
                    
            if (btnPos == 3 and keyPressed == True):   # Bottom
                if (btmFaceVal[centerFaceVal[1]] > 0):
                    error = True
                else:
                    btmFaceVal[centerFaceVal[1]] = centerFaceVal[0] # Set faceID
                    faceWinArray = self.updateMatches(btmFaceVal, btnPos)
                    
            if (btnPos == 4 and keyPressed == True):   # Left
                if (leftFaceVal[centerFaceVal[1]] > 0):
                    error = True
                else:
                    leftFaceVal[centerFaceVal[1]] = centerFaceVal[0] # Set faceID
                    faceWinArray = self.updateMatches(leftFaceVal, btnPos)
                    
            # Add coin for every 1000 points
            if ((score < 5000) and ((score // 1000) > (oldScore * 1000))):
                coins += 3
                oldScore += 1
                
                if (coinSoundPlayed == False):
                    interface.playCoin()
                    coinSoundPlayed = True
            
            if (error == True):
                interface.playCross()
                self.removeLife()
                error = False
                cross = True    # Show cross
            else:
                timer = totalTimer
                self.randomizeFace()
            
            self.value = 0
            btnPos = 0
            
            # Don't exceed 20 coins
            if (coins > 20):
                coins = 20
                
            
    # Reset face array and update score and play sound
    def updateMatches(self, faceArray, btnPos):
        global score, coins, fullFaceWin, faceWin, leftFaceVal, btmFaceVal, rightFaceVal, topFaceVal, flashCenter
        
        # Check if full face
        self.checkMatch = self.checkFacePiecesMatch(btnPos)
        
        if (self.checkMatch == 1):
            score += 100
            coins += 1
            fullFaceWin = True
            interface.playFullFace()
            flashCenter = True
            
        elif (self.checkMatch == 2):
            score += 50
            faceWin = True
            interface.playFace()
            flashCenter = True
            
        else:
            score += 10
            
        return faceArray
        
    # Reset faces after success
    def resetWinFace(self):
        global faceWinArray, topFaceVal, btmFaceVal, leftFaceVal, rightFaceVal
        
        if (faceWinArray == topFaceVal): 
            topFaceVal = [0, 0, 0, 0]
        if (faceWinArray == rightFaceVal):
            rightFaceVal = [0, 0, 0, 0]
        if (faceWinArray == btmFaceVal):
            btmFaceVal = [0, 0, 0, 0]
        if (faceWinArray == leftFaceVal):
            leftFaceVal = [0, 0, 0, 0]
        
    
    # Check face pieces match   
    def checkFacePiecesMatch(self, pos):
        global topFaceVal, btmFaceVal, leftFaceVal, rightFaceVal
        
        self.faceVal = [topFaceVal, rightFaceVal, btmFaceVal, leftFaceVal]
        self.chkFacePart = False
        
        for x in range (0, 4): # Btn position
            if (pos == x + 1):
                self.value = self.faceVal[x]    # Match the face value to the right array
                if (self.value[0] != 0 and self.value[1] != 0 and self.value[2] != 0 and self.value[3] != 0):
                    if (self.value[1] == self.value[0] and self.value[2] == self.value[0] and self.value[3] == self.value[0]):
                        return 1    # full face
                        
                    return 2    # facea
                else:
                    return 3

    # remove a life
    def removeLife(self):
        global lives, gameOver
        
        lives -= 1
        if (lives <= 0):
            gameOver = True
            
    # Clear board when player uses coin
    def clearBoard(self):
        global coins, topFaceVal, btmFaceVal, leftFaceVal, rightFaceVal, timer, totalTimer
        
        self.clearChoice = random.getrandbits(2)
        if (coins > 0):
            coins -= 1
            if (self.clearChoice == 0):
                topFaceVal = [0, 0, 0, 0]
            elif (self.clearChoice == 1):
                btmFaceVal = [0, 0, 0, 0]
            elif (self.clearChoice == 2):
                leftFaceVal = [0, 0, 0, 0]
            else:
                rightFaceVal = [0, 0, 0, 0]
            
            interface.playClear()
            self.randomizeFace()
            timer = totalTimer

    # Game over
    def drawGameOver(self):
        screen.blit(gfx.gameover, self.x1, self.y1 + 5)
    
    # Run face success
    def drawFullFaceSuccess(self):
        screen.blit(gfx.fullface, self.x1 + 1, self.y1 + 5)
        
    def drawFaceSuccess(self):
        screen.blit(gfx.face, self.x1 + 1, self.y1 + 8)
    
    # Run face crash
    def drawFaceFailure(self):
        screen.blit(gfx.cross, self.x1, self.y1)
        
    # Check if any graphics is showing in the center to prevent player from placing a face piece while "pausing", so to speak
    def checkCenterGraphic(self):
        global faceWin, fullFaceWin, cross
        
        if (faceWin == True or fullFaceWin == True or cross == True):
            return True
        
        return False

# Init
logo = Logo()
interface = Interface()
faces = Faces()
faces.setupImages()

# Start menu song
interface.playMenuMusic()

# The main loop
while True:
    
    interface.updateDelta(targetFPS)

    # Read keys
    eventtype = pygame.event.poll()
    if eventtype != pygame.NOEVENT:
        # Keydown events
        if eventtype.type == pygame.KEYDOWN:
            if (gameState == 0):
                if (eventtype.key == pygame.K_RIGHT):
                    musicEnabled = False
                    if (musicIsPlaying == True):
                        interface.stopMusic()
                        musicIsPlaying = False
                    
                if (eventtype.key == pygame.K_LEFT):
                    musicEnabled = True
                    if (musicIsPlaying == False):
                        interface.playMenuMusic()
                        musicIsPlaying = True
                    
            if (gameOver == False):
                if (eventtype.key == pygame.K_UP):
                    if (faces.checkCenterGraphic() == False):
                        if (keyPressed == False):
                            btnPos = 1
                            keyPressed = True
                            if (gameState == 1):
                                interface.playMove()    # Play a sound
                        
                if (eventtype.key == pygame.K_RIGHT):
                    if (faces.checkCenterGraphic() == False):
                        if (keyPressed == False):
                            btnPos = 2
                            keyPressed = True
                            if (gameState == 1):
                                interface.playMove()    # Play a sound
                            
                if (eventtype.key == pygame.K_DOWN):
                    if (faces.checkCenterGraphic() == False):
                        if (keyPressed == False):
                            btnPos = 3
                            keyPressed = True
                            if (gameState == 1):
                                interface.playMove()    # Play a sound
                            
                if (eventtype.key == pygame.K_LEFT):
                    if (faces.checkCenterGraphic() == False):
                        if (keyPressed == False):
                            btnPos = 4
                            keyPressed = True
                            if (gameState == 1):
                                interface.playMove()    # Play a sound
                            
            if (eventtype.key == pygame.BUT_B):
                if (gameState == 0):
                    showInstructions = True
                else:
                    if (coins > 0 and boardCleared == False and gameOver == False):
                        faces.clearBoard()
                        boardCleared = True
            
            if (eventtype.key == pygame.BUT_A):
                # Push to start in menu
                if (gameState == 0):
                    gameState = 1
                    interface.reset()
                    if (musicEnabled == True):
                        interface.playGameMusic()
                elif(gameState == 1 and lives == 0):
                    gameState = 0
                    if (musicEnabled == True):
                        interface.playMenuMusic()
            
            
        # Keyup events
        if eventtype.type == pygame.KEYUP:
            if (eventtype.key == pygame.K_UP):
                btnPos = 0
            if (eventtype.key == pygame.K_RIGHT):
                btnPos = 0
            if (eventtype.key == pygame.K_DOWN):
                btnPos = 0
            if (eventtype.key == pygame.K_LEFT):
                btnPos = 0
            if (eventtype.key == pygame.BUT_B):
                if (gameState == 0):
                    showInstructions = False
                else:
                    boardCleared = False
        
    # Update
    if (gameState == 1):
        # Reset timer
        if (timer > 0):
            if (fullFaceWin == True or faceWin == True or cross == True):
                timer = totalTimer
            else:
                if (gameOver == False):
                    timer -= 1
            
        # Time is up, player loses a life
        else:
            timer = totalTimer
            faces.randomizeFace()
            faces.removeLife()
            interface.playCross()
            cross = True    # Show cross
            
        # Check face logic only when button pressed
        if (btnPos == 0):
            keyPressed = False
        else:
            faces.updateFaces()
            
        if (gameOver == True and gameOverPlayed == False):
            interface.playGameOver()
            gameOverPlayed = True
    else:
        # Start randomizing on menu
        faces.randomizeFace()

    # Render
    screen.fill(0)  # Clear screen
    
    # Menu
    if (gameState == 0):
        if (showInstructions == True):
            interface.showInstructions()
        else:
            logo.drawLogo()
            umachine.draw_text(40, 20, "A: START", 4)
            umachine.draw_text(40, 27, "B: INFO (hold)", 4)
            umachine.draw_text(2, 34, "MUSIC: Left(on) Right(off)", 4)
            umachine.draw_text(15, 42, "by Blackjet in 2019", 8)
            umachine.draw_text(87, 82, "v0." + str(version), 14)
            
    # Game
    else:
        interface.drawInterface()
        interface.drawStats()
        if (gameOver == True):
            # Add left-over coins to score
            if (coins > 0):
                if (pauseTimer > 0):
                    pauseTimer -= 1
                else:
                    pauseTimer = gameOverPauseTimerLength
                    interface.playCoin()
                    coins -= 1
                    score += 100
                
            faces.drawGameOver()
            faces.randomizeFace()
            
        else:
            
            if (fullFaceWin == True):
                if (pauseTimer > 0):
                    if (flashCenter == True):
                        if (flashCenterCounter % 3 == 0):
                            faces.drawFullFaceSuccess()
                            
                        flashCenterCounter -= 1
                        
                    pauseTimer -=1
                    if (pauseTimer <= 0):
                        pauseTimer = pauseTimerLength
                        fullFaceWin = False
                        faces.resetWinFace()
                        flashCenterCounter = flashCenterCounterVal
                        flashCenter = False
            
            if (faceWin == True):
                if (pauseTimer > 0):
                    if (flashCenter == True):
                        if (flashCenterCounter % 3 == 0):
                            faces.drawFaceSuccess()
                            
                        flashCenterCounter -= 1
                        
                    pauseTimer -=1
                    if (pauseTimer <= 0):
                        pauseTimer = pauseTimerLength
                        faceWin = False
                        faces.resetWinFace()
                        flashCenterCounter = flashCenterCounterVal
                        flashCenter = False
                        
            if (cross == True):
                if (pauseTimer > 0):
                    faces.drawFaceFailure()
                    pauseTimer -=1
                    if (pauseTimer <= 0):
                        pauseTimer = pauseTimerLength
                        cross = False
                        
            # Generate a new face piece
            if (pauseTimer == pauseTimerLength):
                faces.drawRandomFacePiece()
            
        # Draw all placed face pieces
        faces.drawAll()
    
    # Sync screen
    pygame.display.flip()
    
    