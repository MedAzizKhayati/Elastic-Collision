import pygame
import math
from pygame import gfxdraw
import random
import numpy as np
import time

pygame.init()
width = 1280
height = 720
win = pygame.display.set_mode((width, height))
pygame.display.set_caption("Gravity Ball")

g = 1000
click = False
clicked = False
balls = []
init = time.time()


class ball:
    def __init__(self, x, y, vx, vy, t0):
        self.x0 = x
        self.y0 = y
        self.vx = vx
        self.vy = vy
        self.t0 = t0
        self.coords = [x, y]
        self.radius = random.randint(10, 50)
        self.mass = self.radius * self.radius / 10

    def update(self, t, other):
        def future_r(ob1, ob2, t):
            dt = 0.01
            t1 = t - ob1.t0 + dt
            t2 = t - ob2.t0 + dt
            coords1 = [ob1.vx * t1 + ob1.x0, g * t1 * t1 / 2 + ob1.vy * t1 + ob1.y0]
            coords2 = [ob2.vx * t2 + ob2.x0, g * t2 * t2 / 2 + ob2.vy * t2 + ob2.y0]
            coords1 = np.array(coords1)
            coords2 = np.array(coords2)
            vec = coords1 - coords2
            return np.linalg.norm(vec)

        keys = pygame.key.get_pressed()
        if balls[0] == self and self.mass < 101:
            if keys[pygame.K_UP]:
                self.mass *= 10
                print(self.mass)
            elif keys[pygame.K_DOWN]:
                self.mass /= 10
                print(self.mass)
        t = t - self.t0
        if self.coords[1] >= height - self.radius and 30 <= g * t + self.vy:
            v2 = - (g * t + self.vy) * 0.7
            vy = v2 - g * t
            self.y0 += t * (self.vy - vy)
            self.vy = vy
            self.y0 = height - self.radius - g * t * t / 2 - self.vy * t
        elif self.coords[1] >= height - self.radius and -30 <= g * t + self.vy < 30:
            v2 = 0
            vy = v2 - g * t
            self.y0 += t * (self.vy - vy)
            self.vy = vy
            self.y0 = height - self.radius - g * t * t / 2 - self.vy * t
        self.coords[0] = self.vx * t + self.x0
        self.coords[1] = g * t * t / 2 + self.vy * t + self.y0
        if self.coords[0] > width - self.radius and self.vx > 0 or (self.coords[0] < self.radius and self.vx < 0):
            self.x0 += 2 * self.vx * t
            self.vx *= -1
        a = np.array(self.coords)
        for i, j in zip(other, range(len(other))):
            b = np.array(i.coords)
            ba = a - b
            r = np.linalg.norm(ba)
            if self.radius + i.radius >= r > future_r(self, i, t + self.t0):
                v1x, v1y = elastic_collision(self, i, t + self.t0)
                v2x, v2y = elastic_collision(i, self, t + self.t0)

                v1x *= 1
                v1y *= 1
                v2x *= 1
                v2y *= 1
                t1 = t + self.t0 - i.t0

                v1y = v1y - g * t
                v2y = v2y - g * t1

                self.x0 += t * (self.vx - v1x)
                i.x0 += (t + self.t0 - i.t0) * (i.vx - v2x)
                self.y0 += t * (self.vy - v1y)
                i.y0 += (t + self.t0 - i.t0) * (i.vy - v2y)

                self.vx = v1x
                self.vy = v1y
                i.vx = v2x
                i.vy = v2y
                if r < self.radius + i.radius:
                    r = self.radius + i.radius
                    if self.coords[1] < i.coords[1]:
                        ob1 = self
                        ob2 = i
                        t1 = t
                    else:
                        ob1 = i
                        ob2 = self
                    a = np.array(self.coords)
                    b = np.array(i.coords)
                    ab = a - b
                    if ab[1] > 0:
                        ab = - ab
                    theta = math.atan2(ab[1], ab[0])
                    if ob1.radius == ob2.radius and theta in [0, math.pi]:
                        if ob1.coords[0] > ob2.coords[0]:
                            theta = 0
                        else:
                            theta = math.pi
                    x = r * math.cos(theta) + ob2.coords[0]
                    if not ab[0]:
                        y = ob2.coords[1] - r
                    else:
                        y = ab[1] / ab[0] * x + ob2.coords[1] - ab[1] / ab[0] * ob2.coords[0]

                    ob1.y0 = y - g * t1 * t1 / 2 - ob1.vy * t1
                    ob1.x0 = x - ob1.vx * t1

    def draw(self):
        draw_circle(win, self.coords[0], self.coords[1], self.radius, (0, 0, 0))


