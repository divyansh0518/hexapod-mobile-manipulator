"""Shared simulated/live controller. Rejects invalid kinematics before output."""
import numpy as np
from .model import Legs, ServoMap, finite
from .gait import Gait
from .arm import Arm

class Controller:
    def __init__(self,cfg):
        self.cfg=cfg;self.legs=Legs(cfg["geometry"]);self.gait=Gait(self.legs,cfg["gait"])
        self.arm=Arm(cfg["arm"]);self.mapper=ServoMap(cfg["servo"])
        self.arm_q=self.arm.home.copy();self.arm_goal=self.arm_q.copy()
        self.phase_time=0.;self.last_command=np.zeros(3)
        self.servo=self.mapper.encode(np.r_[np.concatenate([self.legs.ik(i,p) for i,p in enumerate(self.legs.home)]),self.arm_q])
    def set_target(self,xyz):
        neutral=np.concatenate([self.legs.ik(i,p) for i,p in enumerate(self.legs.home)])
        neutral_servo=self.mapper.encode(np.r_[neutral,self.arm_q])
        if np.linalg.norm(self.last_command)>.01 or np.max(abs(self.servo[:18]-neutral_servo[:18]))>.5:
            raise ValueError("Wait for base to settle at neutral stance")
        if np.linalg.norm(self.arm.fk(self.arm_goal)[:3,3]-finite(xyz))<.5:
            return
        self.arm_goal=self.arm.ik(xyz,seed=self.arm_q)
    def tick(self,dt,command=(0,0,0),gait="tripod",distance_mm=None,enabled=True):
        if not 0<dt<=.1: raise ValueError("Control interval out of range")
        cmd=finite(command)
        if cmd.shape!=(3,) or np.max(abs(cmd))>1: raise ValueError("Three normalized command axes in [-1,1] required")
        blocked=(self.cfg["control"]["require_range_sensor"] and distance_mm is None) or (distance_mm is not None and (not np.isfinite(distance_mm) or distance_mm<self.cfg["control"]["obstacle_stop_mm"]))
        if not enabled or blocked:
            # Hold current command; physical receiver watchdog governs power output.
            return self.servo.copy(),"inhibited"
        if np.linalg.norm(self.arm_goal-self.arm_q)>.001 and np.linalg.norm(cmd)>.01:
            raise ValueError("Manipulation requires a stationary base")
        # Slew joystick inputs; simulated feet remain an ideal flat-ground model.
        self.last_command+=np.clip(cmd-self.last_command,-dt,dt)
        self.phase_time+=dt
        feet,_=self.gait.targets(self.phase_time,self.last_command,gait)
        leg_q=np.concatenate([self.legs.ik(i,p) for i,p in enumerate(feet)])
        arm_step=np.clip(self.arm_goal-self.arm_q,-np.deg2rad(20)*dt,np.deg2rad(20)*dt)
        next_arm=self.arm_q+arm_step
        target=self.mapper.encode(np.r_[leg_q,next_arm])
        limit=self.cfg["servo"]["max_speed_deg_s"]*dt
        self.servo+=np.clip(target-self.servo,-limit,limit)
        self.arm_q=next_arm
        return self.servo.copy(),"active"
