import random #for generating random numbers
import sys #we will use this to exit the program
import pygame
from pygame.locals import *  # basic pygame imports

#Global variables for the game
FPS = 32
SCREENWIDTH = 289
SCREENHEIGHT = 511
# SCREEN = pygame.display.set_mode((SCREENWIDTH, SCREENHEIGHT))
GROUNDY = SCREENHEIGHT * 409
GAME_SPRITES = {}
GAME_SOUNDS = {}
PLAYER = 'gallery/sprites/bird.png'
BACKGROUND = 'gallery/sprites/bg.jpg'
PIPE = 'gallery/sprites/down-pipe.png'

def welcomeScreen():
    """
    Shows welcome images on the screen
    """

    playerx = int(SCREENWIDTH / 5)
    playery = int((SCREENHEIGHT - GAME_SPRITES['player'].get_height()) / 2)
    basex = 0
    messagex = int((SCREENWIDTH - GAME_SPRITES['message'].get_width()) / 2)
    messagey = int(SCREENHEIGHT * 0.0)
    
    while True:
        for event in pygame.event.get():
            # if user clicks on cross button, close the game
            if event.type == QUIT or (event.type == KEYDOWN and event.key == K_ESCAPE):
                pygame.quit()
                sys.exit()
            # if user presses space or up key, start the game for them
            elif event.type == KEYDOWN and (event.key == K_SPACE or event.key == K_UP):
                return
            else:
                SCREEN.blit(GAME_SPRITES['background'], (0, 0))
                SCREEN.blit(GAME_SPRITES['base'], (basex, GROUNDY))
                SCREEN.blit(GAME_SPRITES['player'], (playerx, playery))
                SCREEN.blit(GAME_SPRITES['message'], (messagex, messagey))
                pygame.display.update()
                FPSCLOCK.tick(FPS)

                
