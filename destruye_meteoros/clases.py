import pygame as pg
from destruye_meteoros import DIMENSIONES, FPS
from pygame.locals import *
import sys
import enum
import random
import sqlite3

pg.init()
'''
pg.mixer.init()
musica = pg.mixer.music.load('static/maluma.mp3')
pg.mixer.musica.play(-1)
musica.Sound.set_volume(1.0)
'''
yoshi = pg.image.load('static/yoshi.png')
yoshi_fondo = pg.image.load('static/yoshi_fondo.png')
m = pg.image.load('static/m.png')
g_o = pg.image.load('static/g_o.png')
icono = 'static/S_invaders.jpg'
meteoritos = ()
white = (255, 255, 255)
corazon = pg.image.load('static/corazon.png')
WIDTH = 800
HEIGHT = 600
class Planeta(pg.sprite.Sprite):
    def __init__(self, x, y, vx):
        pg.sprite.Sprite.__init__(self)
        self.vx = vx
        self.image = pg.image.load('static/planet.png')
        self.rect = self.image.get_rect(x=x, y=y)

    def actualizar_posicion(self):
        self.rect.x -= self.vx

    def update(self, dt):
        if self.rect.x < 500:
            self.vx = 0
        self.actualizar_posicion()
class Planeta2(pg.sprite.Sprite):
    def __init__(self, x, y, vx):
        pg.sprite.Sprite.__init__(self)
        self.vx = vx
        self.image = pg.image.load('static/PLANETA_2.png')
        self.rect = self.image.get_rect(x=x, y=y)

    def actualizar_posicion(self):
        self.rect.x -= self.vx

    def update(self, dt):
        if self.rect.x < 500:
            self.vx = 0
        self.actualizar_posicion()
class Meteoritos(pg.sprite.Sprite):
    def __init__(self, x, y, vx):
        pg.sprite.Sprite.__init__(self)
        self.vx = 6
        self.puntuacion = 0
        self.meteoritos_pasados = 0
        self.puntuacion = 0
        self.image = pg.image.load('static/meteorito.png')
        self.rect = self.image.get_rect(x=x, y=y)
        self.num_meteoritos = 0
    def actualizar_posicion(self):
        self.rect.x -= self.vx
    def reset_pos(self):
        self.rect.y = random.randrange(1, 600)
        self.rect.x = 800

    def update(self, dt):
        self.actualizar_posicion()
        if self.rect.x <= -75:
            self.vx += 2
            self.reset_pos()
            self.puntuacion += 25
            self.meteoritos_pasados += 1
            self.num_meteoritos += 1


    def comprobar_colision(self, algo):
        if self.rect.colliderect(algo.rect):
            self.reset_pos()
            self.vx -= 2
            self.num_meteoritos = 0
            self.update()

class NaveStatus(enum.Enum):
    viva = 0
    explotando = 1
    muerta = 2

