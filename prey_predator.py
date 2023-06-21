from vi import Agent, Simulation, Config, HeadlessSimulation, probability
import polars as pl
import seaborn as sns

from ctypes import alignment
from enum import Enum, auto

import pygame as pg
from pygame.math import Vector2
from vi.config import dataclass, deserialize
import random
import math


@deserialize
@dataclass
class FlockingConfig(Config):
    
    p_fox: float = 0.3
    p_rabbit: float = 0.0015




# define Agent classc
class Prey(Agent):
    config: FlockingConfig

    def on_spawn(self):
        # method is replaced for __init__():
        self.p_live = self.config.p_rabbit
        self.role = "prey"
       
        

    def update(self):
        self.there_is_no_escape()
        # get neighbours
        neighbours = list(self.in_proximity_accuracy().without_distance())

        self.save_data("alive", self.is_alive())
        self.save_data("role", self.role)

        
        if probability(self.p_live):
            self.reproduce()

        # when the rabbit collides the fox
        if self.encounter_predator(neighbours) and self.is_alive():
            self.kill()
        

    def is_predator(self, agent):
        return True if agent.role == "predator" else False
    
    def encounter_predator(self, neighbours):
        return any([self.is_predator(neighbour) for neighbour in neighbours])

class Predator(Agent):
    config: FlockingConfig



    def on_spawn(self):
        self.p_live = self.config.p_fox
        self.role = "predator"
        self.energy = 1.00
        self.move = self.move * -1

    def update(self):
        self.there_is_no_escape()
        self.save_data("alive", self.is_alive())
        self.save_data("role", self.role)

        wander_weight = 0.1
        wander_angle = random.uniform(0, 2 * math.pi)
        wander_direction = Vector2(math.cos(wander_angle), math.sin(wander_angle))
        self.wander_direction = wander_direction
        self.move += wander_direction * wander_weight

        if Vector2.length(self.move) > self.config.movement_speed:
            self.move = Vector2.normalize(self.move) * self.config.movement_speed

        neighbours = list(self.in_proximity_accuracy().without_distance())
        
        if self.eat_prey(neighbours):
            self.energy += 0.8
            self.reproduce()

        self.energy -= 0.00175
        #if self.energy <= 0.0:
        #    self.kill()
        
        if random.random() > 0.987 + self.energy / 100:
            self.kill()

    def is_prey(self,agent):
        return True if agent.role == "prey" else False
    
    def eat_prey(self, neighbours):
        return any([self.is_prey(neighbour) for neighbour in neighbours])


    

        




df = (Simulation(FlockingConfig(radius = 10, movement_speed=1))
        .batch_spawn_agents(20, Predator, images=["red.jpg"])
        .batch_spawn_agents(70, Prey, images=["black.jpg", "black.jpg"])
        .run()
        .snapshots
        .groupby(["frame","role",  "alive"])
        .agg(pl.count("id").alias("agents")).sort(["frame", "role",])
        #.write_csv("count_agents.csv")
        )




# Uncomment if you want to plot the number of agents that turn red 

plot = sns.relplot(x = df["frame"], y = df["agents"], hue = df["role"], kind = "line")
sns.relplot(x = df["frame"], y = df["agents"], hue = df["role"], kind = "line")
plot.savefig("agent.png", dpi = 300)

# alias would create the name for the derived column