def mainGame():
    score = 0
    playerx = int(SCREENWIDTH / 5)
    playery = int(SCREENHEIGHT / 2)
    basex = 0 

    #create two pipes for blitting on the screen
    newPipe1 = getRandomPipe()
    newPipe2 = getRandomPipe()

    #my list of upper pipes
    upperPipes = [
        {'x': SCREENWIDTH + 200, 'y': newPipe1[0]['y']},
        {'x': SCREENWIDTH + 200 +(SCREENWIDTH / 2), 'y': newPipe2[0]['y']},
    ]
    #my list of lower pipes 
    lowerPipes = [
        {'x': SCREENWIDTH + 200, 'y': newPipe1[1]['y']},
        {'x': SCREENWIDTH + 200 +(SCREENWIDTH / 2), 'y': newPipe2[1]['y']},
    ]

    pipeVelX = -4  # velocity of pipes.

    playerVelY = -9  # velocity of bird
    playerMaxVelY = 10  # max velocity of bird
    playerMinVelY = -8  # min velocity of bird
    playerAccY = 1  # acceleration of bird

    playerFlapAccY = -8  # velocity while flapping
    playerFlapped = False  # boolean for bird flapping true only when the bird is flapping


    while True:
        for event in pygame.event.get():
            if event.type == QUIT or (event.type == KEYDOWN and event.key == K_ESCAPE):
                pygame.quit()  # uninitialize all pygame modules
                sys.exit()  # exit the program
            if event.type == KEYDOWN and (event.key == K_SPACE or event.key == K_UP):
                if playery > 0:
                    playerVelY = playerFlapAccY  # velocity while flapping
                    playerFlapped = True
                    GAME_SOUNDS['wing'].play()  # play the wing sound when the bird flaps

 
        crashTest = isCollide(playerx, playery, upperPipes, lowerPipes)  # if the player is crashed
        if crashTest:
            return

        # check for score            
        playerMidPos = playerx + GAME_SPRITES['player'].get_width() / 2
        for pipe in upperPipes:
            pipeMidPos = pipe['x'] + GAME_SPRITES['pipe'][0].get_width() / 2
            if pipeMidPos <= playerMidPos < pipeMidPos + 4:
                score += 1
                print(f"Your score is {score}")
                GAME_SOUNDS['point'].play() 


        if playerVelY < playerMaxVelY and not playerFlapped:
            playerVelY += playerAccY  # increase the velocity of bird if the bird is not flapped

        if playerFlapped:
            playerFlapped = False  # reset the flapped variable
        playerHeight = GAME_SPRITES['player'].get_height()
        playery = playery + min(playerVelY, GROUNDY - playery - playerHeight)  # update the position of bird
        
        # move pipes to the left
        for upperPipe, lowerPipe in zip(upperPipes, lowerPipes):
            upperPipe['x'] += pipeVelX
            lowerPipe['x'] += pipeVelX

        # add new pipe when the first pipe is about to cross the leftmost part of the screen
        if 0 < upperPipes[0]['x'] < 5:
            newPipe = getRandomPipe()  # get new pipe
            upperPipes.append(newPipe[0])  # add new pipe to the list of upper pipes
            lowerPipes.append(newPipe[1])  # add new pipe to the list of lower pipes

        # if the pipe is out of the screen, remove it
        if upperPipes[0]['x'] < -GAME_SPRITES['pipe'][0].get_width():
            upperPipes.pop(0)  # remove the first pipe from the list of upper pipes
            lowerPipes.pop(0)  # remove the first pipe from the list of lower pipes

        # Lets blit our game images now
        SCREEN.blit(GAME_SPRITES['background'], (0, 0))  # draw the background
        for upperPipe, lowerPipe in zip(upperPipes, lowerPipes):
            SCREEN.blit(GAME_SPRITES['pipe'][0], (upperPipe['x'], upperPipe['y']))  # draw the upper pipe
            SCREEN.blit(GAME_SPRITES['pipe'][1], (lowerPipe['x'], lowerPipe['y']))  # draw the lower pipe

        SCREEN.blit(GAME_SPRITES['base'], (basex, GROUNDY))
        SCREEN.blit(GAME_SPRITES['player'], (playerx, playery))
        myDigits = [int(x) for x in str(score)]  # convert the score to a list of digits
        width = 0
        for digit in myDigits:
            width += GAME_SPRITES['numbers'][digit].get_width()  # get the width of each digit
        Xoffset = (SCREENWIDTH - width) / 2

        for digit in myDigits:
            SCREEN.blit(GAME_SPRITES['numbers'][digit], (Xoffset, SCREENHEIGHT * 0.12))   # draw the score
            Xoffset += GAME_SPRITES['numbers'][digit].get_width()
        pygame.display.update()  # update the display
        FPSCLOCK.tick(FPS)  # control the frame rate

def isCollide(playerx, playery, upperPipes, lowerPipes):
    if playery > GROUNDY - 25 or playery < 0:
        GAME_SOUNDS['hit'].play()
        return True

    playerHeight = GAME_SPRITES['player'].get_height()
    playerWidth = GAME_SPRITES['player'].get_width()

    # Reduce hitbox size for smoother gameplay
    birdHitboxOffset = 5  # You can increase this to reduce collisions even more

    for pipe in upperPipes:
        pipeX = pipe['x']
        pipeY = pipe['y']
        pipeW = GAME_SPRITES['pipe'][0].get_width()
        pipeH = GAME_SPRITES['pipe'][0].get_height()

        if (playerx + playerWidth - birdHitboxOffset > pipeX and
            playerx + birdHitboxOffset < pipeX + pipeW and
            playery + birdHitboxOffset < pipeY + pipeH):
            GAME_SOUNDS['hit'].play()
            return True

    for pipe in lowerPipes:
        pipeX = pipe['x']
        pipeY = pipe['y']
        pipeW = GAME_SPRITES['pipe'][0].get_width()

        if (playerx + playerWidth - birdHitboxOffset > pipeX and
            playerx + birdHitboxOffset < pipeX + pipeW and
            playery + playerHeight - birdHitboxOffset > pipeY):
            GAME_SOUNDS['hit'].play()
            return True

    return False