class Nave(pg.sprite.Sprite):
    w = 152
    h = 151
    escala = 1
    num_explosion = 8
    retardo_animaciones = 5
    def __init__(self, x, y, vy, vx):
        pg.sprite.Sprite.__init__(self)
        self.sw_pulsado = False
        self.ticks_acumulados = 0
        self.animation_time = FPS//1000 * 3
        self.angle = 0
        self.ticks_por_frame_de_animacion = 1000//FPS * self.retardo_animaciones
        self.vidas = 3
        self.vy = vy
        self.vx = vx
        self.image = pg.image.load('static/nave.png')
        self.imagenes_explosion = self.cargaExplosion()
        self.ix_explosion = 0
        self.rect = self.image.get_rect(x=y, y=y)
        self.giraCentro = (x, y)
        self.current_time = 0
        self.frame = pg.image.load('static/nave.png')
        self.image.blit(self.frame, (0,0), (0, 0, self.w, self.h))
        self.frames = []
        self.index = 0
        self.how_many = 0
        self.animation_time = FPS//2

        self.loadFrames()
        self.current_time = 0
        self.rotando = False
        self.status = NaveStatus.viva

    def loadFrames(self):
        self.sprite_sheet = pg.image.load('static/nave.png').convert_alpha()
        for fila in range(5):
            y = fila * self.h
            for columna in range(6):
                x = columna * self.w

                image = pg.Surface((self.w, self.h))
                image.blit(self.sprite_sheet, (0,0), (x, y, self.w, self.h))

                self.frames.append(image)

        self.how_many = len(self.frames)
        self.image = self.frames[self.index]

    def reiniciar(self):
        self.ticks_acumulados = 0
        self.ix_explosion = 0
        self.status = NaveStatus.viva
        self.rect.x = 1
        self.rect.y = 200
        self.image = self.sprite_sheet

    def cargaExplosion(self):
        return [pg.image.load(f"static/explosion0{i}.png") for i in range(self.num_explosion)]

    def explosion(self, dt):
        if self.ix_explosion >= len(self.imagenes_explosion):
            self.status = NaveStatus.muerta
            return
        self.ticks_acumulados += dt
        self.image = self.imagenes_explosion[self.ix_explosion]
        print('numero explosion:', self.ix_explosion)
        if self.ticks_acumulados >= self.ticks_por_frame_de_animacion:
            self.ix_explosion += 1
            self.ticks_acumulados = 0
        return False

    def comprobar_colision(self, algo):
        if self.rect.colliderect(algo.rect):
            print('explosion detectada')
            self.status = NaveStatus.explotando
            return True

    def update(self, dt):
        if self.status == NaveStatus.explotando:
            return self.explosion(dt)

        self.rect.y += self.vy
        if self.rect.y + 75 >= DIMENSIONES[1]:
            self.rect.y = DIMENSIONES[1] - 75
        if self.rect.y <= 0:
            self.rect.y = 0
        
        if self.rotando:
            self.image = pg.transform.rotate(self.image, 1)
        else:
            if self.current_time > self.animation_time:
                self.current_time = 0
                self.index += 1

                if self.index >= self.how_many:
                    self.index = 0

                self.image = self.frames[self.index]

                self.rect.x += self.velocidad
                if self.rect.x > 800:
                    self.rect.x = -240
                    self.velocidad += 5
        if self.rotando:
            self.angle = (self.angle + 1)%360
            self.image = pg.transform.rotate(self.frame, self.angle)
            rect = self.image.get_rect()
            newSemiW = rect.centerx
            newSemiH = rect.centery

            dX = newSemiW - self.w//2
            dY = newSemiH - self.h//2

            self.rect.centerx = self.giraCentro[0] - dX
            self.rect.centery = self.giraCentro[1] - dY

            if self.angle % 180 == 0:
                self.rotando = False

        else:
            self.giraCentro = self.rect.center

        if self.rect.centerx > 800 + self.w/2:
            self.rect.centerx = -self.w/2
        

