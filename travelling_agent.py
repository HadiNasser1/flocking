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
    
    delta_time: float = .1
    p_join: float = 0.6
    p_leave: float = 0.4
    t_join: int = 2
    t_leave: int = 2



# define Agent class
class TravellingAgent(Agent):
    config: FlockingConfig

    def on_spawn(self):
        # method is replaced for __init__():
        self.state = "wander"
        self.p_join = self.config.p_join
        self.p_leave = self.config.p_leave 
        self.t_join = self.config.t_join
        self.t_leave = self.config.t_leave
        self.join_timer = 0
        self.leave_timer = 0
        

    def update(self):
        self.there_is_no_escape()

        # get neighbours
        neighbours = self.check_bird_neighbours()

        if self.state == "wander":
            if self.is_join(len(neighbours)) :
                self.state = "join"

        elif self.state == "join":
            self.join_timer += 1

            if self.join_timer == self.t_join and self.on_site():
                self.state = "still"
                self.join_timer = 0

        elif self.state == "still" and self.on_site():
            self.freeze_movement()
            if self.is_leave(len(neighbours)):
                self.state = "leave"
                self.continue_movement()
            
        elif self.state == "leave":
            self.leave_timer += 1 
            if self.leave_timer == self.t_leave:
                self.state = "wander"
                self.leave_timer = 0



    
    # return list of id of neighbours in the proximity
    def check_bird_neighbours(self):
        return [agent for agent, _ in self.in_proximity_accuracy()]

    def join_function(self, x):
        return (x**2)/100
    
    def is_join(self, nr_neighhours):
        if self.on_site() and probability(self.join_function(nr_neighhours)):
            return True
        else:
            return False
    
    # method return a probability the agent leaves the site
    '''def leave_function(self, x):
        return (-1/10) * (x**2) + 1'''
    
    def leave_function(self, x):
        return (-1/100) * (x**2) + 0.1

    # check if the agent would leave 
    def is_leave(self, nr_neighbours):
        
        if self.on_site() and probability(self.leave_function(nr_neighbours)):
            return True
        else:
            return False




(Simulation(FlockingConfig(radius = 50, movement_speed=10, seed = 1 ))
        .spawn_site("images/circle@200.png", x = 400, y = 400)
        .batch_spawn_agents(100, TravellingAgent, images=["images/bird.png"])
        .run()
        )



# Uncomment if you want to plot the number of agents that turn red 
'''
plot = sns.relplot(x = df["frame"], y = df["agents"], hue = df["image_index"], kind = "line")
plot.savefig("agent.png", dpi = 300)'''

# alias would create the name for the derived column