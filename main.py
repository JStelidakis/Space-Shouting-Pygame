from random import randint,uniform
import pygame
from os.path import join

class Player(pygame.sprite.Sprite):
    def __init__(self, groups):
        super().__init__(groups)
        self.image =  pygame.image.load(join('images/player.png')).convert_alpha()
        self.rect = self.image.get_frect(center =(WINDOW_WIDTH /2,WINDOW_HEIGHT / 2))
        self.direction = pygame.math.Vector2()
        self.speed = 300

        #cooldown
        self.can_shoot =True
        self.laser_shoot_time = 0
        self.cooldown_duration = 400

        #transform test
        #self.image = pygame.transform.rotate(self.image,90)

        #mask
        self.mask = pygame.mask.from_surface(self.image)
        
    
    def laser_timer(self):
        if not self.can_shoot:
            current_time =pygame.time.get_ticks()
            if current_time -self.laser_shoot_time >= self.cooldown_duration:
                self.can_shoot =True

    def update(self,dt): 
        keys =  pygame.key.get_pressed()
        self.direction.x =int(keys[pygame.K_RIGHT]) - int(keys[pygame.K_LEFT])
        self.direction.y =int(keys[pygame.K_DOWN]) - int(keys[pygame.K_UP])
        self.direction = self.direction.normalize() if self.direction else self.direction
        self.rect.center += self.direction * self.speed * dt

        
        recent_keys = pygame.key.get_just_pressed()
        if recent_keys[pygame.K_SPACE] and self.can_shoot:
            Laser(laser_surf,self.rect.midtop,(all_sprites,laser_Sprites))
            self.can_shoot = False
            self.laser_shoot_time = pygame.time.get_ticks()
            laser_Sound.play()
        
        self.laser_timer()

class star(pygame.sprite.Sprite):
     def __init__(self, groups,surf):
        super().__init__(groups)
        self.image = surf
        self.rect = self.image.get_frect(center = (randint(0, WINDOW_WIDTH),randint(0,WINDOW_HEIGHT)))

class Laser(pygame.sprite.Sprite):
    def __init__(self, surf,pos,groups):
        super().__init__(groups)
        self.image = surf
        self.rect = self.image.get_frect(midbottom = pos)
        self.mask = pygame.mask.from_surface(self.image)

    
    def update(self, dt):
        self.rect.centery -= 400 * dt
        if self.rect.bottom < 0:
            self.kill()

class Meteor(pygame.sprite.Sprite):
    def __init__(self,surf,pos, groups):
        super().__init__(groups)
        self.original_surf = surf
        self.image = surf 
        self.rect = self.image.get_frect(center = pos)
        self.__start_time = pygame.time.get_ticks()
        self.lifetime = 3000
        self.direction = pygame.Vector2(uniform(-0.5, 0.5),1)
        self.speed = randint(400,500)
        self.mask = pygame.mask.from_surface(self.image)
        self.rotation_Speed = randint(40,80)
        self.rotation = 0


    def update(self, dt):
        self.rect.center += self.direction * self.speed *dt
        if pygame.time.get_ticks() - self.__start_time >= self.lifetime:
            self.kill()
        self.rotation += self.rotation_Speed * dt
        self.image = pygame.transform.rotozoom(self.original_surf, self.rotation, 1)
        self.rect = self.image.get_frect(center = self.rect.center)
            
class AnimatedExplosion(pygame.sprite.Sprite):
   def __init__(self,frames,pos,groups):
      super().__init__(groups)
      self.frames = frames
      self.frames_index = 0
      self.image = self.frames[self.frames_index]
      self.rect = self.image.get_frect(center = pos)


   def update(self, dt):
        self.frames_index += 20 *  dt
        if self.frames_index < len(self.frames):
          self.image = self.frames[int(self.frames_index)]
        else:
            self.kill
       

def collisions():
    global running
    collision_sprite = pygame.sprite.spritecollide(player,meteor_sprites,True, pygame.sprite.collide_mask)
    if collision_sprite:
        running =False
        damage_Sound.play()
    
    for laser in laser_Sprites:
        collid_sprites = pygame.sprite.spritecollide(laser,meteor_sprites,True)
        if collid_sprites:
            laser.kill()
            AnimatedExplosion(explosion_frames, laser.rect.midtop,all_sprites)
            explosion_sound.play()

def display_score():
    current_time = pygame.time.get_ticks() // 100
    text_surf =  font.render(str(current_time),True,(240,240,240))
    text_rect = text_surf.get_frect(midbottom =(WINDOW_WIDTH /2,WINDOW_HEIGHT - 50))
    display_surface.blit(text_surf,text_rect)
    pygame.draw.rect(display_surface,'white',text_rect.inflate(20,16).move(0,-8),5,5)

# general setup
pygame.init()
WINDOW_WIDTH,WINDOW_HEIGHT = 1280,720
display_surface = pygame.display.set_mode((WINDOW_WIDTH,WINDOW_HEIGHT))
pygame.display.set_caption('space shooter')
running = True
clock= pygame.time.Clock()

#imports
star_surf =  pygame.image.load(join('images/star.png')).convert_alpha()
meteor_surf = pygame.image.load(join('images/meteor.png')).convert_alpha()
laser_surf = pygame.image.load(join('images/laser.png')).convert_alpha()
font = pygame.font.Font(join('images/Oxanium-Bold.ttf'),40)
explosion_frames = [pygame.image.load(join('images','explosion',f'{i}.png')).convert_alpha() for i in range(21)]

laser_Sound = pygame.mixer.Sound(join('audio','laser.wav'))
laser_Sound.set_volume(0.5)
explosion_sound = pygame.mixer.Sound(join('audio','explosion.wav'))
explosion_sound.set_volume(0.5)
damage_Sound = pygame.mixer.Sound(join('audio','damage.ogg'))
game_music = pygame.mixer.Sound(join('audio','game_music.wav'))
game_music.set_volume(0.2)
game_music.play(loops = -1)

#sprites
all_sprites = pygame.sprite.Group()
meteor_sprites = pygame.sprite.Group()
laser_Sprites =  pygame.sprite.Group()
for i in range(20):
    star(all_sprites,star_surf)
player = Player(all_sprites)
score = pygame.sprite.Group()

 #custom events -> meteor event
meteor_event = pygame.event.custom_type()
pygame.time.set_timer(meteor_event,500)


while running:
    dt = clock.tick() /1000
    
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        if event.type == meteor_event:
            x,y = randint(0,WINDOW_WIDTH),randint(-200,-100)
            Meteor(meteor_surf,(x,y),(all_sprites,meteor_sprites))

    all_sprites.update(dt) 
    collisions()

    display_surface.fill('#3a2e3f') 
    display_score()
    all_sprites.draw(display_surface)

    pygame.display.update()

pygame.quit()  