class Game:
    def __init__(self):
        #self.music = pg.mixer.music.load('static/maluma.mp3')
        self.x = 0
        self.puntuacion = 0
        self.nivel = 0
        self.pantalla = pg.display.set_mode(DIMENSIONES)
        self.rectangulo_pantalla = self.pantalla.get_rect()
        pg.display.set_caption("Destruye_meteoritos")
        pg.display.set_icon(m)
        self.nave = Nave(1, 263, 1, 1)
        self.cuenta_vidas = pg.font.Font('static/VT323-Regular.ttf', 30)
        self.intro3 = pg.font.Font('static/VT323-Regular.ttf', 50)
        self.intro4 = pg.font.Font('static/VT323-Regular.ttf', 150)
        self.meteoritos = Meteoritos(800, random.randint(50, 550), 5)
        self.planeta = Planeta(800, 1, 1)
        self.planeta3 = Planeta2(800, 1, 1)
        self.jugador = pg.sprite.Group(self.nave)
        self.planeta2 = pg.sprite.Group(self.planeta)
        self.planeta3 = pg.sprite.Group(self.planeta3)
        self.todos = pg.sprite.Group()
        self.todos.add(self.jugador, self.meteoritos)
        self.clock = pg.time.Clock()
        self.arriba = pg.image.load('static/arriba.png')
        self.abajo = pg.image.load('static/abajo.png')
        self.bg = pg.image.load('static/bg_(2).png')
        self.estado = 1
    def yoshi(self):
        yoshi = True
        while yoshi:
            events = pg.event.get()
            for event in events:
                if event.type == pg.QUIT:
                    pg.quit()
                    sys.exit()
            self.pantalla.fill((0, 0, 0))
            self.pantalla.blit(yoshi_fondo, (0, 0))
            bigtext = pg.font.Font('static/VT323-Regular.ttf', 500)
            textSurf6, textRect6 = self.diez('RAMÓN PONME', bigtext)
            textSurf7, textRect7 = self.diez('UN 10 :)', bigtext)
            textRect6.center = (400, 250)
            textRect7.center = (400, 350)
            self.pantalla.blit(textSurf6, textRect6)
            self.pantalla.blit(textSurf7, textRect7)
            pg.display.flip()
    def control_eventos(self):
        teclas_pulsadas = pg.key.get_pressed()
        if teclas_pulsadas[K_DOWN]:
            self.nave.vy = 10
        elif teclas_pulsadas[K_UP]:
            self.nave.vy = -10
        elif teclas_pulsadas[K_SPACE]:
            self.nave.rotacion()
        else:
            self.nave.vy = 0
        return False
    def movimiento(self):
        rel_x = self.x % self.bg.get_rect().width
        self.pantalla.blit(self.bg, (rel_x - self.bg.get_rect().width, 0))
        if rel_x <= DIMENSIONES[0]:
            self.pantalla.blit(self.bg, (rel_x, 0))
        self.x -= 5
    def text_objects(self, text, font):
        textSurface = self.intro3.render(text, True, (155, 155, 155))
        return textSurface, textSurface.get_rect()
    def level_p(self, text, font):
        textSurface = self.intro4.render(text, True, (10, 255, 10))
        return textSurface, textSurface.get_rect()
    def text_objects1(self, text, font):
        textSurface = self.cuenta_vidas.render(text, True, (100, 100, 100))
        return textSurface, textSurface.get_rect()
    def game_o(self, text, font):

        textSurface = self.intro4.render(text, True, (255, 10, 10))
        return textSurface, textSurface.get_rect()
    def diez(self, text, font):

        textSurface = self.intro4.render(text, True, (10, 10, 255))
        return textSurface, textSurface.get_rect()
    def reiniciar_(self):
        dt = self.clock.tick(60)
        self.nave.vidas = 4
        self.meteoritos.puntuacion = 0
        self.meteoritos.meteoritos_pasados = 0
        self.meteoritos.num_meteoritos = 0
        self.meteoritos.image = pg.image.load('static/meteorito.png')
        self.nivel = 0
        self.nave.rect.x = 1
        self.nave.rect.y = 200
        self.planeta2.update(dt)
    def reiniciar_lp(self):
        dt = self.clock.tick(60)
        self.nave.image = pg.transform.rotate(self.nave.image, 180)
        self.nave.vidas += 1
        self.nivel = 0
        self.nave.rect.x = 1
        self.nave.rect.y = 200
        self.planeta3.update(dt)
        self.nave.reiniciar()
    def nivel2(self):
        game_over = False
        while not game_over:
            dt = self.clock.tick(60)
            events = pg.event.get()
            for event in events:
                if event.type == pg.QUIT:
                    pg.quit()
                    sys.exit()
            self.movimiento()
            if self.nave.comprobar_colision(self.meteoritos):
                self.meteoritos.puntuacion -= 2
            if self.nave.status == NaveStatus.muerta:
                self.nave.vidas -= 1
                self.meteoritos.reset_posicion()
                self.meteoritos.num_meteoritos = 0
                self.meteoritos.vx = 7
                if self.nave.vidas == 0:
                    game_over = True
                    self.estado = 3
                    self.main_loop()
                else:
                    self.nave.reiniciar()
            Spuntuacion = self.cuenta_vidas.render(str(self.meteoritos.puntuacion), True, (155, 155, 155))
            SnumM = self.cuenta_vidas.render(str(self.meteoritos.meteoritos_pasados), True, (155, 155, 155))
            Svidas = self.cuenta_vidas.render(str(self.nave.vidas), True, (155, 155, 155))
            SPalabra_vidas = self.cuenta_vidas.render('vidas', True, (155, 155, 155))
            Rpalabra_vidas = Svidas.get_rect(topleft=(30, 25))
            SPalabra_puntuacion = self.cuenta_vidas.render('Puntuación =', True, (155, 155, 155))
            Rpalabra_puntuacion = Svidas.get_rect(topleft=(125, 25))
            Rpuntuacion = Svidas.get_rect(topleft=(275, 25))
            Rvidas = Svidas.get_rect(topright=(25, 25))
            RnumM = Svidas.get_rect(topright=(600, 25))
            SPalabra_numM = self.cuenta_vidas.render('Meteoritos Pasados =', True, (155, 155, 155))
            Rpalabra_numM = Svidas.get_rect(topleft=(335, 25))
            self.control_eventos()
            self.todos.update(dt)
            self.todos.draw(self.pantalla)
            if self.meteoritos.num_meteoritos > 1 and self.nivel == 0:
                self.meteoritos.puntuacion += 50
                self.meteoritos.image = pg.image.load('static/a_negro.png')
                self.meteoritos.num_meteoritos = 0
                self.meteoritos.vx = 7
                self.nivel = 1
            if self.meteoritos.num_meteoritos > 5 and self.nivel == 1:
                self.meteoritos.puntuacion += 50
                self.meteoritos.image = pg.image.load('static/ovni.png')
                self.meteoritos.num_meteoritos = 0
                self.meteoritos.vx = 7
                self.nivel = 2
                self.nave.vx = 7
            if self.meteoritos.num_meteoritos > 5 and self.nivel == 2:
                self.meteoritos.puntuacion += 50
                self.meteoritos.image = pg.image.load('static/calavera.png')
                self.meteoritos.num_meteoritos = 0
                self.meteoritos.vx = 15
                self.nivel = 2
                self.nave.vx = 7
                self.nivel = 3
            if self.meteoritos.num_meteoritos > 5 and self.nivel == 3:
                self.meteoritos.vx = 0
                self.planeta3.update(dt)
                self.planeta3.draw(self.pantalla)
                self.nave.rect.x += 1
                if self.nave.rect.x > 375:
                    self.nave.rect.x = 375
                    self.nave.rect.y = 229
                    self.estado = 7
                    self.main_loop()
            if self.nave.rotando == True:
                self.meteoritos.puntuacion += 1
            self.pantalla.blit(SPalabra_vidas, (Rpalabra_vidas.x, Rpalabra_vidas.y))
            self.pantalla.blit(SPalabra_puntuacion, (Rpalabra_puntuacion.x, Rpalabra_puntuacion.y))
            self.pantalla.blit(SPalabra_numM, (Rpalabra_numM.x, Rpalabra_numM.y))
            self.pantalla.blit(Svidas, (Rvidas.x, Rvidas.y))
            self.pantalla.blit(SnumM, (RnumM.x, RnumM.y))
            self.pantalla.blit(Spuntuacion, (Rpuntuacion.x, Rpuntuacion.y))
            pg.display.flip()
    def records_gameOver(self):
        record = True
        while record:
            events = pg.event.get()
            for event in events:
                if event.type == pg.QUIT:
                    pg.quit()
                    sys.exit()
            self.pantalla.fill((0, 0, 0))
            Largetext = pg.font.Font('static/VT323-Regular.ttf', 200)
            bigtext = pg.font.Font('static/VT323-Regular.ttf', 500)
            TextSurf, TextRect = self.text_objects('RECORDS', Largetext)
            puntos = self.meteoritos.puntuacion
            vidas = self.nave.vidas
            numM = self.meteoritos.meteoritos_pasados
            TextSurf1, TextRect1 = self.text_objects1((f"Tu puntuacion ha sido de {puntos} puntos"), Largetext)
            TextSurf2, TextRect2 = self.text_objects1((f"Has acabado con {vidas} vidas"), Largetext)
            TextSurf3, TextRect3 = self.text_objects1((f"Has esquivado {numM} meteoritos"), Largetext)
            textSurf4, textRect4 = self.text_objects1('VOLVER A JUGAR', Largetext)
            textSurf5, textRect5 = self.text_objects1('SALIR', Largetext)
            textSurf6, textRect6 = self.game_o('GAME', bigtext)
            textSurf7, textRect7 = self.game_o('OVER', bigtext)
            TextRect.center = (400, 25)
            TextRect1.center = (400, 75)
            TextRect2.center = (400, 100)
            TextRect3.center = (400, 125)
            textRect4.center = (175, 525)
            textRect5.center = (625, 525)
            textRect6.center = (400, 250)
            textRect7.center = (400, 350)
            self.pantalla.blit(TextSurf, TextRect)
            self.pantalla.blit(TextSurf1, TextRect1)
            self.pantalla.blit(TextSurf2, TextRect2)
            self.pantalla.blit(TextSurf3, TextRect3)
            self.pantalla.blit(textSurf6, textRect6)
            self.pantalla.blit(textSurf7, textRect7)
            mouse = pg.mouse.get_pos()
            click = pg.mouse.get_pressed()
            if 50+250 > mouse[0] > 50 and 500+50 > mouse[1] > 500:
                print('if 1')
                pg.draw.rect(self.pantalla, (255, 255, 255), (50, 500, 250, 50))
                if click[0] == 1:
                    self.estado = 2
                    self.reiniciar_()
                    self.main_loop()
            else:
                print('else 1')
                pg.draw.rect(self.pantalla, (155, 155, 155), (50, 500, 250, 50))
            if 500+250 > mouse[0] > 500 and 500+50 > mouse[1] > 500:
                print('if 2')
                pg.draw.rect(self.pantalla, (255, 255, 255), (500, 500, 250, 50))
                if click[0] == 1:
                    self.estado = 8
                    self.main_loop()
            else:
                print('else 2')
                pg.draw.rect(self.pantalla, (155, 155, 155), (500, 500, 250, 50))
            self.pantalla.blit(textSurf4, textRect4)
            self.pantalla.blit(textSurf5, textRect5)
            pg.display.update()
            self.clock.tick(15)
            pg.display.flip()
    def game_intro(self):
        intro = True
        while intro:
            events = pg.event.get()
            for event in events:
                if event.type == pg.QUIT:
                    pg.quit()
                    sys.exit()
            self.pantalla.fill((0, 0, 0))
            Largetext = pg.font.Font('static/VT323-Regular.ttf', 200)
            TextSurf, TextRect = self.text_objects('ESCAPA DE LA TIERRA', Largetext)
            TextRect.center = (400, 25)
            self.pantalla.blit(TextSurf, TextRect)
            mouse = pg.mouse.get_pos()
            click = pg.mouse.get_pressed()
            print(mouse)
            print(click)
            if 100+600 > mouse[0] > 100 and 500+50 > mouse[1] > 500:
                pg.draw.rect(self.pantalla, (255, 255, 255), (100, 500, 600, 50))
                if click[0] == 1:
                    self.estado = 2
                    self.main_loop()
            else:
                pg.draw.rect(self.pantalla, (155, 155, 155), (100, 500, 600, 50))
            if 0+25 > mouse[0] > 0 and 575+25 > mouse[1] > 575:
                if click[0] == 1:
                    self.nave.vidas = 5
            else:
                pass
            stext = pg.font.Font('static/VT323-Regular.ttf', 1)
            textSurf, textRect = self.text_objects1('PULSA PARA EMPEZAR', Largetext)
            textSurf2, textRect2 = self.text_objects1('Una oleada de aliens ha invadido la Tierra y quieren devorarnos', stext)
            textSurf3, textRect3 = self.text_objects1('Asi que los últimos supervivientes y tu les habeis robado la nave', stext)
            textSurf4, textRect4 = self.text_objects1('PARA HUIR A TODA COSTA Y NO EXTINGUIROS', stext)
            textSurf5, textRect5 = self.text_objects1('Usa la flecha de arriba y la de abajo para esquivar meteoritos', stext)
            textSurf6, textRect6 = self.text_objects1('Y el espacio para rotar la nave', stext)
            textSurf7, textRect7 = self.text_objects1('BUENA SUERTE CAMARADA', stext)
            textSurf8, textRect8 = self.text_objects1('Creado por Tirso Vaquero :)', stext)
            textRect.center = (400, 525)
            textRect2.center = (400, 100)
            textRect3.center = (400, 125)
            textRect4.center = (400, 150)
            textRect5.center = (400, 250)
            textRect6.center = (400, 275)
            textRect7.center = (400, 325)
            textRect8.center = (625, 575)
            self.pantalla.blit(textSurf, textRect)
            self.pantalla.blit(textSurf2, textRect2)
            self.pantalla.blit(textSurf3, textRect3)
            self.pantalla.blit(textSurf4, textRect4)
            self.pantalla.blit(textSurf5, textRect5)
            self.pantalla.blit(textSurf6, textRect6)
            self.pantalla.blit(textSurf7, textRect7)
            self.pantalla.blit(textSurf8, textRect8)
            self.pantalla.blit(corazon, (0, 575))

            pg.display.update()
            self.clock.tick(15)
            pg.display.flip()
    def records_levelp(self):
        recordp = True
        while recordp:
            events = pg.event.get()
            for event in events:
                if event.type == pg.QUIT:
                    pg.quit()
                    sys.exit()
            self.pantalla.fill((0, 0, 0))
            Largetext = pg.font.Font('static/VT323-Regular.ttf', 200)
            bigtext = pg.font.Font('static/VT323-Regular.ttf', 500)
            TextSurf, TextRect = self.text_objects('RECORDS', Largetext)
            puntos = self.meteoritos.puntuacion
            vidas = self.nave.vidas
            numM = self.meteoritos.meteoritos_pasados
            TextSurf1, TextRect1 = self.text_objects1((f"Tu puntuacion ha sido de {puntos} puntos"), Largetext)
            TextSurf2, TextRect2 = self.text_objects1((f"Has acabado con {vidas} vidas"), Largetext)
            TextSurf3, TextRect3 = self.text_objects1((f"Has esquivado {numM} meteoritos"), Largetext)
            textSurf4, textRect4 = self.text_objects1('SIGUIENTE NIVEL', Largetext)
            textSurf5, textRect5 = self.text_objects1('SALIR', Largetext)
            textSurf6, textRect6 = self.level_p('LEVEL', bigtext)
            textSurf7, textRect7 = self.level_p('PASSED', bigtext)
            TextRect.center = (400, 25)
            TextRect1.center = (400, 75)
            TextRect2.center = (400, 100)
            TextRect3.center = (400, 125)
            textRect4.center = (175, 525)
            textRect5.center = (625, 525)
            textRect6.center = (400, 250)
            textRect7.center = (400, 350)
            self.pantalla.blit(TextSurf, TextRect)
            self.pantalla.blit(TextSurf1, TextRect1)
            self.pantalla.blit(TextSurf2, TextRect2)
            self.pantalla.blit(TextSurf3, TextRect3)
            self.pantalla.blit(textSurf6, textRect6)
            self.pantalla.blit(textSurf7, textRect7)
            mouse = pg.mouse.get_pos()
            click = pg.mouse.get_pressed()
            if 50+250 > mouse[0] > 50 and 500+50 > mouse[1] > 500:
                print('entro en el if 1')
                pg.draw.rect(self.pantalla, (255, 255, 255), (50, 500, 250, 50))
                if click[0] == 1:
                    print(self.estado)
                    self.estado = 5

            else:
                print('entro en el else1')
                pg.draw.rect(self.pantalla, (155, 155, 155), (50, 500, 250, 50))
            if 500+250 > mouse[0] > 500 and 500+50 > mouse[1] > 500:
                print('entro en el if 2')
                pg.draw.rect(self.pantalla, (255, 255, 255), (500, 500, 250, 50))
                if click[0] == 1:
                    self.estado = 8

            else:
                pg.draw.rect(self.pantalla, (155, 155, 155), (500, 500, 250, 50))
                print('entro en el else 2')
            if 775+25 > mouse[0] > 775 and 1+25 > mouse[1] > 1:
                if click[0] == 1:
                    self.estado = 10
            else:
                pass
            self.pantalla.blit(textSurf4, textRect4)
            self.pantalla.blit(textSurf5, textRect5)
            self.pantalla.blit(yoshi, (775, 1))
            pg.display.update()
            self.clock.tick(15)
            self.main_loop()
            pg.display.flip()
    def records_levelc(self):
        recordc = True
        while recordc:
            events = pg.event.get()
            for event in events:
                if event.type == pg.QUIT:
                    pg.quit()
                    sys.exit()
            self.pantalla.fill((0, 0, 0))
            Largetext = pg.font.Font('static/VT323-Regular.ttf', 200)
            bigtext = pg.font.Font('static/VT323-Regular.ttf', 500)
            TextSurf, TextRect = self.text_objects('RECORDS', Largetext)
            puntos = self.meteoritos.puntuacion
            vidas = self.nave.vidas
            numM = self.meteoritos.meteoritos_pasados
            TextSurf1, TextRect1 = self.text_objects1((f"Tu puntuacion ha sido de {puntos} puntos"), Largetext)
            TextSurf2, TextRect2 = self.text_objects1((f"Has acabado con {vidas} vidas"), Largetext)
            TextSurf3, TextRect3 = self.text_objects1((f"Has esquivado {numM} meteoritos"), Largetext)
            textSurf4, textRect4 = self.text_objects1('ESTADISTICAS', Largetext)
            textSurf5, textRect5 = self.text_objects1('SALIR', Largetext)
            textSurf6, textRect6 = self.level_p('GAME', bigtext)
            textSurf7, textRect7 = self.level_p('COMPLETED', bigtext)
            TextRect.center = (400, 25)
            TextRect1.center = (400, 75)
            TextRect2.center = (400, 100)
            TextRect3.center = (400, 125)
            textRect4.center = (175, 525)
            textRect5.center = (625, 525)
            textRect6.center = (400, 250)
            textRect7.center = (400, 350)
            self.pantalla.blit(TextSurf, TextRect)
            self.pantalla.blit(TextSurf1, TextRect1)
            self.pantalla.blit(TextSurf2, TextRect2)
            self.pantalla.blit(TextSurf3, TextRect3)
            self.pantalla.blit(textSurf6, textRect6)
            self.pantalla.blit(textSurf7, textRect7)
            mouse = pg.mouse.get_pos()
            click = pg.mouse.get_pressed()
            if 50+250 > mouse[0] > 50 and 500+50 > mouse[1] > 500:
                pg.draw.rect(self.pantalla, (255, 255, 255), (50, 500, 250, 50))
                '''
                if click[0] == 1:
                    self.estado = 5
                    self.reiniciar_lp()
                    self.main_loop()
                '''
            else:
                pg.draw.rect(self.pantalla, (155, 155, 155), (50, 500, 250, 50))
            if 500+250 > mouse[0] > 500 and 500+50 > mouse[1] > 500:
                pg.draw.rect(self.pantalla, (255, 255, 255), (500, 500, 250, 50))
                if click[0] == 1:
                    self.estado = 8
                    self.main_loop()
            else:
                pg.draw.rect(self.pantalla, (155, 155, 155), (500, 500, 250, 50))
            self.pantalla.blit(textSurf4, textRect4)
            self.pantalla.blit(textSurf5, textRect5)
            pg.display.update()
            self.clock.tick(15)
            pg.display.flip()
    def nivel1(self):

        game_over = False
        while not game_over:
            dt = self.clock.tick(60)
            events = pg.event.get()
            for event in events:
                if event.type == pg.QUIT:
                    pg.quit()
                    sys.exit()
            self.movimiento()
            if self.nave.comprobar_colision(self.meteoritos):
                self.meteoritos.puntuacion -= 2
            if self.nave.status == NaveStatus.muerta:
                self.nave.vidas -= 1
                self.meteoritos.num_meteoritos = 0
                self.meteoritos.vx = 7
                if self.nave.vidas == 0:
                    game_over = True
                    self.estado = 3
                    self.main_loop()
                else:
                    self.nave.reiniciar()
            Spuntuacion = self.cuenta_vidas.render(str(self.meteoritos.puntuacion), True, (155, 155, 155))
            SnumM = self.cuenta_vidas.render(str(self.meteoritos.meteoritos_pasados), True, (155, 155, 155))
            Svidas = self.cuenta_vidas.render(str(self.nave.vidas), True, (155, 155, 155))
            SPalabra_vidas = self.cuenta_vidas.render('vidas', True, (155, 155, 155))
            Rpalabra_vidas = Svidas.get_rect(topleft=(30, 25))
            SPalabra_puntuacion = self.cuenta_vidas.render('Puntuación =', True, (155, 155, 155))
            Rpalabra_puntuacion = Svidas.get_rect(topleft=(125, 25))
            Rpuntuacion = Svidas.get_rect(topleft=(275, 25))
            Rvidas = Svidas.get_rect(topright=(25, 25))
            RnumM = Svidas.get_rect(topright=(600, 25))
            SPalabra_numM = self.cuenta_vidas.render('Meteoritos Pasados =', True, (155, 155, 155))
            Rpalabra_numM = Svidas.get_rect(topleft=(335, 25))
            self.control_eventos()
            self.todos.update(dt)
            self.todos.draw(self.pantalla)
            if self.meteoritos.num_meteoritos > 1 and self.nivel == 0:
                self.meteoritos.puntuacion += 50
                self.meteoritos.image = pg.image.load('static/meteorito_mediano.png')
                self.meteoritos.num_meteoritos = 0
                self.meteoritos.vx = 7
                self.nivel = 1
            if self.meteoritos.num_meteoritos > 1 and self.nivel == 1:
                self.meteoritos.puntuacion += 50
                self.meteoritos.image = pg.image.load('static/meteorito_grande.png')
                self.meteoritos.num_meteoritos = 0
                self.meteoritos.vx = 7
                self.nivel = 2
                self.nave.vx = 7
            if self.meteoritos.num_meteoritos > 1 and self.nivel == 2:
                self.meteoritos.vx = 0
                self.planeta2.update(dt)
                self.planeta2.draw(self.pantalla)
                self.nave.rect.x += 1
                if self.nave.rect.x > 375:
                    self.nave.rect.x = 375
                    self.nave.rect.y = 229
                    self.estado = 4
                    self.main_loop()
            if self.nave.rotando == True:
                self.meteoritos.puntuacion += 1
            self.pantalla.blit(SPalabra_vidas, (Rpalabra_vidas.x, Rpalabra_vidas.y))
            self.pantalla.blit(SPalabra_puntuacion, (Rpalabra_puntuacion.x, Rpalabra_puntuacion.y))
            self.pantalla.blit(SPalabra_numM, (Rpalabra_numM.x, Rpalabra_numM.y))
            self.pantalla.blit(Svidas, (Rvidas.x, Rvidas.y))
            self.pantalla.blit(SnumM, (RnumM.x, RnumM.y))
            self.pantalla.blit(Spuntuacion, (Rpuntuacion.x, Rpuntuacion.y))
            pg.display.flip()
    def historia(self):
        historia = True
        while historia:
            events = pg.event.get()
            for event in events:
                if event.type == pg.QUIT:
                    pg.quit()
                    sys.exit()
            self.pantalla.fill((0, 0, 0))
            Largetext = pg.font.Font('static/VT323-Regular.ttf', 200)
            TextSurf, TextRect = self.text_objects('ESCAPA DE ALDEBARAN', Largetext)
            TextRect.center = (400, 25)
            self.pantalla.blit(TextSurf, TextRect)
            mouse = pg.mouse.get_pos()
            click = pg.mouse.get_pressed()
            if 100+600 > mouse[0] > 100 and 500+50 > mouse[1] > 500:
                pg.draw.rect(self.pantalla, (255, 255, 255), (100, 500, 600, 50))
                if click[0] == 1:
                    self.estado = 6
                    self.main_loop()
            else:
                pg.draw.rect(self.pantalla, (155, 155, 155), (100, 500, 600, 50))

            stext = pg.font.Font('static/VT323-Regular.ttf', 1)
            textSurf, textRect = self.text_objects1('PULSA PARA EMPEZAR', Largetext)
            textSurf2, textRect2 = self.text_objects1('Al llegar al planeta todo parecia estar bien', stext)
            textSurf3, textRect3 = self.text_objects1('Pero el segundo dia la raza natal os atacó', stext)
            textSurf4, textRect4 = self.text_objects1('Asi que os subisteis a la nave y huisteis', stext)
            textSurf5, textRect5 = self.text_objects1('Usa la flecha de arriba y la de abajo para esquivar meteoritos', stext)
            textSurf6, textRect6 = self.text_objects1('Y el espacio para rotar la nave', stext)
            textSurf7, textRect7 = self.text_objects1('BUENA SUERTE DE NUEVO CAMARADA', stext)
            textRect.center = (400, 525)
            textRect2.center = (400, 100)
            textRect3.center = (400, 125)
            textRect4.center = (400, 150)
            textRect5.center = (400, 250)
            textRect6.center = (400, 275)
            textRect7.center = (400, 325)
            self.pantalla.blit(textSurf, textRect)
            self.pantalla.blit(textSurf2, textRect2)
            self.pantalla.blit(textSurf3, textRect3)
            self.pantalla.blit(textSurf4, textRect4)
            self.pantalla.blit(textSurf5, textRect5)
            self.pantalla.blit(textSurf6, textRect6)
            self.pantalla.blit(textSurf7, textRect7)

            pg.display.update()
            self.clock.tick(15)
            pg.display.flip()
    def main_loop(self):
        running = True
        while running:
            #pg.mixer.music.play()
            dt = self.clock.tick(60)
            events = pg.event.get()
            for event in events:
                if event.type == pg.QUIT:
                    pg.quit()
                    sys.exit()
            if self.estado == 1:
                self.game_intro()
            elif self.estado == 2:
                self.nivel1()
            elif self.estado == 3:
                self.records_gameOver()
            elif self.estado == 4:
                self.records_levelp()
            elif self.estado == 5:
                self.historia()
            elif self.estado == 6:
                self.reiniciar_lp()
                self.nivel2()
            elif self.estado == 7:
                self.records_levelc()
            elif self.estado == 8:
                pg.quit()
                sys.exit()
            elif self.estado == 10:
                self.yoshi()