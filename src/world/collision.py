import pygame

from src.utils.config import GRAVITY


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


def handle_ladder(player, ladder, dt, climb_speed):
    keys = pygame.key.get_pressed()
    up_pressed = keys[pygame.K_UP] or keys[pygame.K_w] or keys[pygame.K_SPACE]
    down_pressed = keys[pygame.K_DOWN] or keys[pygame.K_s]
    left_pressed = keys[pygame.K_LEFT] or keys[pygame.K_a]
    right_pressed = keys[pygame.K_RIGHT] or keys[pygame.K_d]

    if not up_pressed and not down_pressed:
        return False

    if player.rect.centerx > ladder.rect.centerx and player.rect.bottom - 14 > ladder.rect.top:
        player.pos.x = ladder.rect.left - player.width + 10

    player.vel.x = 0
    player.vel.y = 0
    player.on_ground = True
    player.move_input = False

    if up_pressed:
        player.pos.y -= climb_speed * dt
    elif down_pressed:
        player.pos.y += climb_speed * dt

    if left_pressed:
        player.pos.x -= climb_speed * dt
    elif right_pressed:
        player.pos.x += climb_speed * dt

    return True


def snap_to_platform(obj, platforms):
    hit = obj.rect.collidelist(platforms)
    if hit != -1:
        obj.pos.x = platforms[hit].rect.centerx - obj.width
        obj.pos.y = platforms[hit].rect.top - obj.height


def collect_artifacts(player, artifacts, active_objects=None):
    hit = player.rect.collidelist(artifacts)
    if hit == -1:
        return

    artifact = artifacts[hit]
    player.artifacts.append(artifact)
    artifact.active = False
    del artifacts[hit]
    if active_objects is not None and artifact in active_objects:
        active_objects.remove(artifact)


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
