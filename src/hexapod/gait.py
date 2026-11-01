"""Phase-driven insect-inspired gaits; open-loop flat-ground trajectories."""
import numpy as np
from .model import finite
# Index order RF RM RR LR LM LF. Swing windows start at these phases.
GAITS = {
    "tripod": (0.5, np.array([0,.5,0,.5,0,.5])),
    "ripple": (2/3, np.array([0,1/3,2/3,0,1/3,2/3])),
    "wave": (5/6, np.array([0,1/6,2/6,3/6,4/6,5/6])),
}
class Gait:
    def __init__(self, legs, cfg):
        self.legs,self.cfg=legs,cfg
    def targets(self, time_s, command=(0,0,0), name="tripod"):
        vx,vy,w=finite(command)
        if max(abs(vx),abs(vy),abs(w))>1: raise ValueError("Commands must be normalized")
        if not np.isfinite(time_s): raise ValueError("Invalid time")
        duty,offsets=GAITS[name]
        points=self.legs.home.copy()
        if np.linalg.norm(command)<1e-9: return points,np.ones(6,dtype=bool)
        phase=(time_s/self.cfg["period_s"]-offsets)%1
        stance=phase+1e-12>=1-duty
        for i,p in enumerate(phase):
            if not stance[i]:
                u=p/(1-duty)
                # Smoothstep gives zero planar velocity at lift-off and touchdown.
                s=3*u*u-2*u*u*u
                travel=s-.5
                points[i,2]+=self.cfg["lift_mm"]*np.sin(np.pi*u)**2
            else:
                u=(p-(1-duty))/duty
                travel=.5-u
            angle=w*self.cfg["yaw_rad"]*travel
            c,s=np.cos(angle),np.sin(angle)
            points[i,:2]=np.array([[c,-s],[s,c]])@points[i,:2]
            points[i,:2]+=np.array([vx,vy])*self.cfg["stride_mm"]*travel
        return points,stance

def support_margin(feet, stance, com_xy=(0,0)):
    """Signed distance to convex support polygon; no contact/force model."""
    pts=sorted(set(map(tuple,np.asarray(feet)[stance,:2])))
    if len(pts)<3: return float("-inf")
    def cross(o,a,b):
        u,v=np.array(a)-o,np.array(b)-o
        return u[0]*v[1]-u[1]*v[0]
    lower=[];upper=[]
    for p in pts:
        while len(lower)>=2 and cross(lower[-2],lower[-1],p)<=0: lower.pop()
        lower.append(p)
    for p in reversed(pts):
        while len(upper)>=2 and cross(upper[-2],upper[-1],p)<=0: upper.pop()
        upper.append(p)
    hull=lower[:-1]+upper[:-1]
    margins=[]
    for a,b in zip(hull,hull[1:]+hull[:1]):
        edge=np.array(b)-a; rel=np.array(com_xy)-a
        margins.append(float((edge[0]*rel[1]-edge[1]*rel[0])/np.linalg.norm(edge)))
    return min(margins)
