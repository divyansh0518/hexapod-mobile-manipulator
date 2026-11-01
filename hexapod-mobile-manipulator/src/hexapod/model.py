"""Millimetres, radians, body frame +X forward, +Y left, +Z up."""
import json
from pathlib import Path
import numpy as np

def load_config(path="config/robot.json"):
    return json.loads(Path(path).read_text())

def finite(values):
    a = np.asarray(values, dtype=float)
    if not np.all(np.isfinite(a)):
        raise ValueError("Non-finite numeric input")
    return a

class Legs:
    def __init__(self, cfg):
        self.a, self.b, self.c = finite(cfg["links_mm"])
        self.mounts = finite(cfg["mounts_mm"])
        self.yaws = np.arctan2(self.mounts[:, 1], self.mounts[:, 0])
        self.home = np.column_stack((self.mounts[:,0]+cfg["home_radius_mm"]*np.cos(self.yaws),
                                    self.mounts[:,1]+cfg["home_radius_mm"]*np.sin(self.yaws),
                                    np.full(6, cfg["home_z_mm"])))

    def fk(self, leg, q):
        yaw, hip, knee = finite(q)
        yaw += self.yaws[leg]
        r = self.a + self.b*np.cos(hip) + self.c*np.cos(hip+knee)
        z = self.b*np.sin(hip) + self.c*np.sin(hip+knee)
        return np.r_[self.mounts[leg] + r*np.array([np.cos(yaw),np.sin(yaw)]),z]

    def ik(self, leg, target):
        x,y,z = finite(target) - np.r_[self.mounts[leg],0]
        r = np.hypot(x,y)-self.a
        d2 = r*r+z*z
        k = (d2-self.b*self.b-self.c*self.c)/(2*self.b*self.c)
        if abs(k)>1+1e-9 or r<0:
            raise ValueError("Unreachable leg target; command rejected")
        knee = -np.arccos(np.clip(k,-1,1))
        hip = np.arctan2(z,r)-np.arctan2(self.c*np.sin(knee),self.b+self.c*np.cos(knee))
        yaw = (np.arctan2(y,x)-self.yaws[leg]+np.pi)%(2*np.pi)-np.pi
        return np.array([yaw,hip,knee])

class ServoMap:
    def __init__(self, cfg):
        self.cfg=cfg
    def encode(self, q):
        q=finite(q)
        if q.shape!=(24,): raise ValueError("Expected 24 joint angles")
        out=np.array(self.cfg["offset_deg"])+np.array(self.cfg["sign"])*np.rad2deg(q)
        if np.any(out<self.cfg["min_deg"]) or np.any(out>self.cfg["max_deg"]):
            raise ValueError("Servo limit exceeded; recalibrate or reduce motion")
        return out