temp = ball(0, 0, 0, 0, init)


def draw_circle(surface, x, y, radius, color):
    x = int(x)
    y = int(y)
    gfxdraw.aacircle(surface, x, y, radius, color)
    gfxdraw.filled_circle(surface, x, y, radius, color)


def vector_angle(v):
    ba = np.array(v)
    dot = ba[0]
    det = ba[1]
    return math.atan2(det, dot)


def elastic_collision(ob1, ob2, t):
    t1 = t - ob1.t0
    t2 = t - ob2.t0

    v1y = g * t1 + ob1.vy
    v2y = g * t2 + ob2.vy

    theta1 = vector_angle([ob1.vx, v1y])
    theta2 = vector_angle([ob2.vx, v2y])
    # if height - ob1.radius == ob1.coords[1] and height - ob2.radius == ob2.coords[1]:
    #     phi = 0
    # else:
    dx = ob2.coords[0] - ob1.coords[0]
    if dx == 0:
        phi = math.pi / 2
    else:
        phi = math.atan((ob2.coords[1] - ob1.coords[1]) / dx)

    m1 = ob1.mass
    m2 = ob2.mass

    v1 = math.sqrt(ob1.vx * ob1.vx + v1y * v1y)
    v2 = math.sqrt(ob2.vx * ob2.vx + v2y * v2y)

    vx = (v1 * math.cos(theta1 - phi) * (m1 - m2) + 2 * m2 * v2 * math.cos(theta2 - phi)) / (m1 + m2)
    vy = vx

    vx = vx * math.cos(phi) + v1 * math.sin(theta1 - phi) * math.cos(phi + math.pi / 2)
    vy = vy * math.sin(phi) + v1 * math.sin(theta1 - phi) * math.sin(phi + math.pi / 2)
    return vx, vy


def spawn_ball(mx, my, x, y):
    global click, clicked, temp, balls

    def velocity(mousex, mousey, xx, yy):
        a = np.array([xx, yy])
        b = np.array([mousex, mousey])
        ba = a - b
        r = np.linalg.norm(ba)
        dot = ba[0]
        det = -ba[1]
        angle = math.atan2(det, dot)
        sin = math.sin(angle)
        cos = math.cos(angle)
        vx = r * cos * 4
        vy = -r * sin * 4
        return vx, vy

    keys = pygame.key.get_pressed()
    if keys[pygame.K_r]:
        x, y = mx, my
        balls.append(ball(x, y, 0, 0, time.time()))
    if click and not clicked:
        clicked = True
        x, y = mx, my
        temp = ball(mx, my, 0, 0, time.time())
        temp.draw()
    elif click and clicked:
        temp.radius = int(20 * math.sin(time.time()*2) + 30)
        temp.mass = temp.radius * temp.radius / 10
        pygame.draw.aaline(win, (0, 0, 0), (x, y), (mx, my))
        temp.vx, temp.vy = velocity(mx, my, x, y)
        temp.draw()
    elif not click and clicked:
        clicked = False
        temp.t0 = time.time()
        balls.append(temp)
    return x, y


def main():
    global click, clicked, balls, temp
    run = True
    # clock = pygame.time.Clock()
    mx, my = 0, 0
    x, y = 0, 0
    while run:
        win.fill((255, 255, 255))
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
        i = 0
        while i in range(len(balls)):
            try:
                balls[i].draw()
                balls[i].update(time.time(), balls[i + 1:])
            except:
                balls.pop(i)
                i -= 1
            i += 1
        x, y = spawn_ball(mx, my, x, y)
        click = False
        if pygame.mouse.get_pressed()[0]:
            click = True
        if pygame.mouse.get_pressed()[1]:
            balls = []
        mx, my = pygame.mouse.get_pos()
        pygame.display.update()


main()
pygame.quit()