def getRandomPipe():
       """
       Generate positions of two pipes (one bottom straight and one rotated) for blitting on the screen
       """
       pipeHEIGHT = GAME_SPRITES['pipe'][0].get_height()
       offset = SCREENHEIGHT / 3
       y2 = offset + random.randrange(0, int(SCREENHEIGHT - GAME_SPRITES['base'].get_height() - 1.2 * offset))
       pipeX = SCREENWIDTH + 10
       y1 = pipeHEIGHT - y2 + offset
       pipe = [
           {'x': pipeX, 'y': -y1},  # top pipe
           {'x': pipeX, 'y': y2}    # bottom pipe
       ]      
       return pipe  # return the generated pipes
if __name__ == "__main__":
    # this will be the main point from where our game will start
    pygame.init()  # initialize all imported pygame modules
    SCREEN = pygame.display.set_mode((SCREENWIDTH, SCREENHEIGHT))

    FPSCLOCK = pygame.time.Clock()  # create a clock object to control the frame rate
    pygame.display.set_caption('Flappy Bird by SSUET CLoudComputing Students')
    GAME_SPRITES['numbers'] = (
        pygame.image.load('gallery/sprites/0.png').convert_alpha(),
        pygame.image.load('gallery/sprites/1.png').convert_alpha(),
        pygame.image.load('gallery/sprites/2.png').convert_alpha(),
        pygame.image.load('gallery/sprites/3.png').convert_alpha(),
        pygame.image.load('gallery/sprites/4.png').convert_alpha(),
        pygame.image.load('gallery/sprites/5.png').convert_alpha(),
        pygame.image.load('gallery/sprites/6.png').convert_alpha(),
        pygame.image.load('gallery/sprites/7.png').convert_alpha(),
        pygame.image.load('gallery/sprites/8.png').convert_alpha(),
        pygame.image.load('gallery/sprites/9.png').convert_alpha()
    )

    GAME_SPRITES['message'] = pygame.image.load('gallery/sprites/message.png').convert_alpha()
    GAME_SPRITES['base'] = pygame.image.load('gallery/sprites/down-base.png').convert_alpha()
     # Load and resize bird image
    bird_img = pygame.image.load(PLAYER).convert_alpha()
    bird_img = pygame.transform.scale(bird_img, (50, 40))  # Resize bird
    GAME_SPRITES['player'] = bird_img

    pipe_image = pygame.image.load(PIPE).convert_alpha()
    GAME_SPRITES['pipe'] = (
        pygame.transform.rotate(pipe_image, 180),
        pipe_image
    )

    # Load and resize background
    BACKGROUND_IMAGE = pygame.image.load(BACKGROUND).convert()
    BACKGROUND_IMAGE = pygame.transform.scale(BACKGROUND_IMAGE, (SCREENWIDTH, SCREENHEIGHT))
    GAME_SPRITES['background'] = BACKGROUND_IMAGE
    number_images = []
    for i in range(10):
        image = pygame.image.load(f'gallery/sprites/{i}.png').convert_alpha()
        image = pygame.transform.scale(image, (
            int(image.get_width() * 0.5),
            int(image.get_height() * 0.5)
        ))
        number_images.append(image)
    GAME_SPRITES['numbers'] = tuple(number_images)


    # Load sounds
    GAME_SOUNDS['die'] = pygame.mixer.Sound('gallery/sound/die.mp3')
    GAME_SOUNDS['hit'] = pygame.mixer.Sound('gallery/sound/hit.mp3')
    GAME_SOUNDS['point'] = pygame.mixer.Sound('gallery/sound/point.mp3')
    GAME_SOUNDS['swoosh'] = pygame.mixer.Sound('gallery/sound/swoosh.mp3')
    GAME_SOUNDS['wing'] = pygame.mixer.Sound('gallery/sound/wing.mp3')

    # Correct bird position calculation
    GROUNDY = SCREENHEIGHT - GAME_SPRITES['base'].get_height()
    BIRD_X = int(SCREENWIDTH / 5)
    BIRD_Y = int((SCREENHEIGHT - GAME_SPRITES['player'].get_height()) / 2)

    # Start the game loop
    while True:
        welcomeScreen()
        mainGame()