import pygame

from src.utils.config import GRAVITY, PLAYER_SPEED
from pygame.locals import *
    

def apply_gravity(entity, dt, gravity=GRAVITY):
    entity.vel.y += gravity * dt


def move_with_platforms(entity, platforms, dt):
    entity.pos.x += entity.vel.x * dt
    hit = entity.rect.collidelist(platforms)
    if hit != -1:
        if entity.vel.x > 0:
            entity.pos.x = platforms[hit].rect.left - entity.width
        elif entity.vel.x < 0:
            entity.pos.x = platforms[hit].rect.right
        entity.vel.x = 0

    entity.on_ground = False
    entity.pos.y += entity.vel.y * dt
    hit = entity.rect.collidelist(platforms)
    if hit != -1:
        if entity.vel.y > 0:
            entity.pos.y = platforms[hit].rect.top - entity.height
            entity.on_ground = True
        elif entity.vel.y < 0:
            entity.pos.y = platforms[hit].rect.bottom
        entity.vel.y = 0
    else:
        _snap_to_ground(entity, platforms)


def _snap_to_ground(entity, platforms, tolerance=2):
    if entity.vel.y < 0:
        return

    entity_rect = entity.rect
    for platform in platforms:
        plat_rect = platform.rect
        if entity_rect.right <= plat_rect.left or entity_rect.left >= plat_rect.right:
            continue
        gap = plat_rect.top - entity_rect.bottom
        if 0 <= gap <= tolerance:
            entity.pos.y = plat_rect.top - entity.height
            entity.vel.y = 0
            entity.on_ground = True
            return


def handle_ladder(player, platforms, dt, climb_speed):
    keys = pygame.key.get_pressed()
    up_pressed = keys[pygame.K_UP] or keys[pygame.K_w] or keys[pygame.K_SPACE]
    down_pressed = keys[pygame.K_DOWN] or keys[pygame.K_s]
    left_pressed = keys[pygame.K_LEFT] or keys[pygame.K_a]
    right_pressed = keys[pygame.K_RIGHT] or keys[pygame.K_d]

    if not up_pressed and not down_pressed:
        return False

    player.vel.x = 0
    player.vel.y = 0
    player.on_ground = True
    player.move_input = False

    if left_pressed:
        player.pos.x -= climb_speed * dt
    elif right_pressed:
        player.pos.x += climb_speed * dt
    hit = player.rect.collidelist(platforms)
    if hit != -1:
        if right_pressed:
            player.pos.x = platforms[hit].rect.left - player.width
        elif left_pressed:
            player.pos.x = platforms[hit].rect.right

    if up_pressed:
        player.pos.y -= climb_speed * dt
    elif down_pressed:
        player.pos.y += climb_speed * dt
    hit = player.rect.collidelist(platforms)
    if hit != -1:
        if down_pressed:
            player.pos.y = platforms[hit].rect.top - player.height
            player.on_ground = True
        elif up_pressed:
            player.pos.y = platforms[hit].rect.bottom

    return True


def snap_to_platform(obj, platforms):
    if not platforms:
        return

    obj_rect = obj.rect
    best_platform = None
    best_distance = None

    for platform in platforms:
        plat_rect = platform.rect
        if not (plat_rect.left <= obj_rect.centerx <= plat_rect.right):
            continue

        target_y = plat_rect.top - obj.height
        distance = abs(obj.pos.y - target_y)
        if best_distance is None or distance < best_distance:
            best_distance = distance
            best_platform = platform

    if best_platform is None:
        hit = obj.rect.collidelist(platforms)
        if hit == -1:
            return
        best_platform = platforms[hit]

    plat_rect = best_platform.rect
    obj.pos.x = max(plat_rect.left, min(obj.pos.x, plat_rect.right - obj.width))
    obj.pos.y = plat_rect.top - obj.height


def collect_artifacts(player, artifacts, active_objects=None):
    hit = player.rect.collidelist(artifacts)
    if hit == -1:
        return None

    artifact = artifacts[hit]
    player.artifacts.append(artifact)
    artifact.active = False
    del artifacts[hit]
    if active_objects is not None and artifact in active_objects:
        active_objects.remove(artifact)
    return artifact


def collect_coins(player, coins, active_objects=None):
    hit = player.rect.collidelist(coins)
    if hit == -1:
        return None

    coin = coins[hit]
    coin.active = False
    del coins[hit]
    if active_objects is not None and coin in active_objects:
        active_objects.remove(coin)
    return coin


def apply_player_attack(player, enemies):
    if not player.consume_attack():
        return

    attack_rect = player.get_attack_rect()
    for enemy in enemies:
        if not enemy.active:
            continue
        if enemy.rect.colliderect(attack_rect):
            enemy.take_damage(1)


def get_ladder_hit(player, ladders):
    return player.rect.collidelist(ladders)

def handle_lake(player, lake, dt):
    keys = pygame.key.get_pressed()
 
    player.vel.x = 0
    move_speed = PLAYER_SPEED * 0.30
    if keys[pygame.K_LEFT] or keys[pygame.K_a]:
        player.vel.x = -move_speed
    if keys[pygame.K_RIGHT] or keys[pygame.K_d]:
        player.vel.x = move_speed
 
    gravity_scale = 1.3
    player.vel.y += GRAVITY * gravity_scale * dt

    if (keys[pygame.K_UP] or keys[pygame.K_w] or keys[pygame.K_SPACE]):
        player.vel.y -= GRAVITY * 1.31 * dt
 
    max_rise = -PLAYER_SPEED * 1.6
    max_fall = PLAYER_SPEED * 2.7
    player.vel.y = max(max_rise, min(player.vel.y, max_fall))
 
    player.pos.x += player.vel.x * dt
    current_step = lake.get_stair_index(player.rect.centerx)
    if(current_step is not None and current_step <= 1) or current_step is None:
        player.pos.y += player.vel.y * dt
 
    stair_support_y = lake.get_stair_support_y_for_rect(player.rect)
 
    if stair_support_y is None and player.pos.y - 1 < lake.rect.top:
        if player.vel.y < 0:
            player.vel.y = 30
 
    player.on_ground = False
 
    if stair_support_y is not None:
        snap_margin = max(4, lake.get_step_height())
        if player.rect.bottom >= stair_support_y - snap_margin:
            player.pos.y = stair_support_y - player.height
            if player.vel.y > 0:
                player.vel.y = 0
            player.on_ground = True
 
    if player.rect.bottom >= lake.rect.bottom:
        player.pos.y = lake.rect.bottom - player.height
        player.vel.y = 0
        player.on_ground = False
