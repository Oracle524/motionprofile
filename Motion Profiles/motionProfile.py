# |profile|--------------------------------------------------------------------
import numpy as np

def profile(displacement: float, start: float, time: list[float], Ta: float) -> \
    tuple[list[float], list[float], list[float]]:

    d = []
    v = []
    a = []
    time = np.array(time)

    T = 2*Ta 
    Tm = max(time)
    Tb = Tm - 2*Ta
    am = displacement*np.pi**2 / (8*Ta**2+2*Ta*(Tm-Ta)*np.pi)
    Da = displacement/2 - (am*2*Ta*(Tm-2*Ta))/(2*np.pi)
    #am = ((np.pi**2)*2*Da)/(2* (T**2))
    #Da = (am*((2*Ta)**2))/(np.pi)**2

    for t in time: # loop to get all the motion data 
        if 0 <= t < Ta: # Accleration part 
            aa = am*np.cos((np.pi * t) / (2 * Ta))
            va = am*2*(Ta/np.pi)*np.sin((np.pi*t)/(2*Ta))
            da = Da - Da*np.cos((np.pi*t)/(2*Ta))

            a.append(aa)
            v.append(va)
            d.append(da)

        elif Ta <= t <= Tb + Ta: # Constant velocity part 
            ab = 0
            vb = am*((2*Ta)/np.pi)
            db = am*(((2*Ta)/np.pi)*t) - am*(((2*Ta)/np.pi)*Ta) + Da
            a.append(ab)
            v.append(vb)
            d.append(db)

        elif Ta + Tb <= t <= Tm:  # Deceleration part 
            ac = am*np.cos((np.pi*(t-Tb))/(2 *Ta))
            vc = am*((2*Ta)/np.pi)*np.sin((np.pi*(t-Tb))/(2*Ta))
            dc = -Da*np.cos((np.pi*(t-Tb))/(2*Ta)) + am * ((2*Ta)/np.pi)*Tb + Da

            a.append(ac)
            v.append(vc)
            d.append(dc)

        else:
            a.append(0)
            v.append(0)
            d.append(0)


    return d,v,a

# |motion|---------------------------------------------------------------------
def motion(displacement: float, interval: float, accelLimit: float = 0, veloLimit: float = 0) -> \
    tuple[list[float], float]:
    # Given the acceleration limit and velocity limit,
    # Find the fastest time for the move.
    time = []
    Ta = 0 
    #am = ((np.pi**2)*displacement)/(2* (T**2))

    # fastest time is when there is no constant velocity time part 
    T = np.sqrt(((np.pi**2)*displacement))/(2 * accelLimit)
    Ta = T / 2
    Tm = 2 * Ta
    #time = 

    return time,Ta

# |jointInterpolation|---------------------------------------------------------
def jointInterpolation(displacementA: float, startA: float,
                       displacementB: float, startB: float, interval: float, 
                       accelLimitA:float = 0, veloLimitA:float = 0, 
                       accelLimitB: float = 0, veloLimitB:float =0) -> \
                       tuple[tuple[list[float], list[float], list[float]], 
                                tuple[list[float], list[float], list[float]], 
                                list[float]]:
    # Given the acceleration limit and velocity limits for two joints,
    # Find the fastest time for the move and
    # Coordinate the joints to move together.   
    eomA = profile(0, 0, [0], 0)
    eomB = profile(0, 0, [0], 0)
    time = []

    return eomA, eomB, time