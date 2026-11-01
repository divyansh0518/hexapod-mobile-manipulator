"""Six revolute axes with numerical position/orientation IK (assumed geometry)."""
import numpy as np
from .model import finite

def rotation(axis, a):
    v=np.eye(3)["xyz".index(axis)]
    x,y,z=v; K=np.array([[0,-z,y],[z,0,-x],[-y,x,0]])
    return np.eye(3)+np.sin(a)*K+(1-np.cos(a))*(K@K)

def rotation_error(target, actual):
    # SO(3) logarithm, including the neighbourhood of pi.
    R=target@actual.T
    theta=np.arccos(np.clip((np.trace(R)-1)/2,-1,1))
    if theta<1e-8: return np.zeros(3)
    if np.pi-theta<1e-5:
        values,vectors=np.linalg.eig(R)
        axis=np.real(vectors[:,np.argmin(abs(values-1))])
        return theta*axis/np.linalg.norm(axis)
    return theta/(2*np.sin(theta))*np.array([R[2,1]-R[1,2],R[0,2]-R[2,0],R[1,0]-R[0,1]])

class Arm:
    def __init__(self,cfg):
        self.cfg=cfg
        self.limits=np.deg2rad(cfg["limits_deg"])
        self.home=np.deg2rad(cfg["home_deg"])
    def fk(self,q):
        q=finite(q)
        if q.shape!=(6,): raise ValueError("Six arm joints required")
        T=np.eye(4);T[:3,3]=self.cfg["base_xyz_mm"]
        for axis,link,a in zip(self.cfg["axes"],self.cfg["links_mm"],q):
            A=np.eye(4);A[:3,:3]=rotation(axis,a); A[:3,3]=A[:3,:3]@np.array(link)
            T=T@A
        return T
    def ik(self,xyz,orientation=None,seed=None,iterations=300):
        xyz=finite(xyz)
        if xyz.shape!=(3,): raise ValueError("XYZ required")
        q=self.home.copy() if seed is None else finite(seed).copy()
        if q.shape!=(6,): raise ValueError("Six joint seed required")
        q=np.clip(q,*self.limits.T)
        if orientation is not None:
            orientation=finite(orientation)
            if orientation.shape!=(3,3) or not np.allclose(orientation.T@orientation,np.eye(3),atol=1e-5) or np.linalg.det(orientation)<.99:
                raise ValueError("Invalid rotation matrix")
        weight=70.0
        for _ in range(iterations):
            T=self.fk(q); error=xyz-T[:3,3]
            if orientation is not None:
                ori=rotation_error(orientation,T[:3,:3]);error=np.r_[error,weight*ori]
            if np.linalg.norm(error[:3])<.5 and (orientation is None or np.linalg.norm(error[3:])/weight<.02):
                return q
            J=np.zeros((len(error),6));eps=1e-5
            for j in range(6):
                dq=q.copy();dq[j]+=eps;T2=self.fk(dq)
                J[:3,j]=(T2[:3,3]-T[:3,3])/eps
                if orientation is not None: J[3:,j]=weight*rotation_error(T2[:3,:3],T[:3,:3])/eps
            step=J.T@np.linalg.solve(J@J.T+4*np.eye(len(error)),error)
            q=np.clip(q+np.clip(step,-.12,.12),*self.limits.T)
        raise ValueError("Arm IK did not converge within limits")

def interpolate(start,goal,steps=100):
    """Quintic interpolation; controller additionally enforces servo speed limits."""
    for u in np.linspace(0,1,steps):
        s=10*u**3-15*u**4+6*u**5
        yield np.asarray(start)+(np.asarray(goal)-start)*s
